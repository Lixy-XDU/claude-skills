#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""校验 layout_plan.json 是否符合模板槽位约束。"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


def text_len(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, str):
        return len(value.strip())
    if isinstance(value, list):
        return sum(text_len(v) for v in value)
    if isinstance(value, dict):
        return sum(text_len(v) for v in value.values())
    return len(str(value))


def has_forbidden_coord(obj: Any) -> bool:
    if isinstance(obj, dict):
        keys = set(obj.keys())
        if {"x", "y", "w", "h"}.issubset(keys) or "bbox" in keys:
            return True
        return any(has_forbidden_coord(v) for v in obj.values())
    if isinstance(obj, list):
        return any(has_forbidden_coord(v) for v in obj)
    return False


# ── LaTeX 公式检测 ──────────────────────────────────────────────────

LATEX_PATTERNS = [
    r"\$\$.+?\$\$",          # $$...$$ display math
    r"\$[^$]+?\$",           # $...$ inline math
    r"\\\(",                 # \( display math opener
    r"\\\)",                 # \) display math closer
    r"\\\[",                 # \[ display math opener
    r"\\\]",                 # \] display math closer
    r"\\frac\b",             # \frac
    r"\\sum\b",              # \sum
    r"\\int\b",              # \int
    r"\\prod\b",             # \prod
    r"\\lambda\b",           # \lambda
    r"\\theta\b",            # \theta
    r"\\alpha\b",            # \alpha
    r"\\beta\b",             # \beta
    r"\\gamma\b",            # \gamma
    r"\\delta\b",            # \delta
    r"\\epsilon\b",          # \epsilon
    r"\\mu\b",               # \mu
    r"\\sigma\b",            # \sigma
    r"\\omega\b",            # \omega
    r"\\partial\b",          # \partial
    r"\\nabla\b",            # \nabla
    r"\\infty\b",            # \infty
    r"\\sqrt\b",             # \sqrt
    r"\\begin\{",            # \begin{...} environments
    r"\\end\{",              # \end{...} environments
    r"_\{",                  # _{...} subscript
    r"\^\{",                 # ^{...} superscript
]

LATEX_REGEX = re.compile("|".join(LATEX_PATTERNS))


def _extract_text_from_slot(value: Any) -> list[str]:
    """递归提取槽位中所有文本内容，排除 latex 字段。"""
    texts: list[str] = []
    if isinstance(value, str):
        texts.append(value)
    elif isinstance(value, list):
        for item in value:
            texts.extend(_extract_text_from_slot(item))
    elif isinstance(value, dict):
        for k, v in value.items():
            if k == "latex":
                continue
            texts.extend(_extract_text_from_slot(v))
    return texts


def validate(plan: dict, layout_def: dict) -> dict:
    layouts = layout_def.get("layouts", {})
    issues = []
    warnings = []

    slides = plan.get("slides", [])
    if not slides:
        issues.append({"type": "NO_SLIDES", "message": "layout_plan.json 中没有 slides。"})

    for idx, slide in enumerate(slides, start=1):
        slide_no = slide.get("slide_no", idx)
        layout_name = slide.get("layout")
        if layout_name not in layouts:
            issues.append({"slide_no": slide_no, "type": "UNKNOWN_LAYOUT", "message": f"未知 layout：{layout_name}"})
            continue
        spec = layouts[layout_name]
        allowed_slots = set(spec.get("slots", {}).keys())
        slots = slide.get("slots", {})
        if not isinstance(slots, dict):
            issues.append({"slide_no": slide_no, "type": "SLOTS_NOT_OBJECT", "message": "slots 必须是 object。"})
            continue

        if has_forbidden_coord(slots):
            issues.append({"slide_no": slide_no, "type": "FORBIDDEN_COORDINATES", "message": "slots 中不允许出现 x/y/w/h/bbox。"})

        for name in slots:
            # 支持 one_column 的 title/body 等槽位，以及用 title 字段填槽位
            if name not in allowed_slots:
                issues.append({"slide_no": slide_no, "type": "UNKNOWN_SLOT", "slot": name, "message": f"layout {layout_name} 不存在 slot：{name}"})

        # 检查 slot 长度
        for name, slot_spec in spec.get("slots", {}).items():
            if name not in slots:
                continue
            value = slots.get(name)
            max_chars = slot_spec.get("max_chars")
            if max_chars and text_len(value) > max_chars:
                warnings.append({"slide_no": slide_no, "type": "TEXT_MAY_OVERFLOW", "slot": name, "message": f"{name} 内容长度 {text_len(value)} 超过建议 {max_chars}。"})
            max_items = slot_spec.get("max_items")
            if max_items and isinstance(value, list) and len(value) > max_items:
                issues.append({"slide_no": slide_no, "type": "TOO_MANY_ITEMS", "slot": name, "message": f"{name} 最多 {max_items} 项，当前 {len(value)} 项。"})
            if max_items and isinstance(value, dict) and isinstance(value.get("items"), list) and len(value["items"]) > max_items:
                warnings.append({"slide_no": slide_no, "type": "TOO_MANY_ITEMS", "slot": name, "message": f"{name}.items 建议不超过 {max_items} 项。"})

        # ── 公式专用校验 ─────────────────────────────────────────

        for name, slot_spec in spec.get("slots", {}).items():
            value = slots.get(name)
            if value is None:
                continue

            # CHECK: 公式槽位必须有 latex 或 image_path
            if slot_spec.get("kind") == "formula":
                if isinstance(value, dict):
                    if not value.get("latex") and not value.get("image_path"):
                        issues.append({
                            "slide_no": slide_no,
                            "type": "FORMULA_MISSING_LATEX",
                            "severity": "high",
                            "slot": name,
                            "message": f"公式槽位 '{name}' 没有 'latex' 也没有 'image_path' 字段。",
                        })
                    fb = str(value.get("fallback", "fail_then_report")).strip()
                    if fb not in ("image", "fail_then_report"):
                        warnings.append({
                            "slide_no": slide_no,
                            "type": "INVALID_FALLBACK",
                            "slot": name,
                            "message": f"公式槽位 '{name}' 的 fallback 值 '{fb}' 无效，应为 'image' 或 'fail_then_report'。",
                        })
                    # CHECK: 公式过长
                    latex_str = str(value.get("latex", ""))
                    if len(latex_str) > 120:
                        warnings.append({
                            "slide_no": slide_no,
                            "type": "FORMULA_TOO_LONG",
                            "slot": name,
                            "message": f"公式槽位 '{name}' 的 LaTeX 长度 {len(latex_str)} 超过建议上限 120，建议拆分为多页。当前前 80 字符：{latex_str[:80]}...",
                        })

            # CHECK: text / bullets / caption / inline_meta 槽位中不应出现 LaTeX
            if slot_spec.get("kind") in ("text", "bullets", "caption", "inline_meta"):
                all_texts = _extract_text_from_slot(value)
                found_in = None
                for text in all_texts:
                    if LATEX_REGEX.search(text):
                        found_in = text
                        break
                if found_in is not None:
                    issues.append({
                        "slide_no": slide_no,
                        "type": "FORMULA_IN_TEXT_SLOT",
                        "severity": "high",
                        "slot": name,
                        "message": f"在 {slot_spec.get('kind')} 类型槽位 '{name}' 中检测到 LaTeX 公式模式。公式必须放入 kind='formula' 的槽位。匹配片段：{found_in[:80]}",
                    })

            # CHECK: mixed_box 中不应出现 latex 字段
            if slot_spec.get("kind") == "mixed_box":
                if isinstance(value, dict) and value.get("latex"):
                    issues.append({
                        "slide_no": slide_no,
                        "type": "FORMULA_IN_TEXT_SLOT",
                        "severity": "high",
                        "slot": name,
                        "message": f"在 mixed_box 槽位 '{name}' 中发现 'latex' 字段。公式必须放入 kind='formula' 的槽位。",
                    })

        if layout_name not in {"title", "agenda", "section", "closing"} and not slide.get("evidence_refs"):
            warnings.append({"slide_no": slide_no, "type": "MISSING_EVIDENCE_REFS", "message": "非装饰页建议保留 evidence_refs。"})

    return {
        "status": "pass" if not issues else "fail",
        "issues": issues,
        "warnings": warnings,
        "issue_count": len(issues),
        "warning_count": len(warnings)
    }


def main() -> int:
    if len(sys.argv) != 4:
        print("Usage: validate_layout.py <layout_plan.json> <template_layouts.json> <output_report.json>")
        return 2
    plan_path = Path(sys.argv[1])
    layout_path = Path(sys.argv[2])
    output_path = Path(sys.argv[3])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    layout_def = json.loads(layout_path.read_text(encoding="utf-8"))
    report = validate(plan, layout_def)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
