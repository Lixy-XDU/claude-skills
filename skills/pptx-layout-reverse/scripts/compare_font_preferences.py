#!/usr/bin/env python3
"""对比新鲜渲染版和用户编辑版的 PPTX 原始 shape dump，推断字体偏好。"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple


def localize_argparse() -> None:
    """将 argparse 自动生成的帮助/错误文案改为中文。"""
    translations = {
        "usage: ": "用法：",
        "positional arguments": "位置参数",
        "options": "选项",
        "optional arguments": "可选参数",
        "show this help message and exit": "显示此帮助信息并退出",
        "the following arguments are required: %s": "缺少必填参数：%s",
        "unrecognized arguments: %s": "无法识别的参数：%s",
        "invalid choice: %(value)r (choose from %(choices)s)": "无效选择：%(value)r（可选：%(choices)s）",
        "argument %(argument_name)s: %(message)s": "参数 %(argument_name)s：%(message)s",
        "%(prog)s: error: %(message)s\n": "%(prog)s：错误：%(message)s\n",
        "expected one argument": "需要一个参数",
        "not allowed with argument %s": "不能与参数 %s 同时使用",
        "ignored explicit argument %r": "忽略显式参数 %r",
    }
    argparse._ = lambda text: translations.get(text, text)  # type: ignore[attr-defined]




def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def center(shape: Mapping[str, Any]) -> Optional[Tuple[float, float]]:
    c = shape.get("center")
    if isinstance(c, list) and len(c) == 2 and all(isinstance(v, (int, float)) for v in c):
        return float(c[0]), float(c[1])
    bbox = shape.get("bbox")
    if isinstance(bbox, list) and len(bbox) == 4 and all(isinstance(v, (int, float)) for v in bbox):
        return float(bbox[0]) + float(bbox[2]) / 2, float(bbox[1]) + float(bbox[3]) / 2
    return None


def dist(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def text_shapes(raw: Mapping[str, Any], slide_index: int) -> List[Mapping[str, Any]]:
    for slide in raw.get("slides", []):
        if isinstance(slide, dict) and int(slide.get("slide_index", -1)) == slide_index:
            return [
                s
                for s in slide.get("shapes", [])
                if isinstance(s, dict) and s.get("has_text_frame") and center(s) is not None
            ]
    return []


def all_slide_indexes(*raws: Mapping[str, Any]) -> List[int]:
    indexes = set()
    for raw in raws:
        for slide in raw.get("slides", []):
            if isinstance(slide, dict):
                indexes.add(int(slide.get("slide_index", 0)))
    return sorted(indexes)


def values_mode(values: List[Any]) -> Any:
    values = [v for v in values if v is not None]
    if not values:
        return None
    try:
        return statistics.mode(values)
    except statistics.StatisticsError:
        return values[0]


def font_candidates(shape: Mapping[str, Any]) -> Dict[str, Any]:
    tf = shape.get("text_frame")
    if not isinstance(tf, dict):
        return {}

    run_sizes: List[float] = []
    paragraph_sizes: List[float] = []
    names: List[str] = []
    bolds: List[bool] = []
    italics: List[bool] = []

    for p in tf.get("paragraphs", []):
        if not isinstance(p, dict):
            continue
        pfont = p.get("font", {}) if isinstance(p.get("font"), dict) else {}
        if isinstance(pfont.get("size_pt"), (int, float)):
            paragraph_sizes.append(float(pfont["size_pt"]))
        if isinstance(pfont.get("name"), str):
            names.append(pfont["name"])
        if isinstance(pfont.get("bold"), bool):
            bolds.append(pfont["bold"])
        if isinstance(pfont.get("italic"), bool):
            italics.append(pfont["italic"])

        for r in p.get("runs", []):
            if not isinstance(r, dict):
                continue
            rfont = r.get("font", {}) if isinstance(r.get("font"), dict) else {}
            if isinstance(rfont.get("size_pt"), (int, float)):
                run_sizes.append(float(rfont["size_pt"]))
            if isinstance(rfont.get("name"), str):
                names.append(rfont["name"])
            if isinstance(rfont.get("bold"), bool):
                bolds.append(rfont["bold"])
            if isinstance(rfont.get("italic"), bool):
                italics.append(rfont["italic"])

    effective_size = values_mode(run_sizes) if run_sizes else values_mode(paragraph_sizes)
    source = "run" if run_sizes else ("paragraph" if paragraph_sizes else "missing")
    return {
        "effective_size_pt": effective_size,
        "size_source": source,
        "run_size_pt": values_mode(run_sizes),
        "paragraph_size_pt": values_mode(paragraph_sizes),
        "font_name": values_mode(names),
        "bold": values_mode(bolds),
        "italic": values_mode(italics),
        "has_run_size": bool(run_sizes),
    }


def text_preview(shape: Mapping[str, Any], limit: int = 100) -> str:
    tf = shape.get("text_frame")
    text = ""
    if isinstance(tf, dict):
        text = str(tf.get("text", ""))
    return " ".join(text.split())[:limit]


def match_shapes(
    fresh_shapes: List[Mapping[str, Any]],
    edited_shapes: List[Mapping[str, Any]],
    threshold_in: float,
) -> List[Tuple[Mapping[str, Any], Mapping[str, Any], float]]:
    matches: List[Tuple[Mapping[str, Any], Mapping[str, Any], float]] = []
    used_edited: set[int] = set()

    for fresh in fresh_shapes:
        fc = center(fresh)
        if fc is None:
            continue
        best_idx: Optional[int] = None
        best_dist: Optional[float] = None
        for idx, edited in enumerate(edited_shapes):
            if idx in used_edited:
                continue
            ec = center(edited)
            if ec is None:
                continue
            d = dist(fc, ec)
            if best_dist is None or d < best_dist:
                best_idx = idx
                best_dist = d
        if best_idx is not None and best_dist is not None and best_dist <= threshold_in:
            used_edited.add(best_idx)
            matches.append((fresh, edited_shapes[best_idx], best_dist))

    return matches


def changed(a: Any, b: Any) -> bool:
    if a is None or b is None:
        return False
    return a != b


def compare(fresh: Mapping[str, Any], edited: Mapping[str, Any], threshold_in: float) -> Dict[str, Any]:
    comparisons: List[Dict[str, Any]] = []
    aggregate: Dict[str, Dict[str, Any]] = {
        "size_changes": {"samples": 0, "deltas_pt": []},
        "run_size_became_inherited": {"samples": 0},
        "font_name_changes": {"samples": 0},
        "bold_changes": {"samples": 0},
    }

    for slide_index in all_slide_indexes(fresh, edited):
        matches = match_shapes(text_shapes(fresh, slide_index), text_shapes(edited, slide_index), threshold_in)
        for fresh_shape, edited_shape, d in matches:
            ff = font_candidates(fresh_shape)
            ef = font_candidates(edited_shape)
            fresh_size = ff.get("effective_size_pt")
            edited_size = ef.get("effective_size_pt")
            size_delta = None
            if isinstance(fresh_size, (int, float)) and isinstance(edited_size, (int, float)):
                size_delta = round(float(edited_size) - float(fresh_size), 3)
                if abs(size_delta) > 0.01:
                    aggregate["size_changes"]["samples"] += 1
                    aggregate["size_changes"]["deltas_pt"].append(size_delta)

            if ff.get("has_run_size") and not ef.get("has_run_size"):
                aggregate["run_size_became_inherited"]["samples"] += 1
            if changed(ff.get("font_name"), ef.get("font_name")):
                aggregate["font_name_changes"]["samples"] += 1
            if changed(ff.get("bold"), ef.get("bold")):
                aggregate["bold_changes"]["samples"] += 1

            comparisons.append(
                {
                    "slide_index": slide_index,
                    "distance_in": round(d, 4),
                    "fresh_shape_id": fresh_shape.get("shape_id"),
                    "edited_shape_id": edited_shape.get("shape_id"),
                    "text_preview": text_preview(edited_shape) or text_preview(fresh_shape),
                    "fresh_font": ff,
                    "edited_font": ef,
                    "size_delta_pt": size_delta,
                    "run_size_became_inherited": bool(ff.get("has_run_size") and not ef.get("has_run_size")),
                }
            )

    deltas = aggregate["size_changes"]["deltas_pt"]
    if deltas:
        aggregate["size_changes"]["avg_delta_pt"] = round(sum(deltas) / len(deltas), 3)
        aggregate["size_changes"]["median_delta_pt"] = round(statistics.median(deltas), 3)
    else:
        aggregate["size_changes"]["avg_delta_pt"] = None
        aggregate["size_changes"]["median_delta_pt"] = None

    return {
        "metadata": {
            "fresh_source_pptx": fresh.get("source_pptx"),
            "edited_source_pptx": edited.get("source_pptx"),
            "match_threshold_in": threshold_in,
        },
        "summary": {
            "matched_text_shapes": len(comparisons),
            "size_change_samples": aggregate["size_changes"]["samples"],
            "run_size_became_inherited_samples": aggregate["run_size_became_inherited"]["samples"],
            "font_name_change_samples": aggregate["font_name_changes"]["samples"],
            "bold_change_samples": aggregate["bold_changes"]["samples"],
        },
        "aggregate": aggregate,
        "comparisons": comparisons,
    }


def main(argv: Optional[List[str]] = None) -> int:
    localize_argparse()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fresh", type=Path, required=True, help="新鲜渲染版 PPTX 提取出的原始 JSON")
    parser.add_argument("--edited", type=Path, required=True, help="用户编辑版 PPTX 提取出的原始 JSON")
    parser.add_argument("--match-threshold", type=float, default=0.5, help="中心点匹配的最大距离，单位 inch")
    parser.add_argument("--output", "-o", type=Path, default=Path("font_preferences.recovered.json"), help="输出字体偏好分析 JSON 的路径")
    args = parser.parse_args(argv)

    result = compare(read_json(args.fresh), read_json(args.edited), args.match_threshold)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"已写入 {args.output} —— 匹配 {result['summary']['matched_text_shapes']} 个文本 shape；"
        f"字号变化样本 {result['summary']['size_change_samples']} 个；"
        f"run 级字号转为继承的样本 {result['summary']['run_size_became_inherited_samples']} 个",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
