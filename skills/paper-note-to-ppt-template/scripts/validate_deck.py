#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""最终 PPT 轻量检查。"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 4:
        print("Usage: validate_deck.py <deck.pptx> <layout_plan.json> <final_report.md>")
        return 2

    deck_path = Path(sys.argv[1])
    plan_path = Path(sys.argv[2])
    report_path = Path(sys.argv[3])
    report_path.parent.mkdir(parents=True, exist_ok=True)

    warnings = []
    errors = []

    if not deck_path.exists():
        errors.append(f"PPT 不存在：{deck_path}")
        slide_count = 0
    else:
        try:
            from pptx import Presentation
            prs = Presentation(str(deck_path))
            slide_count = len(prs.slides)
        except Exception as exc:
            errors.append(f"无法读取 PPT：{exc}")
            slide_count = -1

    plan = {}
    if plan_path.exists():
        try:
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"无法读取 layout_plan：{exc}")
    else:
        warnings.append(f"layout_plan 不存在：{plan_path}")

    # 读取公式渲染报告（在 layout_plan 目录或 deck.pptx 目录下查找）
    formula_report = {}
    for candidate_dir in [plan_path.parent, deck_path.parent]:
        formula_report_path = candidate_dir / "formula_report.json"
        if formula_report_path.exists():
            try:
                formula_report = json.loads(formula_report_path.read_text(encoding="utf-8"))
                break
            except Exception:
                pass

    planned = len(plan.get("slides", [])) if plan else 0
    if slide_count >= 0 and planned and slide_count != planned:
        warnings.append(f"PPT 页数 {slide_count} 与 layout_plan 页数 {planned} 不一致。")

    missing_refs = []
    for s in plan.get("slides", []):
        if s.get("layout") not in {"title", "agenda", "section", "closing"} and not s.get("evidence_refs"):
            missing_refs.append(str(s.get("slide_no", "?")))
    if missing_refs:
        warnings.append("以下页面缺少 evidence_refs：" + ", ".join(missing_refs))

    lines = [
        "# Final Report",
        "",
        f"- PPT: `{deck_path}`",
        f"- Layout Plan: `{plan_path}`",
        f"- Planned slides: {planned}",
        f"- PPT slides: {slide_count}",
        f"- Status: {'fail' if errors else 'pass'}",
        "",
        "## Errors",
    ]
    lines += [f"- {e}" for e in errors] or ["- 无"]
    lines += ["", "## Warnings"]
    lines += [f"- {w}" for w in warnings] or ["- 无"]

    # ── 公式渲染报告 ─────────────────────────────────────────
    lines += ["", "## Formula Rendering"]
    formula_results = formula_report.get("formula_results", [])
    if formula_results:
        ok_count = sum(1 for r in formula_results if r["status"] == "ok")
        img_count = sum(1 for r in formula_results if r["status"] == "fallback_image")
        imgpath_count = sum(1 for r in formula_results if r["status"] == "image_path")
        failed = [r for r in formula_results if r["status"] == "failed"]
        skipped = [r for r in formula_results if r["status"] == "skipped_in_mixed_box"]

        lines.append(f"- Total formulas: {len(formula_results)}")
        lines.append(f"- Native OMML: {ok_count}")
        lines.append(f"- Image fallback: {img_count}")
        lines.append(f"- Pre-rendered image: {imgpath_count}")
        lines.append(f"- Failed: {len(failed)}")
        lines.append(f"- Skipped (in mixed_box): {len(skipped)}")

        if failed:
            lines.append("")
            lines.append("### Formula Rendering Failures")
            for r in failed:
                lines.append(f"- Slide {r['slide_no']}, slot `{r['slot']}`: {r['message']}")
                lines.append(f"  LaTeX: `{r.get('latex', '')[:100]}`")

        if skipped:
            lines.append("")
            lines.append("### Formulas Skipped (not in formula slots)")
            for r in skipped:
                lines.append(f"- Slide {r['slide_no']}, slot `{r['slot']}`: {r['message']}")
                lines.append(f"  LaTeX: `{r.get('latex', '')[:100]}`")
    else:
        lines.append("- No formulas in deck.")

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(report_path)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
