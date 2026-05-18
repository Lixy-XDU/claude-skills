#!/usr/bin/env python3
"""将提取出的 PPTX shape 匹配到模板 slot，并计算 bbox delta。"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Tuple


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



BBox = List[float]


LAYOUT_KEYS = ("layout_name", "layout", "layout_id", "template", "template_name")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def round_list(values: Iterable[float], digits: int = 4) -> List[float]:
    return [round(float(v), digits) for v in values]


def bbox_center(bbox: BBox) -> Tuple[float, float]:
    return (bbox[0] + bbox[2] / 2, bbox[1] + bbox[3] / 2)


def distance(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def valid_bbox(bbox: Any) -> bool:
    return isinstance(bbox, list) and len(bbox) == 4 and all(isinstance(x, (int, float)) for x in bbox)


def normalize_layouts(layouts_obj: Any) -> Dict[str, Any]:
    """兼容常见 layout JSON 外层结构，并返回 {layout_name: layout_spec}。"""
    if not isinstance(layouts_obj, dict):
        raise ValueError("layout JSON 必须是一个对象")
    for key in ("layouts", "template_layouts", "slides", "slide_layouts"):
        if key in layouts_obj and isinstance(layouts_obj[key], dict):
            return layouts_obj[key]
    return layouts_obj


def slot_items(layout_spec: Mapping[str, Any]) -> Iterable[Tuple[str, Mapping[str, Any]]]:
    slots = layout_spec.get("slots", layout_spec)
    if not isinstance(slots, dict):
        return []
    return [(name, spec) for name, spec in slots.items() if isinstance(spec, dict) and valid_bbox(spec.get("bbox"))]


def shape_center(shape: Mapping[str, Any]) -> Optional[Tuple[float, float]]:
    center = shape.get("center")
    if isinstance(center, list) and len(center) == 2 and all(isinstance(v, (int, float)) for v in center):
        return float(center[0]), float(center[1])
    bbox = shape.get("bbox")
    if valid_bbox(bbox):
        return bbox_center([float(x) for x in bbox])
    return None


def shape_bbox(shape: Mapping[str, Any]) -> Optional[BBox]:
    bbox = shape.get("bbox")
    if valid_bbox(bbox):
        return [float(x) for x in bbox]
    return None


def match_slot(
    shape_cx: float,
    shape_cy: float,
    layout_name: str,
    all_layouts: Mapping[str, Any],
    threshold_in: float,
) -> Optional[Tuple[str, Mapping[str, Any], float]]:
    layout = all_layouts.get(layout_name)
    if not isinstance(layout, dict):
        return None

    best: Optional[Tuple[str, Mapping[str, Any], float]] = None
    for slot_name, spec in slot_items(layout):
        bc = bbox_center([float(x) for x in spec["bbox"]])
        d = distance((shape_cx, shape_cy), bc)
        if best is None or d < best[2]:
            best = (slot_name, spec, d)

    if best and best[2] <= threshold_in:
        return best
    return None


def load_layout_map(path: Optional[Path]) -> Dict[int, str]:
    if not path:
        return {}
    obj = read_json(path)
    mapping: Dict[int, str] = {}

    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and str(k).isdigit():
                mapping[int(k)] = v
            elif isinstance(v, dict):
                layout = first_layout_name(v)
                if layout and str(k).isdigit():
                    mapping[int(k)] = layout
    elif isinstance(obj, list):
        for idx, value in enumerate(obj):
            if isinstance(value, str):
                mapping[idx] = value
            elif isinstance(value, dict):
                layout = first_layout_name(value)
                slide_index = value.get("slide_index", value.get("index", idx))
                if layout is not None:
                    mapping[int(slide_index)] = layout
    return mapping


def first_layout_name(obj: Mapping[str, Any]) -> Optional[str]:
    for key in LAYOUT_KEYS:
        val = obj.get(key)
        if isinstance(val, str):
            return val
    return None


def load_layout_plan(path: Optional[Path]) -> Dict[int, str]:
    if not path:
        return {}
    obj = read_json(path)
    mapping: Dict[int, str] = {}

    if isinstance(obj, dict):
        if "slides" in obj and isinstance(obj["slides"], list):
            for idx, slide in enumerate(obj["slides"]):
                if isinstance(slide, dict):
                    layout = first_layout_name(slide)
                    slide_index = slide.get("slide_index", slide.get("index", idx))
                    if layout:
                        mapping[int(slide_index)] = layout
        else:
            # 兼容普通映射：{"0": {"layout_name": "..."}} 或 {"0": "..."}。
            mapping.update(load_layout_map(path))
    elif isinstance(obj, list):
        for idx, slide in enumerate(obj):
            if isinstance(slide, dict):
                layout = first_layout_name(slide)
                slide_index = slide.get("slide_index", slide.get("index", idx))
                if layout:
                    mapping[int(slide_index)] = layout
    return mapping


def text_shapes(slide: Mapping[str, Any]) -> List[Mapping[str, Any]]:
    result: List[Mapping[str, Any]] = []
    for shape in slide.get("shapes", []):
        if not isinstance(shape, dict):
            continue
        if shape.get("has_text_frame") and shape_bbox(shape) is not None and shape_center(shape) is not None:
            result.append(shape)
    return result


def infer_layout_for_slide(slide: Mapping[str, Any], layouts: Mapping[str, Any]) -> Tuple[Optional[str], Optional[float]]:
    shapes = text_shapes(slide)
    if not shapes:
        return None, None

    best_name: Optional[str] = None
    best_score: Optional[float] = None

    for layout_name, layout_spec in layouts.items():
        if not isinstance(layout_spec, dict):
            continue
        slots = list(slot_items(layout_spec))
        if not slots:
            continue
        dists: List[float] = []
        for shape in shapes:
            sc = shape_center(shape)
            if sc is None:
                continue
            nearest = min(distance(sc, bbox_center([float(x) for x in spec["bbox"]])) for _, spec in slots)
            dists.append(nearest)
        if dists:
            # 使用最近 N 个距离的平均值，降低额外文本框造成的惩罚。
            dists.sort()
            n = min(len(dists), max(1, len(slots)))
            score = sum(dists[:n]) / n
            if best_score is None or score < best_score:
                best_score = score
                best_name = layout_name

    return best_name, round(best_score, 4) if best_score is not None else None


def confidence_from_distance(distance_in: float, threshold_in: float) -> str:
    if distance_in <= 0.15:
        return "high"
    if distance_in <= min(0.75, threshold_in / 3):
        return "medium"
    return "low"


def shape_text_preview(shape: Mapping[str, Any], limit: int = 120) -> str:
    tf = shape.get("text_frame")
    text = ""
    if isinstance(tf, dict):
        text = str(tf.get("text", ""))
    text = " ".join(text.split())
    return text[:limit]


def is_formula_candidate(shape: Mapping[str, Any], slot_name: str) -> bool:
    tf = shape.get("text_frame")
    has_runs = False
    if isinstance(tf, dict):
        has_runs = bool(tf.get("has_runs"))
    return bool(shape.get("has_text_frame")) and not has_runs and slot_name == "formula"


def summarize_font(shape: Mapping[str, Any]) -> Dict[str, Any]:
    tf = shape.get("text_frame")
    if not isinstance(tf, dict):
        return {}
    run_sizes: List[float] = []
    paragraph_sizes: List[float] = []
    names: List[str] = []
    bold_values: List[bool] = []

    for p in tf.get("paragraphs", []):
        if not isinstance(p, dict):
            continue
        p_font = p.get("font", {}) if isinstance(p.get("font"), dict) else {}
        if isinstance(p_font.get("size_pt"), (int, float)):
            paragraph_sizes.append(float(p_font["size_pt"]))
        if isinstance(p_font.get("name"), str):
            names.append(p_font["name"])
        if isinstance(p_font.get("bold"), bool):
            bold_values.append(p_font["bold"])
        for r in p.get("runs", []):
            if not isinstance(r, dict):
                continue
            r_font = r.get("font", {}) if isinstance(r.get("font"), dict) else {}
            if isinstance(r_font.get("size_pt"), (int, float)):
                run_sizes.append(float(r_font["size_pt"]))
            if isinstance(r_font.get("name"), str):
                names.append(r_font["name"])
            if isinstance(r_font.get("bold"), bool):
                bold_values.append(r_font["bold"])

    def mode_or_none(values: List[Any]) -> Any:
        if not values:
            return None
        try:
            return statistics.mode(values)
        except statistics.StatisticsError:
            return values[0]

    return {
        "run_size_pt": mode_or_none(run_sizes),
        "paragraph_size_pt": mode_or_none(paragraph_sizes),
        "effective_size_pt": mode_or_none(run_sizes) if run_sizes else mode_or_none(paragraph_sizes),
        "font_name": mode_or_none(names),
        "bold": mode_or_none(bold_values),
        "run_size_missing": not bool(run_sizes),
    }


def aggregate_matches(slides: List[Dict[str, Any]]) -> Dict[str, Dict[str, Dict[str, Any]]]:
    bucket: MutableMapping[str, MutableMapping[str, List[List[float]]]] = defaultdict(lambda: defaultdict(list))
    for slide in slides:
        layout_name = slide.get("layout_name")
        if not isinstance(layout_name, str):
            continue
        for match in slide.get("matches", []):
            if not isinstance(match, dict):
                continue
            slot = match.get("slot")
            delta = match.get("delta")
            if isinstance(slot, str) and valid_bbox(delta):
                bucket[layout_name][slot].append([float(x) for x in delta])

    result: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for layout_name, slots in bucket.items():
        result[layout_name] = {}
        for slot, deltas in slots.items():
            transposed = list(zip(*deltas))
            result[layout_name][slot] = {
                "samples": len(deltas),
                "avg_delta": round_list([sum(vals) / len(vals) for vals in transposed]),
                "median_delta": round_list([statistics.median(vals) for vals in transposed]),
                "max_abs_delta": round_list([max(abs(v) for v in vals) for vals in transposed]),
            }
    return result


def patch_suggestions(
    layouts: Mapping[str, Any], aggregate: Mapping[str, Mapping[str, Mapping[str, Any]]]
) -> Dict[str, Any]:
    suggestions: Dict[str, Any] = {}
    for layout_name, slots in aggregate.items():
        layout_spec = layouts.get(layout_name)
        if not isinstance(layout_spec, dict):
            continue
        suggestions.setdefault(layout_name, {"slots": {}})
        slots_spec = dict(slot_items(layout_spec))
        for slot, stats in slots.items():
            spec = slots_spec.get(slot)
            delta = stats.get("avg_delta") if isinstance(stats, dict) else None
            if spec and valid_bbox(spec.get("bbox")) and valid_bbox(delta):
                base = [float(x) for x in spec["bbox"]]
                new_bbox = round_list([base[i] + float(delta[i]) for i in range(4)])
                suggestions[layout_name]["slots"][slot] = {
                    "bbox": new_bbox,
                    "source": "来自编辑版 PPTX 的实际平均 delta",
                    "samples": stats.get("samples"),
                    "avg_delta": delta,
                }
    return suggestions


def recover(
    raw: Mapping[str, Any],
    layouts: Mapping[str, Any],
    layout_map: Mapping[int, str],
    threshold_in: float,
) -> Dict[str, Any]:
    slides_out: List[Dict[str, Any]] = []
    matched_count = 0
    unmatched_count = 0
    formula_candidates = 0
    shapes_considered = 0

    for slide in raw.get("slides", []):
        if not isinstance(slide, dict):
            continue
        slide_index = int(slide.get("slide_index", len(slides_out)))
        layout_name = layout_map.get(slide_index)
        inferred_layout = None
        inferred_score = None
        if not layout_name:
            inferred_layout, inferred_score = infer_layout_for_slide(slide, layouts)
            layout_name = inferred_layout

        matches: List[Dict[str, Any]] = []
        unmatched: List[Dict[str, Any]] = []

        for shape in text_shapes(slide):
            shapes_considered += 1
            sc = shape_center(shape)
            ab = shape_bbox(shape)
            if not sc or not ab or not layout_name:
                unmatched_count += 1
                unmatched.append(
                    {
                        "shape_id": shape.get("shape_id"),
                        "reason": "缺少 layout 名称或几何信息",
                        "actual_bbox": ab,
                        "text_preview": shape_text_preview(shape),
                    }
                )
                continue

            matched = match_slot(sc[0], sc[1], layout_name, layouts, threshold_in)
            if not matched:
                unmatched_count += 1
                unmatched.append(
                    {
                        "shape_id": shape.get("shape_id"),
                        "reason": f"{threshold_in} inch 范围内没有可匹配 slot",
                        "actual_bbox": round_list(ab),
                        "text_preview": shape_text_preview(shape),
                    }
                )
                continue

            slot_name, slot_spec, dist = matched
            template_bbox = [float(x) for x in slot_spec["bbox"]]
            delta = [ab[i] - template_bbox[i] for i in range(4)]
            formula = is_formula_candidate(shape, slot_name) or bool(shape.get("contains_omml_xml"))
            if formula:
                formula_candidates += 1
            matched_count += 1

            matches.append(
                {
                    "slot": slot_name,
                    "shape_id": shape.get("shape_id"),
                    "shape_name": shape.get("name"),
                    "confidence": confidence_from_distance(dist, threshold_in),
                    "distance_in": round(dist, 4),
                    "actual_bbox": round_list(ab),
                    "template_bbox": round_list(template_bbox),
                    "delta": round_list(delta),
                    "is_formula_candidate": formula,
                    "font_summary": summarize_font(shape),
                    "text_preview": shape_text_preview(shape),
                }
            )

        slides_out.append(
            {
                "slide_index": slide_index,
                "layout_name": layout_name,
                "layout_inferred": bool(inferred_layout),
                "layout_inference_score": inferred_score,
                "matches": matches,
                "unmatched_shapes": unmatched,
            }
        )

    aggregate = aggregate_matches(slides_out)
    return {
        "metadata": {
            "source_raw": raw.get("source_pptx") or raw.get("source_raw"),
            "match_threshold_in": threshold_in,
            "unit": {"geometry": "inch", "font_size": "pt"},
        },
        "summary": {
            "slides": len(slides_out),
            "shapes_considered": shapes_considered,
            "matched_shapes": matched_count,
            "unmatched_shapes": unmatched_count,
            "formula_candidates": formula_candidates,
        },
        "slides": slides_out,
        "aggregate_slot_deltas": aggregate,
        "template_layout_patch_suggestions": patch_suggestions(layouts, aggregate),
    }


def main(argv: Optional[List[str]] = None) -> int:
    localize_argparse()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, required=True, help="extract_pptx_shapes.py 生成的原始 shape JSON")
    parser.add_argument("--layouts", type=Path, required=True, help="模板 layout JSON，例如 template_layouts_16x9.json")
    parser.add_argument("--layout-plan", type=Path, help="可选的 layout_plan.json")
    parser.add_argument("--layout-map", type=Path, help="可选 JSON：将 slide index 映射到 layout name")
    parser.add_argument("--layout-name", help="所有 slide 统一使用同一个 layout name")
    parser.add_argument("--match-threshold", type=float, default=4.0, help="中心点匹配的最大距离，单位 inch")
    parser.add_argument("--output", "-o", type=Path, default=Path("layout_deltas.recovered.json"), help="输出恢复结果 JSON 的路径")
    args = parser.parse_args(argv)

    raw = read_json(args.raw)
    layouts = normalize_layouts(read_json(args.layouts))

    layout_map: Dict[int, str] = {}
    layout_map.update(load_layout_plan(args.layout_plan))
    layout_map.update(load_layout_map(args.layout_map))
    if args.layout_name:
        for slide in raw.get("slides", []):
            if isinstance(slide, dict):
                layout_map[int(slide.get("slide_index", len(layout_map)))] = args.layout_name

    recovered = recover(raw, layouts, layout_map, args.match_threshold)
    recovered["metadata"].update(
        {
            "source_raw_json": str(args.raw),
            "layouts_json": str(args.layouts),
            "layout_plan_json": str(args.layout_plan) if args.layout_plan else None,
            "layout_map_json": str(args.layout_map) if args.layout_map else None,
        }
    )

    args.output.write_text(json.dumps(recovered, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"已写入 {args.output} —— 成功匹配 {recovered['summary']['matched_shapes']} / "
        f"{recovered['summary']['shapes_considered']} 个文本 shape；"
        f"公式候选 {recovered['summary']['formula_candidates']} 个",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
