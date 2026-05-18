#!/usr/bin/env python3
"""将现有 PPTX 逆向为生成版 layout JSON，并输出布局分析。

这是无模板路径：不需要已有 template_layouts_16x9.json。
脚本会从 PPTX 中提取可见内容 shape，推断它们的 layout 角色，
把相似页面聚类成可复用 layout，并写出：

- template_layouts_16x9.generated.json
- layout_plan.generated.json
- layout_analysis.json
- layout_analysis.md

坐标与尺寸使用 inch；字号使用 pt。
"""

from __future__ import annotations

import argparse
import json
import math
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence, Tuple


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



SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    from extract_pptx_shapes import extract as extract_pptx_raw  # type: ignore
except Exception as exc:  # pragma: no cover - dependency/import error path
    raise SystemExit(
        "无法导入 extract_pptx_shapes.py。请确保 reverse_pptx_to_layout.py "
        "与它位于同一个 scripts/ 目录。"
    ) from exc

BBox = List[float]
Point = Tuple[float, float]

ROLE_ORDER = {
    "title": 10,
    "subtitle": 20,
    "section_header": 30,
    "body": 40,
    "formula": 45,
    "table": 50,
    "chart": 55,
    "image": 60,
    "caption": 70,
    "footer": 90,
    "page_number": 95,
    "text": 80,
    "shape": 85,
}

TEXT_KIND = {"text", "formula"}
MEDIA_KIND = {"image", "table", "chart"}

ROLE_LABEL_ZH = {
    "title": "标题",
    "subtitle": "副标题",
    "section_header": "小节标题",
    "body": "正文",
    "formula": "公式",
    "table": "表格",
    "chart": "图表",
    "image": "图片",
    "caption": "图注",
    "footer": "页脚",
    "page_number": "页码",
    "text": "文本",
    "shape": "装饰形状",
}


def display_role(role: Any) -> str:
    """把 JSON 中的英文 role 名称转换为中文展示文本。"""
    text = str(role)
    return f"{ROLE_LABEL_ZH.get(text, text)}（{text}）" if text in ROLE_LABEL_ZH else text


def markdown_cell(value: Any) -> str:
    """把 Markdown 报告中的空值和布尔值转换成中文展示。"""
    if value is None:
        return "无"
    if value is True:
        return "是"
    if value is False:
        return "否"
    return str(value)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def round_float(value: float, digits: int = 4) -> float:
    return round(float(value), digits)


def round_list(values: Iterable[float], digits: int = 4) -> List[float]:
    return [round_float(float(v), digits) for v in values]


def valid_bbox(bbox: Any) -> bool:
    return isinstance(bbox, list) and len(bbox) == 4 and all(isinstance(v, (int, float)) for v in bbox)


def as_bbox(bbox: Any) -> Optional[BBox]:
    if valid_bbox(bbox):
        return [float(v) for v in bbox]
    return None


def bbox_center(bbox: BBox) -> Point:
    return bbox[0] + bbox[2] / 2.0, bbox[1] + bbox[3] / 2.0


def bbox_area(bbox: BBox) -> float:
    return max(0.0, bbox[2]) * max(0.0, bbox[3])


def bbox_right(bbox: BBox) -> float:
    return bbox[0] + bbox[2]


def bbox_bottom(bbox: BBox) -> float:
    return bbox[1] + bbox[3]


def normalized_bbox(bbox: BBox, slide_w: float, slide_h: float) -> List[float]:
    if slide_w <= 0 or slide_h <= 0:
        return bbox[:]
    return [bbox[0] / slide_w, bbox[1] / slide_h, bbox[2] / slide_w, bbox[3] / slide_h]


def bbox_distance(a: BBox, b: BBox, slide_w: float, slide_h: float) -> float:
    """基于中心点和尺寸计算两个 bbox 的归一化距离。"""
    na = normalized_bbox(a, slide_w, slide_h)
    nb = normalized_bbox(b, slide_w, slide_h)
    acx, acy = na[0] + na[2] / 2.0, na[1] + na[3] / 2.0
    bcx, bcy = nb[0] + nb[2] / 2.0, nb[1] + nb[3] / 2.0
    parts = [acx - bcx, acy - bcy, na[2] - nb[2], na[3] - nb[3]]
    return math.sqrt(sum(p * p for p in parts))


def median(values: Sequence[float]) -> Optional[float]:
    vals = [float(v) for v in values if isinstance(v, (int, float))]
    if not vals:
        return None
    return float(statistics.median(vals))


def mode(values: Sequence[Any]) -> Any:
    vals = [v for v in values if v is not None]
    if not vals:
        return None
    counts = Counter(vals)
    return counts.most_common(1)[0][0]


def quantile(values: Sequence[float], q: float) -> Optional[float]:
    vals = sorted(float(v) for v in values if isinstance(v, (int, float)))
    if not vals:
        return None
    if len(vals) == 1:
        return vals[0]
    pos = (len(vals) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return vals[lo]
    return vals[lo] * (hi - pos) + vals[hi] * (pos - lo)


def slugify(value: str, max_len: int = 50) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9_\u4e00-\u9fff-]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value[:max_len] or "layout"


def get_text(shape: Mapping[str, Any]) -> str:
    tf = shape.get("text_frame")
    if isinstance(tf, dict):
        return str(tf.get("text", ""))
    return ""


def text_preview(text: str, limit: int = 80) -> str:
    return " ".join(text.split())[:limit]


def text_has_runs(shape: Mapping[str, Any]) -> bool:
    tf = shape.get("text_frame")
    if not isinstance(tf, dict):
        return False
    return bool(tf.get("has_runs"))


def paragraph_values(shape: Mapping[str, Any], field: str) -> List[Any]:
    tf = shape.get("text_frame")
    values: List[Any] = []
    if not isinstance(tf, dict):
        return values
    for paragraph in tf.get("paragraphs", []):
        if not isinstance(paragraph, dict):
            continue
        if field in paragraph:
            values.append(paragraph.get(field))
    return values


def font_summary(shape: Mapping[str, Any]) -> Dict[str, Any]:
    tf = shape.get("text_frame")
    if not isinstance(tf, dict):
        return {}

    run_sizes: List[float] = []
    paragraph_sizes: List[float] = []
    names: List[str] = []
    bolds: List[bool] = []
    italics: List[bool] = []
    underlines: List[bool] = []
    colors: List[str] = []
    alignments: List[str] = []
    levels: List[int] = []

    for paragraph in tf.get("paragraphs", []):
        if not isinstance(paragraph, dict):
            continue
        alignment = paragraph.get("alignment")
        if isinstance(alignment, str):
            alignments.append(alignment)
        level = paragraph.get("level")
        if isinstance(level, int):
            levels.append(level)

        p_font = paragraph.get("font") if isinstance(paragraph.get("font"), dict) else {}
        if isinstance(p_font.get("size_pt"), (int, float)):
            paragraph_sizes.append(float(p_font["size_pt"]))
        if isinstance(p_font.get("name"), str):
            names.append(p_font["name"])
        if isinstance(p_font.get("bold"), bool):
            bolds.append(p_font["bold"])
        if isinstance(p_font.get("italic"), bool):
            italics.append(p_font["italic"])
        if isinstance(p_font.get("underline"), bool):
            underlines.append(p_font["underline"])
        if isinstance(p_font.get("color_rgb"), str):
            colors.append(p_font["color_rgb"])

        for run in paragraph.get("runs", []):
            if not isinstance(run, dict):
                continue
            r_font = run.get("font") if isinstance(run.get("font"), dict) else {}
            if isinstance(r_font.get("size_pt"), (int, float)):
                run_sizes.append(float(r_font["size_pt"]))
            if isinstance(r_font.get("name"), str):
                names.append(r_font["name"])
            if isinstance(r_font.get("bold"), bool):
                bolds.append(r_font["bold"])
            if isinstance(r_font.get("italic"), bool):
                italics.append(r_font["italic"])
            if isinstance(r_font.get("underline"), bool):
                underlines.append(r_font["underline"])
            if isinstance(r_font.get("color_rgb"), str):
                colors.append(r_font["color_rgb"])

    effective_size = median(run_sizes) if run_sizes else median(paragraph_sizes)
    max_size = max(run_sizes + paragraph_sizes) if (run_sizes or paragraph_sizes) else None
    return {
        "font_name": mode(names),
        "effective_size_pt": round_float(effective_size, 2) if effective_size is not None else None,
        "max_size_pt": round_float(max_size, 2) if max_size is not None else None,
        "run_size_pt": round_float(median(run_sizes), 2) if run_sizes else None,
        "paragraph_size_pt": round_float(median(paragraph_sizes), 2) if paragraph_sizes else None,
        "bold": mode(bolds),
        "italic": mode(italics),
        "underline": mode(underlines),
        "color_rgb": mode(colors),
        "alignment": mode(alignments),
        "paragraph_levels": sorted(set(levels)),
        "run_size_missing": not bool(run_sizes) and bool(paragraph_sizes or get_text(shape)),
    }


def text_frame_summary(shape: Mapping[str, Any]) -> Dict[str, Any]:
    tf = shape.get("text_frame")
    if not isinstance(tf, dict):
        return {}
    return {
        "margin_left_in": tf.get("margin_left_in"),
        "margin_right_in": tf.get("margin_right_in"),
        "margin_top_in": tf.get("margin_top_in"),
        "margin_bottom_in": tf.get("margin_bottom_in"),
        "word_wrap": tf.get("word_wrap"),
        "auto_size": tf.get("auto_size"),
    }


def shape_kind(shape: Mapping[str, Any]) -> str:
    if shape.get("has_table"):
        return "table"
    if shape.get("has_chart"):
        return "chart"
    if shape.get("has_picture"):
        return "image"
    if shape.get("has_text_frame"):
        if bool(shape.get("contains_omml_xml")) or (not text_has_runs(shape) and not get_text(shape).strip()):
            return "formula"
        return "text"
    return "shape"


def is_full_slide_background(bbox: BBox, slide_w: float, slide_h: float) -> bool:
    if slide_w <= 0 or slide_h <= 0:
        return False
    covers_area = bbox_area(bbox) >= 0.88 * slide_w * slide_h
    covers_width = bbox[2] >= 0.92 * slide_w
    covers_height = bbox[3] >= 0.88 * slide_h
    starts_near_origin = bbox[0] <= 0.12 * slide_w and bbox[1] <= 0.12 * slide_h
    return covers_area and covers_width and covers_height and starts_near_origin


def is_low_information_text(text: str) -> bool:
    cleaned = re.sub(r"\s+", "", text)
    return not cleaned


def text_line_count(text: str) -> int:
    lines = [line for line in text.splitlines() if line.strip()]
    return max(1, len(lines)) if text.strip() else 0


def collect_slide_records(
    raw_slide: Mapping[str, Any],
    slide_w: float,
    slide_h: float,
    include_backgrounds: bool,
    include_decorative_shapes: bool,
    min_area_in2: float,
) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for shape in raw_slide.get("shapes", []):
        if not isinstance(shape, dict):
            continue
        bbox = as_bbox(shape.get("bbox"))
        if bbox is None:
            continue
        kind = shape_kind(shape)
        if not include_backgrounds and kind == "image" and is_full_slide_background(bbox, slide_w, slide_h):
            continue
        if not include_decorative_shapes and kind == "shape":
            continue
        if bbox_area(bbox) < min_area_in2:
            continue
        text = get_text(shape)
        if kind in TEXT_KIND and kind != "formula" and is_low_information_text(text):
            continue

        fs = font_summary(shape)
        cx, cy = bbox_center(bbox)
        records.append(
            {
                "shape_id": shape.get("shape_id"),
                "shape_name": shape.get("name"),
                "kind": kind,
                "role": kind if kind in MEDIA_KIND or kind == "formula" else "text",
                "bbox": round_list(bbox),
                "center": [round_float(cx), round_float(cy)],
                "area_in2": round_float(bbox_area(bbox)),
                "text": text,
                "text_preview": text_preview(text),
                "text_length": len(text.strip()),
                "line_count": text_line_count(text),
                "font": fs,
                "text_frame": text_frame_summary(shape),
                "contains_omml_xml": bool(shape.get("contains_omml_xml")),
            }
        )
    return records


def classify_text_roles(records: List[Dict[str, Any]], slide_w: float, slide_h: float) -> None:
    """就地修改 records，为文本 shape 分配语义角色。"""
    text_records = [r for r in records if r.get("kind") == "text"]
    if not text_records:
        return

    # 先识别页脚、页码、图注等元素。
    for rec in text_records:
        bbox = rec["bbox"]
        text = str(rec.get("text", "")).strip()
        font_size = rec.get("font", {}).get("effective_size_pt")
        font_size = float(font_size) if isinstance(font_size, (int, float)) else None
        cx, cy = bbox_center(bbox)
        bottom_zone = cy >= slide_h * 0.87 or bbox[1] >= slide_h * 0.82
        right_zone = cx >= slide_w * 0.82
        tinyish = font_size is not None and font_size <= 11.5
        numericish = bool(re.fullmatch(r"[\d\s/\-.]+", text))
        if bottom_zone and right_zone and numericish:
            rec["role"] = "page_number"
        elif bottom_zone and (tinyish or bbox[3] <= 0.45):
            rec["role"] = "footer"
        elif tinyish and bbox[3] <= 0.6 and len(text) <= 220:
            rec["role"] = "caption"
        else:
            rec["role"] = "body"

    title_candidates = [
        r
        for r in text_records
        if r.get("role") == "body" and (r["bbox"][1] <= slide_h * 0.28 or bbox_center(r["bbox"])[1] <= slide_h * 0.28)
    ]
    if not title_candidates:
        title_candidates = [r for r in text_records if r.get("role") == "body"]

    def title_score(rec: Mapping[str, Any]) -> Tuple[float, float, float]:
        bbox = rec["bbox"]
        font_size = rec.get("font", {}).get("max_size_pt") or rec.get("font", {}).get("effective_size_pt") or 0
        if not isinstance(font_size, (int, float)):
            font_size = 0
        # 字号更大、宽度更大、位置更靠上的文本框更可能是标题。
        score = float(font_size) * 1.6 + bbox[2] * 0.6 - bbox[1] * 4.0
        return score, -bbox[1], bbox[2]

    if title_candidates:
        sorted_candidates = sorted(title_candidates, key=title_score, reverse=True)
        title = sorted_candidates[0]
        title_font = title.get("font", {}).get("max_size_pt") or title.get("font", {}).get("effective_size_pt")
        title_bbox = title["bbox"]
        if title_bbox[1] <= slide_h * 0.34 or (isinstance(title_font, (int, float)) and title_font >= 18):
            title["role"] = "title"

            # 副标题通常靠近标题、位于标题下方，字号更小且靠上。
            for rec in sorted_candidates[1:]:
                bbox = rec["bbox"]
                if rec.get("role") != "body":
                    continue
                if bbox[1] <= slide_h * 0.42 and bbox[1] >= title_bbox[1] and bbox[3] <= max(0.9, title_bbox[3] * 1.4):
                    rec["role"] = "subtitle"
                    break

    # 小节标题通常在顶部或左侧栏，字号大于正文/图注但小于标题。
    body_font_sizes = [
        float(r.get("font", {}).get("effective_size_pt"))
        for r in text_records
        if r.get("role") == "body" and isinstance(r.get("font", {}).get("effective_size_pt"), (int, float))
    ]
    body_med = median(body_font_sizes) or 14.0
    for rec in text_records:
        if rec.get("role") != "body":
            continue
        bbox = rec["bbox"]
        fs = rec.get("font", {}).get("effective_size_pt")
        if isinstance(fs, (int, float)) and fs >= body_med + 3 and rec.get("line_count", 1) <= 2 and bbox[3] <= 0.9:
            if bbox[1] <= slide_h * 0.55:
                rec["role"] = "section_header"


def assign_slot_names(records: List[Dict[str, Any]]) -> None:
    counters: MutableMapping[str, int] = defaultdict(int)
    # 按阅读顺序命名，便于重复角色保持稳定 slot 名称。
    for rec in sorted(records, key=lambda r: (ROLE_ORDER.get(str(r.get("role")), 999), r["bbox"][1], r["bbox"][0], r["bbox"][2])):
        role = str(rec.get("role") or rec.get("kind") or "slot")
        counters[role] += 1
        rec["slot_name"] = role if counters[role] == 1 else f"{role}_{counters[role]}"


def slide_to_model(
    raw_slide: Mapping[str, Any],
    slide_w: float,
    slide_h: float,
    include_backgrounds: bool,
    include_decorative_shapes: bool,
    min_area_in2: float,
) -> Dict[str, Any]:
    slide_index = int(raw_slide.get("slide_index", 0))
    records = collect_slide_records(
        raw_slide,
        slide_w=slide_w,
        slide_h=slide_h,
        include_backgrounds=include_backgrounds,
        include_decorative_shapes=include_decorative_shapes,
        min_area_in2=min_area_in2,
    )
    classify_text_roles(records, slide_w, slide_h)
    for rec in records:
        rec["source_slide_index"] = slide_index
    assign_slot_names(records)
    records = sorted(records, key=lambda r: (ROLE_ORDER.get(str(r.get("role")), 999), r["bbox"][1], r["bbox"][0]))
    return {"slide_index": slide_index, "records": records}


def role_sequence(slide_model: Mapping[str, Any]) -> List[str]:
    return [str(rec.get("role")) for rec in slide_model.get("records", []) if isinstance(rec, dict)]


def slide_distance(a: Mapping[str, Any], b: Mapping[str, Any], slide_w: float, slide_h: float) -> float:
    ar = [r for r in a.get("records", []) if isinstance(r, dict)]
    br = [r for r in b.get("records", []) if isinstance(r, dict)]
    if len(ar) != len(br):
        return 10.0 + abs(len(ar) - len(br))
    if role_sequence(a) != role_sequence(b):
        return 5.0
    if not ar:
        return 0.0
    distances = [bbox_distance(x["bbox"], y["bbox"], slide_w, slide_h) for x, y in zip(ar, br)]
    return sum(distances) / len(distances)


def cluster_slides(
    slide_models: List[Dict[str, Any]], slide_w: float, slide_h: float, threshold: float, no_cluster: bool
) -> List[Dict[str, Any]]:
    clusters: List[Dict[str, Any]] = []
    if no_cluster:
        for model in slide_models:
            clusters.append({"members": [model], "prototype": model, "distances": [0.0]})
        return clusters

    for model in slide_models:
        best_idx = None
        best_dist = None
        for idx, cluster in enumerate(clusters):
            dist = slide_distance(model, cluster["prototype"], slide_w, slide_h)
            if best_dist is None or dist < best_dist:
                best_dist = dist
                best_idx = idx
        if best_idx is not None and best_dist is not None and best_dist <= threshold:
            clusters[best_idx]["members"].append(model)
            clusters[best_idx]["distances"].append(round_float(best_dist, 5))
        else:
            clusters.append({"members": [model], "prototype": model, "distances": [0.0]})
    return clusters


def aggregate_slot_style(records: List[Mapping[str, Any]]) -> Dict[str, Any]:
    fonts = [r.get("font", {}) for r in records if isinstance(r.get("font"), dict)]
    tfs = [r.get("text_frame", {}) for r in records if isinstance(r.get("text_frame"), dict)]
    result = {
        "font_name": mode([f.get("font_name") for f in fonts]),
        "font_size_pt": round_float(median([f.get("effective_size_pt") for f in fonts if isinstance(f.get("effective_size_pt"), (int, float))]), 2)
        if median([f.get("effective_size_pt") for f in fonts if isinstance(f.get("effective_size_pt"), (int, float))]) is not None
        else None,
        "max_font_size_pt": round_float(median([f.get("max_size_pt") for f in fonts if isinstance(f.get("max_size_pt"), (int, float))]), 2)
        if median([f.get("max_size_pt") for f in fonts if isinstance(f.get("max_size_pt"), (int, float))]) is not None
        else None,
        "bold": mode([f.get("bold") for f in fonts]),
        "italic": mode([f.get("italic") for f in fonts]),
        "underline": mode([f.get("underline") for f in fonts]),
        "color_rgb": mode([f.get("color_rgb") for f in fonts]),
        "alignment": mode([f.get("alignment") for f in fonts]),
        "margin_left_in": round_float(median([tf.get("margin_left_in") for tf in tfs if isinstance(tf.get("margin_left_in"), (int, float))]), 4)
        if median([tf.get("margin_left_in") for tf in tfs if isinstance(tf.get("margin_left_in"), (int, float))]) is not None
        else None,
        "margin_right_in": round_float(median([tf.get("margin_right_in") for tf in tfs if isinstance(tf.get("margin_right_in"), (int, float))]), 4)
        if median([tf.get("margin_right_in") for tf in tfs if isinstance(tf.get("margin_right_in"), (int, float))]) is not None
        else None,
        "margin_top_in": round_float(median([tf.get("margin_top_in") for tf in tfs if isinstance(tf.get("margin_top_in"), (int, float))]), 4)
        if median([tf.get("margin_top_in") for tf in tfs if isinstance(tf.get("margin_top_in"), (int, float))]) is not None
        else None,
        "margin_bottom_in": round_float(median([tf.get("margin_bottom_in") for tf in tfs if isinstance(tf.get("margin_bottom_in"), (int, float))]), 4)
        if median([tf.get("margin_bottom_in") for tf in tfs if isinstance(tf.get("margin_bottom_in"), (int, float))]) is not None
        else None,
        "word_wrap": mode([tf.get("word_wrap") for tf in tfs]),
        "auto_size": mode([tf.get("auto_size") for tf in tfs]),
    }
    return {k: v for k, v in result.items() if v is not None}


def average_bbox(records: Sequence[Mapping[str, Any]], digits: int = 4) -> BBox:
    cols = list(zip(*(r["bbox"] for r in records)))
    return round_list([sum(float(v) for v in col) / len(col) for col in cols], digits)


def slot_variance(records: Sequence[Mapping[str, Any]], avg_bbox: BBox, slide_w: float, slide_h: float) -> Dict[str, Any]:
    if not records:
        return {}
    distances = [bbox_distance(r["bbox"], avg_bbox, slide_w, slide_h) for r in records]
    return {
        "max_normalized_distance": round_float(max(distances), 5),
        "avg_normalized_distance": round_float(sum(distances) / len(distances), 5),
    }


def layout_name_for_cluster(index: int, cluster: Mapping[str, Any]) -> str:
    members = cluster["members"]
    prototype = members[0]
    roles = [str(r.get("role")) for r in prototype.get("records", []) if isinstance(r, dict)]
    counts = Counter(roles)
    name_parts = []
    for role in sorted(counts, key=lambda r: ROLE_ORDER.get(r, 999)):
        count = counts[role]
        name_parts.append(role if count == 1 else f"{role}{count}")
    suffix = slugify("_".join(name_parts), 60)
    return f"layout_{index:02d}_{suffix}" if suffix else f"layout_{index:02d}"


def build_layouts(
    clusters: List[Dict[str, Any]], slide_w: float, slide_h: float, round_digits: int
) -> Tuple[Dict[str, Any], Dict[int, str]]:
    layouts: Dict[str, Any] = {}
    plan_map: Dict[int, str] = {}

    for idx, cluster in enumerate(clusters, start=1):
        layout_name = layout_name_for_cluster(idx, cluster)
        members = cluster["members"]
        source_slide_indexes = [int(m["slide_index"]) for m in members]
        for si in source_slide_indexes:
            plan_map[si] = layout_name

        # 按 slot_name 聚合；聚类匹配要求角色序列一致，因此名称应基本对齐。
        by_slot: MutableMapping[str, List[Mapping[str, Any]]] = defaultdict(list)
        for member in members:
            for rec in member.get("records", []):
                if isinstance(rec, dict) and isinstance(rec.get("slot_name"), str):
                    by_slot[rec["slot_name"]].append(rec)

        slots: Dict[str, Any] = {}
        for slot_name, records in sorted(
            by_slot.items(),
            key=lambda item: (ROLE_ORDER.get(str(item[1][0].get("role")), 999), item[1][0]["bbox"][1], item[1][0]["bbox"][0]),
        ):
            avg_bbox = average_bbox(records, digits=round_digits)
            role = mode([r.get("role") for r in records])
            kind = mode([r.get("kind") for r in records])
            slot_spec: Dict[str, Any] = {
                "bbox": avg_bbox,
                "role": role,
                "kind": kind,
                "samples": len(records),
                "source_slide_indexes": sorted({int(r.get("source_slide_index")) for r in records if isinstance(r.get("source_slide_index"), int)}),
                "stability": slot_variance(records, avg_bbox, slide_w, slide_h),
            }
            style = aggregate_slot_style(records)
            if style:
                slot_spec["style"] = style
            previews = [str(r.get("text_preview")) for r in records if str(r.get("text_preview", "")).strip()]
            if previews:
                slot_spec["sample_text_preview"] = previews[:3]
            slots[slot_name] = slot_spec

        avg_cluster_distance = sum(cluster.get("distances", [0.0])) / max(1, len(cluster.get("distances", [])))
        layouts[layout_name] = {
            "slide_size": {"width_in": round_float(slide_w, 4), "height_in": round_float(slide_h, 4)},
            "source_slide_indexes": source_slide_indexes,
            "slide_count": len(source_slide_indexes),
            "cluster_distance": {
                "avg_normalized_distance": round_float(avg_cluster_distance, 5),
                "max_normalized_distance": round_float(max(cluster.get("distances", [0.0])), 5),
            },
            "slots": slots,
        }

    return layouts, plan_map


def describe_layout(layout_name: str, layout_spec: Mapping[str, Any]) -> str:
    slots = layout_spec.get("slots", {}) if isinstance(layout_spec.get("slots"), dict) else {}
    roles = [str(spec.get("role")) for spec in slots.values() if isinstance(spec, dict)]
    counts = Counter(roles)
    bits: List[str] = []
    if counts.get("title"):
        bits.append("顶部标题区")
    if counts.get("subtitle"):
        bits.append("副标题区")
    if counts.get("body", 0) == 1:
        bits.append("单主体内容区")
    elif counts.get("body", 0) >= 2:
        bits.append(f"{counts['body']} 个主体内容区")
    media_count = counts.get("image", 0) + counts.get("chart", 0) + counts.get("table", 0)
    if media_count:
        bits.append(f"{media_count} 个视觉/数据对象区")
    if counts.get("formula"):
        bits.append("公式区")
    if counts.get("footer") or counts.get("page_number"):
        bits.append("页脚/页码区")
    summary = "、".join(bits) if bits else "自由排版布局"
    return f"{layout_name}: {summary}"


def margin_summary(slide_models: Sequence[Mapping[str, Any]], slide_w: float, slide_h: float) -> Dict[str, Any]:
    lefts: List[float] = []
    rights: List[float] = []
    tops: List[float] = []
    bottoms: List[float] = []
    for model in slide_models:
        for rec in model.get("records", []):
            if not isinstance(rec, dict):
                continue
            role = rec.get("role")
            if role in {"footer", "page_number", "caption"}:
                continue
            bbox = rec.get("bbox")
            if valid_bbox(bbox):
                b = [float(v) for v in bbox]
                lefts.append(b[0])
                rights.append(slide_w - bbox_right(b))
                tops.append(b[1])
                bottoms.append(slide_h - bbox_bottom(b))
    return {
        "median_left_in": round_float(median(lefts), 3) if median(lefts) is not None else None,
        "median_right_in": round_float(median(rights), 3) if median(rights) is not None else None,
        "median_top_in": round_float(median(tops), 3) if median(tops) is not None else None,
        "median_bottom_in": round_float(median(bottoms), 3) if median(bottoms) is not None else None,
    }


def typography_summary(slide_models: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    by_role: MutableMapping[str, List[Mapping[str, Any]]] = defaultdict(list)
    all_fonts: List[str] = []
    run_missing = 0
    text_shape_count = 0
    for model in slide_models:
        for rec in model.get("records", []):
            if not isinstance(rec, dict):
                continue
            if rec.get("kind") not in TEXT_KIND:
                continue
            text_shape_count += 1
            font = rec.get("font") if isinstance(rec.get("font"), dict) else {}
            by_role[str(rec.get("role"))].append(font)
            if isinstance(font.get("font_name"), str):
                all_fonts.append(font["font_name"])
            if font.get("run_size_missing"):
                run_missing += 1

    roles_out: Dict[str, Any] = {}
    for role, fonts in sorted(by_role.items(), key=lambda item: ROLE_ORDER.get(item[0], 999)):
        sizes = [f.get("effective_size_pt") for f in fonts if isinstance(f.get("effective_size_pt"), (int, float))]
        roles_out[role] = {
            "samples": len(fonts),
            "median_size_pt": round_float(median(sizes), 2) if median(sizes) is not None else None,
            "min_size_pt": round_float(min(sizes), 2) if sizes else None,
            "max_size_pt": round_float(max(sizes), 2) if sizes else None,
            "common_font": mode([f.get("font_name") for f in fonts]),
            "common_bold": mode([f.get("bold") for f in fonts]),
            "common_alignment": mode([f.get("alignment") for f in fonts]),
        }
    return {
        "common_fonts": Counter(all_fonts).most_common(8),
        "run_size_missing_shapes": run_missing,
        "text_shape_count": text_shape_count,
        "run_size_missing_ratio": round_float(run_missing / text_shape_count, 4) if text_shape_count else 0,
        "by_role": roles_out,
    }


def layout_usage(layouts: Mapping[str, Any]) -> List[Dict[str, Any]]:
    rows = []
    for name, spec in layouts.items():
        if not isinstance(spec, dict):
            continue
        rows.append(
            {
                "layout_name": name,
                "slide_count": int(spec.get("slide_count", 0)),
                "source_slide_indexes": spec.get("source_slide_indexes", []),
                "slot_count": len(spec.get("slots", {})) if isinstance(spec.get("slots"), dict) else 0,
                "description": describe_layout(name, spec),
            }
        )
    rows.sort(key=lambda r: (-r["slide_count"], r["layout_name"]))
    return rows


def infer_composition_characteristics(layouts: Mapping[str, Any]) -> List[str]:
    lines: List[str] = []
    usage = layout_usage(layouts)
    if not usage:
        return ["未检测到可用于生成 layout 的内容形状。"]
    repeated = [u for u in usage if u["slide_count"] >= 2]
    if repeated:
        lines.append(f"检测到 {len(repeated)} 个可复用布局，说明该 PPT 存在重复版式结构。")
    else:
        lines.append("每页版式差异较大，更接近逐页定制排版。")

    title_layouts = 0
    media_layouts = 0
    multi_body_layouts = 0
    formula_layouts = 0
    for spec in layouts.values():
        if not isinstance(spec, dict):
            continue
        roles = [slot.get("role") for slot in spec.get("slots", {}).values() if isinstance(slot, dict)]
        counts = Counter(roles)
        if counts.get("title"):
            title_layouts += 1
        if counts.get("image", 0) + counts.get("chart", 0) + counts.get("table", 0):
            media_layouts += 1
        if counts.get("body", 0) >= 2:
            multi_body_layouts += 1
        if counts.get("formula"):
            formula_layouts += 1
    if title_layouts:
        lines.append(f"{title_layouts} 个布局包含明确标题区，标题通常可作为稳定 slot 保留。")
    if multi_body_layouts:
        lines.append(f"{multi_body_layouts} 个布局使用多主体内容区，适合保留为双栏/多栏模板。")
    if media_layouts:
        lines.append(f"{media_layouts} 个布局包含图片、图表或表格对象，需要在 layout 文件中保留非文本 slot。")
    if formula_layouts:
        lines.append(f"{formula_layouts} 个布局包含公式区，应保留 formula slot 以支持 OMML 或公式渲染。")
    return lines


def build_analysis(
    raw: Mapping[str, Any], slide_models: Sequence[Mapping[str, Any]], layouts: Mapping[str, Any]
) -> Dict[str, Any]:
    slide_w = float(raw.get("slide_width_in") or 0)
    slide_h = float(raw.get("slide_height_in") or 0)
    role_counts = Counter()
    kind_counts = Counter()
    per_slide_counts: List[int] = []
    for model in slide_models:
        records = [r for r in model.get("records", []) if isinstance(r, dict)]
        per_slide_counts.append(len(records))
        for rec in records:
            role_counts[str(rec.get("role"))] += 1
            kind_counts[str(rec.get("kind"))] += 1

    return {
        "metadata": {
            "source_pptx": raw.get("source_pptx"),
            "slide_size": {"width_in": slide_w, "height_in": slide_h},
            "unit": {"geometry": "inch", "font_size": "pt"},
        },
        "summary": {
            "slide_count": int(raw.get("slide_count", len(slide_models))),
            "layout_count": len(layouts),
            "total_content_slots": sum(per_slide_counts),
            "median_slots_per_slide": round_float(median(per_slide_counts), 2) if median(per_slide_counts) is not None else 0,
            "role_counts": dict(role_counts.most_common()),
            "kind_counts": dict(kind_counts.most_common()),
        },
        "layout_usage": layout_usage(layouts),
        "spatial_summary": margin_summary(slide_models, slide_w, slide_h),
        "typography_summary": typography_summary(slide_models),
        "layout_characteristics": infer_composition_characteristics(layouts),
    }


def markdown_table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> str:
    out = ["| " + " | ".join(markdown_cell(h) for h in headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        out.append("| " + " | ".join(markdown_cell(cell) for cell in row) + " |")
    return "\n".join(out)


def render_analysis_markdown(analysis: Mapping[str, Any]) -> str:
    summary = analysis.get("summary", {}) if isinstance(analysis.get("summary"), dict) else {}
    spatial = analysis.get("spatial_summary", {}) if isinstance(analysis.get("spatial_summary"), dict) else {}
    typography = analysis.get("typography_summary", {}) if isinstance(analysis.get("typography_summary"), dict) else {}
    usage = analysis.get("layout_usage", []) if isinstance(analysis.get("layout_usage"), list) else []

    lines: List[str] = []
    lines.append("# PPTX 版式逆向分析")
    lines.append("")
    lines.append("## 概览")
    lines.append("")
    lines.append(f"- 幻灯片数：{summary.get('slide_count', 0)}")
    lines.append(f"- 生成 layout 数：{summary.get('layout_count', 0)}")
    lines.append(f"- 内容 slot 总数：{summary.get('total_content_slots', 0)}")
    lines.append(f"- 每页 slot 中位数：{summary.get('median_slots_per_slide', 0)}")
    lines.append("")

    characteristics = analysis.get("layout_characteristics", [])
    if isinstance(characteristics, list) and characteristics:
        lines.append("## 布局特点")
        lines.append("")
        for item in characteristics:
            lines.append(f"- {item}")
        lines.append("")

    if usage:
        lines.append("## 生成的 layout")
        lines.append("")
        rows = []
        for item in usage:
            rows.append(
                [
                    item.get("layout_name"),
                    item.get("slide_count"),
                    ", ".join(str(x) for x in item.get("source_slide_indexes", [])),
                    item.get("slot_count"),
                    item.get("description"),
                ]
            )
        lines.append(markdown_table(["layout 名称", "页数", "来源 slide index", "Slot 数", "说明"], rows))
        lines.append("")

    role_counts = summary.get("role_counts") if isinstance(summary.get("role_counts"), dict) else {}
    if role_counts:
        lines.append("## Slot 角色分布")
        lines.append("")
        lines.append(markdown_table(["角色", "数量"], [[display_role(k), v] for k, v in role_counts.items()]))
        lines.append("")

    lines.append("## 空间位置摘要")
    lines.append("")
    lines.append(
        markdown_table(
            ["指标", "数值（inch）"],
            [
                ["左边距中位数", spatial.get("median_left_in")],
                ["右边距中位数", spatial.get("median_right_in")],
                ["上边距中位数", spatial.get("median_top_in")],
                ["下边距中位数", spatial.get("median_bottom_in")],
            ],
        )
    )
    lines.append("")

    by_role = typography.get("by_role") if isinstance(typography.get("by_role"), dict) else {}
    if by_role:
        lines.append("## 按角色统计的字体")
        lines.append("")
        rows = []
        for role, spec in by_role.items():
            if not isinstance(spec, dict):
                continue
            rows.append(
                [
                    display_role(role),
                    spec.get("samples"),
                    spec.get("median_size_pt"),
                    spec.get("min_size_pt"),
                    spec.get("max_size_pt"),
                    spec.get("common_font"),
                    spec.get("common_alignment"),
                ]
            )
        lines.append(markdown_table(["角色", "样本数", "字号中位数 pt", "最小 pt", "最大 pt", "常见字体", "对齐方式"], rows))
        lines.append("")

    lines.append("## 备注")
    lines.append("")
    lines.append("- bbox 格式为 `[x, y, width, height]`，单位 inch。")
    lines.append("- 生成的 slot 名称和角色来自启发式推断，替换生产模板前必须人工复核。")
    lines.append("- 默认排除整页背景图；如果背景图也是可复用 layout 的一部分，请使用 `--include-backgrounds` 重新运行。")
    return "\n".join(lines) + "\n"


def reverse_pptx_to_layout(
    pptx_path: Path,
    include_backgrounds: bool,
    include_decorative_shapes: bool,
    min_area_in2: float,
    cluster_threshold: float,
    no_cluster: bool,
    round_digits: int,
) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    raw = extract_pptx_raw(pptx_path, include_images=True)
    slide_w = float(raw.get("slide_width_in") or 0)
    slide_h = float(raw.get("slide_height_in") or 0)
    slide_models = [
        slide_to_model(
            slide,
            slide_w=slide_w,
            slide_h=slide_h,
            include_backgrounds=include_backgrounds,
            include_decorative_shapes=include_decorative_shapes,
            min_area_in2=min_area_in2,
        )
        for slide in raw.get("slides", [])
        if isinstance(slide, dict)
    ]
    clusters = cluster_slides(slide_models, slide_w, slide_h, threshold=cluster_threshold, no_cluster=no_cluster)
    layouts, plan_map = build_layouts(clusters, slide_w, slide_h, round_digits=round_digits)

    layout_json = {
        "metadata": {
            "source_pptx": str(pptx_path),
            "generated_by": "pptx-layout-reverse/reverse_pptx_to_layout.py",
            "unit": {"geometry": "inch", "font_size": "pt"},
            "slide_size": {"width_in": round_float(slide_w, 4), "height_in": round_float(slide_h, 4)},
            "cluster_threshold": cluster_threshold,
            "include_backgrounds": include_backgrounds,
            "include_decorative_shapes": include_decorative_shapes,
        },
        "layouts": layouts,
    }

    layout_plan = {
        "metadata": {
            "source_pptx": str(pptx_path),
            "generated_by": "pptx-layout-reverse/reverse_pptx_to_layout.py",
        },
        "slides": [
            {
                "slide_index": model["slide_index"],
                "layout_name": plan_map.get(int(model["slide_index"])),
                "slot_count": len(model.get("records", [])),
            }
            for model in sorted(slide_models, key=lambda m: int(m["slide_index"]))
        ],
    }

    raw_model_json = {
        "metadata": {
            "source_pptx": str(pptx_path),
            "slide_size": {"width_in": round_float(slide_w, 4), "height_in": round_float(slide_h, 4)},
        },
        "slides": slide_models,
    }
    analysis = build_analysis(raw, slide_models, layouts)
    return layout_json, layout_plan, analysis, raw_model_json


def main(argv: Optional[List[str]] = None) -> int:
    localize_argparse()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pptx", type=Path, help="需要逆向为 layout 的现有 PPTX 路径")
    parser.add_argument("--output-dir", type=Path, default=Path("pptx_layout_reverse_out"), help="生成文件的输出目录")
    parser.add_argument("--layout-output", type=Path, help="可选：明确指定生成 layout JSON 的路径")
    parser.add_argument("--plan-output", type=Path, help="可选：明确指定生成 layout plan JSON 的路径")
    parser.add_argument("--analysis-json-output", type=Path, help="可选：明确指定分析 JSON 的路径")
    parser.add_argument("--analysis-md-output", type=Path, help="可选：明确指定分析 Markdown 的路径")
    parser.add_argument("--raw-model-output", type=Path, help="可选：明确指定逐页 slot 模型 JSON 的路径")
    parser.add_argument("--include-backgrounds", action="store_true", help="将铺满整页的背景图也作为 image slot 纳入")
    parser.add_argument("--include-decorative-shapes", action="store_true", help="包含非文本、非媒体的装饰性 shape")
    parser.add_argument("--min-area", type=float, default=0.02, help="纳入分析的最小 shape 面积，单位平方 inch")
    parser.add_argument("--cluster-threshold", type=float, default=0.075, help="合并页面为同一 layout 的最大归一化距离")
    parser.add_argument("--no-cluster", action="store_true", help="不聚类，每页生成一个独立 layout")
    parser.add_argument("--round-digits", type=int, default=4, help="生成 bbox 时保留的小数位数")
    args = parser.parse_args(argv)

    if not args.pptx.exists():
        parser.error(f"找不到 PPTX 文件：{args.pptx}")

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    layout_path = args.layout_output or output_dir / "template_layouts_16x9.generated.json"
    plan_path = args.plan_output or output_dir / "layout_plan.generated.json"
    analysis_json_path = args.analysis_json_output or output_dir / "layout_analysis.json"
    analysis_md_path = args.analysis_md_output or output_dir / "layout_analysis.md"
    raw_model_path = args.raw_model_output or output_dir / "pptx_slide_slot_model.json"

    layout_json, layout_plan, analysis, raw_model = reverse_pptx_to_layout(
        args.pptx,
        include_backgrounds=args.include_backgrounds,
        include_decorative_shapes=args.include_decorative_shapes,
        min_area_in2=args.min_area,
        cluster_threshold=args.cluster_threshold,
        no_cluster=args.no_cluster,
        round_digits=args.round_digits,
    )

    write_json(layout_path, layout_json)
    write_json(plan_path, layout_plan)
    write_json(analysis_json_path, analysis)
    write_json(raw_model_path, raw_model)
    analysis_md_path.parent.mkdir(parents=True, exist_ok=True)
    analysis_md_path.write_text(render_analysis_markdown(analysis), encoding="utf-8")

    summary = analysis.get("summary", {})
    print(
        "已写入生成的 layout 文件：\n"
        f"  - {layout_path}\n"
        f"  - {plan_path}\n"
        f"  - {analysis_json_path}\n"
        f"  - {analysis_md_path}\n"
        f"  - {raw_model_path}\n"
        f"幻灯片数：{summary.get('slide_count')}；layout 数：{summary.get('layout_count')}；"
        f"内容 slot 数：{summary.get('total_content_slots')}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
