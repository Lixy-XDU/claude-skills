#!/usr/bin/env python3
"""
生成 Claude Code 本地 skill 的中文版 HTML 关系图。

默认行为：
  - 扫描 ~/.claude/skills/*/SKILL.md
  - 给缺失的 skill 自动创建 skill.meta.yaml
  - 默认保留已有 skill.meta.yaml，不覆盖手工编辑
  - 生成 ~/.claude/skills/SKILL_GRAPH.html

无第三方依赖。内置简易 YAML 读写器，仅支持本脚本生成的格式。
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple


RELATION_KEYS = [
    "coordinates", "cooperates_with", "upstream", "downstream",
    "should_run_before", "should_run_after", "supersedes", "overlaps_with",
]

RELATION_LABELS_ZH = {
    "coordinates": "协调",
    "cooperates_with": "协同",
    "upstream": "上游",
    "downstream": "下游",
    "should_run_before": "先于",
    "should_run_after": "后于",
    "supersedes": "替代",
    "overlaps_with": "重叠",
}

CATEGORY_ORDER_ZH = [
    "元技能", "规划与评审", "编码与调试", "测试与质量", "文档与写作",
    "运维与发布", "研究与发现", "设计与界面", "数据与分析",
    "MATLAB", "数学与方法库",
    "项目专用", "未分类",
]


def today() -> str:
    return _dt.date.today().isoformat()


def normalize_skill_name(name: str) -> str:
    return (name or "").strip().lstrip("/")


def slug_to_title(name: str) -> str:
    return normalize_skill_name(name).replace("-", " ").replace("_", " ").title()


def normalize_categories(raw) -> List[str]:
    """将 category 字段规范化为字符串列表。支持逗号分隔的多分类。"""
    if isinstance(raw, list):
        return [c.strip() for c in raw if c.strip()]
    if isinstance(raw, str):
        return [c.strip() for c in raw.split(",") if c.strip()]
    return ["未分类"]


def parse_frontmatter(text: str) -> Dict[str, str]:
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    data: Dict[str, str] = {}
    for line in parts[1].splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        k, v = line.split(":", 1)
        data[k.strip()] = v.strip().strip('"').strip("'")
    return data


def extract_heading(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def read_skill_md(skill_dir: Path) -> Dict[str, str]:
    p = skill_dir / "SKILL.md"
    if not p.exists():
        return {}
    text = p.read_text(encoding="utf-8", errors="replace")
    fm = parse_frontmatter(text)
    name = normalize_skill_name(fm.get("name") or skill_dir.name)
    return {
        "name": name,
        "title": extract_heading(text) or slug_to_title(name),
        "description": fm.get("description", ""),
        "argument-hint": fm.get("argument-hint", ""),
        "disable-model-invocation": fm.get("disable-model-invocation", ""),
    }


def infer_category(name: str, description: str) -> str:
    text = f"{name} {description}".lower()
    rules = [
        (["skill-index", "skill-graph", "skill-distiller", "find-local-skills",
          "local skill", "skill meta", "skill.meta", "metadata"], "元技能"),
        (["math", "数学", "method", "方法", "formula", "theorem", "proof"], "数学与方法库"),
        (["release", "deploy", "rollback", "monitor", "ops", "production", "运维", "发布"], "运维与发布"),
        (["test", "qa", "coverage", "regression", "validation", "测试", "质量"], "测试与质量"),
        (["doc", "docs", "documentation", "changelog", "writing", "spec", "文档", "写作"], "文档与写作"),
        (["plan", "review", "risk", "migration", "audit", "architecture", "strategy", "规划", "评审", "风险"], "规划与评审"),
        (["ml-", "matlab-", "matlab "], "MATLAB"),
        (["ui", "ux", "design", "frontend", "component", "visual", "gui", "界面", "设计"], "设计与界面"),
        (["data", "analysis", "metric", "report", "analytics", "数据", "分析"], "数据与分析"),
        (["code", "debug", "bug", "refactor", "python", "implementation", "编码", "调试"], "编码与调试"),
        (["find", "search", "research", "discovery", "external", "community", "搜索", "发现"], "研究与发现"),
    ]
    for keywords, label in rules:
        if any(k in text for k in keywords):
            return label
    return "未分类"


def infer_scope(root: Path) -> str:
    try:
        if root.resolve() == (Path.home() / ".claude" / "skills").resolve():
            return "personal"
    except Exception:
        pass
    if ".claude" in root.parts:
        return "project"
    return "unknown"


def infer_relations(name: str) -> Dict[str, List[str]]:
    name = normalize_skill_name(name)
    rel = {k: [] for k in RELATION_KEYS}
    presets = {
        "find-local-skills": {
            "downstream": ["skill-distiller", "skill-index", "skill-graph"],
            "should_run_before": ["skill-distiller", "skill-index"],
        },
        "find-skills": {
            "downstream": ["skill-distiller", "skill-index"],
            "should_run_before": ["skill-distiller"],
        },
        "skill-distiller": {
            "upstream": ["find-local-skills", "find-skills"],
            "downstream": ["skill-index", "skill-graph"],
            "should_run_after": ["find-local-skills"],
            "should_run_before": ["skill-index", "skill-graph"],
        },
        "skill-index": {
            "coordinates": ["find-local-skills", "find-skills", "skill-distiller", "skill-graph"],
            "upstream": ["find-local-skills", "find-skills", "skill-distiller", "skill-graph"],
            "should_run_after": ["find-local-skills", "skill-distiller", "skill-graph"],
        },
        "skill-graph": {
            "cooperates_with": ["skill-index", "find-local-skills", "skill-distiller"],
            "upstream": ["find-local-skills", "skill-distiller"],
            "downstream": ["skill-index"],
            "should_run_after": ["skill-distiller", "find-local-skills"],
        },
        "literature-to-math": {
            "cooperates_with": ["math-method-lib"],
            "upstream": ["math-method-lib"],
            "downstream": ["math-method-lib"],
        },
    }
    rel.update(presets.get(name, {}))
    return rel


def yaml_list(items: List[str], indent: int = 4) -> str:
    if not items:
        return " []"
    sp = " " * indent
    return "\n" + "\n".join(f"{sp}- {x}" for x in items)


def render_meta_yaml(meta: Dict[str, Any]) -> str:
    lines = [
        f"name: {meta['name']}",
        f"title: {meta['title']}",
        f"category: {meta['category']}",
        f"scope: {meta['scope']}",
        f"status: {meta['status']}",
        f"version: {meta['version']}",
        f"updated: {meta['updated']}",
        "",
        f"purpose: {meta['purpose']}",
        "",
        "relations:",
    ]
    rel = meta.get("relations", {})
    for k in RELATION_KEYS:
        lines.append(f"  {k}:{yaml_list(rel.get(k, []), indent=4)}")
    lines += [
        "",
        "notes:",
        "  - 自动生成的 metadata。建议手工检查 category、purpose 和 relations。",
        "",
    ]
    return "\n".join(lines)


def create_meta_from_skill(skill_dir: Path, root: Path) -> Dict[str, Any]:
    skill = read_skill_md(skill_dir)
    name = normalize_skill_name(skill.get("name") or skill_dir.name)
    desc = skill.get("description", "")
    return {
        "name": name,
        "title": skill.get("title") or slug_to_title(name),
        "category": infer_category(name, desc),
        "scope": infer_scope(root),
        "status": "active",
        "version": "0.1.0",
        "updated": today(),
        "purpose": desc if desc else f"本地 Claude Code skill：{name}。",
        "relations": infer_relations(name),
    }


def parse_simple_meta_yaml(path: Path) -> Dict[str, Any]:
    data: Dict[str, Any] = {}
    relations: Dict[str, List[str]] = {}
    notes: List[str] = []
    section = None
    current_rel = None

    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # 顶层 key
        if not line.startswith(" ") and ":" in line:
            k, v = line.split(":", 1)
            k = k.strip()
            v = v.strip()
            current_rel = None
            if k == "relations":
                section = "relations"
                data["relations"] = relations
                continue
            if k == "notes":
                section = "notes"
                data["notes"] = notes
                continue
            section = None
            data[k] = [] if v == "[]" else v.strip('"').strip("'")
            continue

        if section == "relations":
            # "  key: []" or "  key:"
            if raw.startswith("  ") and not raw.startswith("    ") and ":" in stripped:
                k, v = stripped.split(":", 1)
                current_rel = k.strip()
                v = v.strip()
                relations[current_rel] = []
                continue
            if raw.startswith("    - ") and current_rel:
                relations[current_rel].append(stripped[2:].strip())
                continue

        if section == "notes" and stripped.startswith("- "):
            notes.append(stripped[2:].strip())

    data.setdefault("relations", relations)
    data.setdefault("notes", notes)
    return data


def discover_skill_dirs(root: Path) -> List[Path]:
    if not root.exists():
        return []
    return sorted(p for p in root.iterdir() if p.is_dir() and (p / "SKILL.md").exists())


def ensure_meta_files(root: Path, overwrite: bool = False) -> Tuple[List[Path], List[Path]]:
    created, preserved = [], []
    for d in discover_skill_dirs(root):
        mp = d / "skill.meta.yaml"
        if mp.exists() and not overwrite:
            preserved.append(mp)
            continue
        mp.write_text(render_meta_yaml(create_meta_from_skill(d, root)), encoding="utf-8")
        created.append(mp)
    return created, preserved


def load_all_metadata(root: Path) -> Tuple[List[Dict[str, Any]], List[str]]:
    metas: List[Dict[str, Any]] = []
    warnings: List[str] = []
    for d in discover_skill_dirs(root):
        mp = d / "skill.meta.yaml"
        skill = read_skill_md(d)
        if not mp.exists():
            warnings.append(f"缺少 metadata：{mp}")
            meta = create_meta_from_skill(d, root)
        else:
            try:
                meta = parse_simple_meta_yaml(mp)
            except Exception as e:
                warnings.append(f"无法解析 {mp}: {e}")
                meta = create_meta_from_skill(d, root)

        name = normalize_skill_name(meta.get("name") or skill.get("name") or d.name)
        meta["_dir"] = str(d)
        meta["_path"] = str(mp)
        meta["name"] = name
        meta.setdefault("title", skill.get("title") or slug_to_title(name))
        meta.setdefault("category", infer_category(name, skill.get("description", "")))
        meta["categories"] = normalize_categories(meta.get("category", "未分类"))
        meta.setdefault("scope", infer_scope(root))
        meta.setdefault("status", "active")
        meta.setdefault("version", "0.1.0")
        meta.setdefault("updated", "")
        meta.setdefault("purpose", skill.get("description", ""))
        meta.setdefault("relations", {k: [] for k in RELATION_KEYS})
        meta.setdefault("notes", [])
        for k in RELATION_KEYS:
            meta["relations"].setdefault(k, [])
        metas.append(meta)
    return metas, warnings


def build_edges(metas: List[Dict[str, Any]]) -> Tuple[List[Dict[str, str]], List[str]]:
    known = {normalize_skill_name(m.get("name", "")) for m in metas}
    # 需要翻转方向的关系键（语义为反向）
    FLIP_KEYS = {"upstream", "should_run_after"}
    # 不建边的关系键
    SKIP_KEYS = {"cooperates_with", "overlaps_with"}
    edges, warnings, seen = [], [], set()
    for m in metas:
        src = normalize_skill_name(m.get("name", ""))
        rel = m.get("relations", {}) or {}
        for key, label in RELATION_LABELS_ZH.items():
            if key in SKIP_KEYS:
                continue
            targets = rel.get(key, []) or []
            if isinstance(targets, str):
                targets = [targets]
            for t in targets:
                tgt = normalize_skill_name(str(t))
                if not tgt:
                    continue
                if tgt not in known:
                    warnings.append(f"`/{src}` 的 `{label}` 关系指向未知 skill：`{tgt}`")
                    continue
                # 翻转键：边方向为 target(上游) → source(下游)
                if key in FLIP_KEYS:
                    s, d = tgt, src
                else:
                    s, d = src, tgt
                k = (s, d)
                if k in seen:
                    continue
                seen.add(k)
                edges.append({"source": s, "target": d, "type": key, "label": label})
    return edges, warnings


def detect_isolated(metas, edges):
    names = {normalize_skill_name(m.get("name", "")) for m in metas}
    connected = set()
    for e in edges:
        connected.add(e["source"])
        connected.add(e["target"])
    return sorted(names - connected)


# ---------- HTML 模板（已支持节点拖拽） ----------
HTML_TEMPLATE = r"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Claude Code Skill 关系图</title>
<style>
:root {
  --bg:#f6f7fb; --panel:#fff; --text:#1f2937; --muted:#6b7280;
  --border:#e5e7eb; --accent:#2563eb; --accent-soft:#dbeafe;
  --shadow:0 8px 24px rgba(15,23,42,.08);
}
*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei","Noto Sans CJK SC",Arial,sans-serif;background:var(--bg);color:var(--text)}
header{padding:22px 28px 14px}
h1{margin:0 0 8px;font-size:26px}
.sub{color:var(--muted);font-size:13px}
.toolbar{display:grid;grid-template-columns:1.4fr repeat(3,minmax(140px,.5fr));gap:10px;padding:12px 28px 18px}
input,select{border:1px solid var(--border);background:#fff;color:var(--text);border-radius:10px;padding:10px 12px;font-size:14px}
.layout{display:grid;grid-template-columns:300px 1fr 360px;gap:14px;padding:0 28px 28px;min-height:calc(100vh - 160px)}
.panel{background:var(--panel);border:1px solid var(--border);border-radius:16px;box-shadow:var(--shadow);overflow:hidden}
.panel h2{font-size:15px;margin:0;padding:14px 16px;border-bottom:1px solid var(--border);background:#fafafa}
.list{max-height:calc(100vh - 230px);overflow:auto}
.item{padding:12px 14px;border-bottom:1px solid var(--border);cursor:pointer}
.item:hover,.item.active{background:var(--accent-soft)}
.item .name{font-weight:700;font-size:14px}
.item .meta{color:var(--muted);font-size:12px;margin-top:4px}
.graph-wrap{height:calc(100vh - 210px);min-height:540px;position:relative;user-select:none;-webkit-user-select:none}
.zoom-reset{position:absolute;bottom:12px;right:12px;background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:6px 14px;font-size:13px;color:var(--text);cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,.08);display:none;z-index:10}
.zoom-reset.visible{display:block}
svg{width:100%;height:100%;display:block;background:radial-gradient(circle at 20px 20px,rgba(37,99,235,.05) 2px,transparent 2px);background-size:36px 36px;user-select:none;-webkit-user-select:none}
.edge{stroke:#94a3b8;stroke-width:0.8;stroke-opacity:0.35;marker-end:url(#arrow);fill:none}
.legend{display:flex;gap:16px;justify-content:center;padding:8px 0 0 0;font-size:12px;color:var(--muted)}
.legend-item{display:flex;align-items:center;gap:4px}
.edge.highlight{stroke:var(--accent);stroke-width:1.6;stroke-opacity:0.6}
.node circle{fill:#fff;stroke:var(--accent);stroke-width:2;cursor:grab}
.node.meta circle{fill:#eff6ff;stroke:#2563eb}
.node.domain circle{fill:#f0fdf4;stroke:#16a34a}
.node.warn circle{fill:#fffbeb;stroke:#d97706}
.node.selected circle{stroke:#dc2626;stroke-width:4;stroke-dasharray:6 3}
.node text{font-size:12px;font-weight:700;fill:var(--text);text-anchor:middle;dominant-baseline:middle;pointer-events:none}
.detail{padding:14px 16px 18px;overflow:auto;max-height:calc(100vh - 230px);font-size:13px}
.badge{display:inline-block;padding:3px 8px;border-radius:999px;background:var(--accent-soft);color:#1d4ed8;font-size:12px;margin:3px 4px 3px 0}
.badge.gray{background:#f3f4f6;color:#374151}
.badge.green{background:#dcfce7;color:#166534}
.badge.warn{background:#fef3c7;color:#92400e}
.kv{margin:10px 0}
.kv strong{display:block;font-size:12px;color:var(--muted);margin-bottom:3px}
.kv code{background:#f3f4f6;padding:2px 5px;border-radius:6px}
.table{width:100%;border-collapse:collapse;font-size:13px}
.table th,.table td{border-bottom:1px solid var(--border);padding:8px 10px;text-align:left;vertical-align:top}
.notice{margin:12px 0;padding:10px 12px;border-radius:10px;background:#fff7ed;color:#9a3412;font-size:13px}
.footer-panels{display:grid;grid-template-columns:1fr 1fr;gap:14px;padding:0 28px 28px}
.small{font-size:13px;color:var(--muted)}
@media (max-width:1100px){
  .layout{grid-template-columns:1fr}
  .toolbar{grid-template-columns:1fr 1fr}
  .graph-wrap{height:620px}
  .footer-panels{grid-template-columns:1fr}
}
</style>
</head>
<body>
<header>
  <h1>Claude Code Skill 关系图</h1>
  <div class="sub">
    生成时间：<span id="generated"></span>　
    根目录：<code id="root"></code>　
    节点：<span id="nodeCount"></span>　
    关系：<span id="edgeCount"></span>
  </div>
</header>

<section class="toolbar">
  <input id="search" placeholder="搜索 skill 名称、用途、分类……">
  <select id="category"></select>
  <select id="scope"></select>
  <select id="status"></select>
</section>

<main class="layout">
  <aside class="panel">
    <h2>Skill 列表</h2>
    <div id="skillList" class="list"></div>
  </aside>

  <section class="panel">
    <h2>关系网络</h2>
    <div class="graph-wrap">
      <svg id="graph" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Skill 关系图"></svg>
      <button id="zoomReset" class="zoom-reset" onclick="resetZoom()">重置缩放</button>
    </div>
    <div class="legend">
      <span class="legend-item"><svg width="24" height="12"><line x1="2" y1="6" x2="18" y2="6" stroke="#94a3b8" stroke-width="1.5"/><circle cx="21" cy="6" r="3" fill="#94a3b8"/></svg> 上游指向下游</span>
    </div>
  </section>

  <aside class="panel">
    <h2>节点详情</h2>
    <div id="detail" class="detail">点击左侧列表或图中的节点查看详情。</div>
  </aside>
</main>

<section class="footer-panels">
  <section class="panel"><h2>警告</h2><div id="warnings" class="detail"></div></section>
  <section class="panel"><h2>孤立节点</h2><div id="isolated" class="detail"></div></section>
</section>

<script id="skill-data" type="application/json">__DATA_JSON__</script>
<script>
"use strict";
const SVG_NS = "http://www.w3.org/2000/svg";
const DATA = JSON.parse(document.getElementById("skill-data").textContent);
let selected = null;
let posMap = new Map();           // 当前布局位置
let isDragging = false;
let dragArmed = false;             // 按下但未移动（超过阈值才进入 isDragging）
let dragStartX = 0, dragStartY = 0;
let draggedNode = null;
let offsetX = 0, offsetY = 0;
let dragSvg = null;                // 拖拽时的 SVG 引用
let velMap = new Map();            // nodeName → {vx, vy} 所有节点的速度追踪
let lastDragPos = null;            // 上一次拖拽位置 {x, y}，用于差分算速度
let vbX = -20, vbY = -20, vbW = 1240, vbH = 840;  // viewBox 状态
let isPanning = false;             // 平移画布状态
let panStartX = 0, panStartY = 0;  // 平移起始屏幕坐标
let panVbX = 0, panVbY = 0;        // 平移起始 viewBox
let panelDirty = false;            // 侧边栏是否需要刷新

const $ = (id) => document.getElementById(id);

$("generated").textContent = DATA.generated;
$("root").textContent = DATA.root;
$("nodeCount").textContent = DATA.nodes.length;
$("edgeCount").textContent = DATA.edges.length;

function optionList(select, label, values) {
  select.innerHTML = "";
  const all = document.createElement("option");
  all.value = ""; all.textContent = label;
  select.appendChild(all);
  values.forEach((v) => {
    const o = document.createElement("option");
    o.value = v; o.textContent = v;
    select.appendChild(o);
  });
}
optionList($("category"), "全部分类", DATA.categories);
optionList($("scope"), "全部范围", DATA.scopes);
optionList($("status"), "全部状态", DATA.statuses);

function getFilters() {
  return {
    q: $("search").value.trim().toLowerCase(),
    category: $("category").value,
    scope: $("scope").value,
    status: $("status").value,
  };
}

function visibleNodes() {
  const f = getFilters();
  return DATA.nodes.filter((n) => {
    const hay = [n.name, n.title, ...nodeCats(n), n.scope, n.status, n.purpose].join(" ").toLowerCase();
    if (f.q && !hay.includes(f.q)) return false;
    if (f.category && !nodeCats(n).includes(f.category)) return false;
    if (f.scope && n.scope !== f.scope) return false;
    if (f.status && n.status !== f.status) return false;
    return true;
  });
}

function escapeHtml(s) {
  return String(s ?? "")
    .replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;").replaceAll("'", "&#039;");
}

function nodeCats(n) { return n.categories || [n.category || "未分类"]; }
function jaccard(a, b) { const ca = nodeCats(a); const cb = nodeCats(b); const inter = ca.filter(c => cb.includes(c)).length; return inter / (ca.length + cb.length - inter); }
function truncate(s, n) {
  s = String(s ?? "");
  return s.length > n ? s.slice(0, n - 1) + "…" : s;
}

function getMagnified() {
  const set = new Set();
  if (!selected) return set;
  set.add(selected);
  DATA.edges.forEach(e => {
    if (e.source === selected) set.add(e.target);
    if (e.target === selected) set.add(e.source);
  });
  return set;
}

const CAT_COLORS = {
  "元技能": "#2563eb",
  "数学与方法库": "#7c3aed",
  "编码与调试": "#16a34a",
  "测试与质量": "#ea580c",
  "文档与写作": "#0891b2",
  "运维与发布": "#dc2626",
  "研究与发现": "#ca8a04",
  "设计与界面": "#db2777",
  "数据与分析": "#4f46e5",
  "规划与评审": "#059669",
  "MATLAB": "#e7702e",
};
function catColor(cat) { return CAT_COLORS[cat] || "#94a3b8"; }


function drawEnvelopes(svg, nodes) {
  const groups = new Map();
  nodes.forEach(n => {
    const p = posMap.get(n.name);
    if (!p) return;
    nodeCats(n).forEach(cat => {
      if (!groups.has(cat)) groups.set(cat, []);
      groups.get(cat).push({x: p.x, y: p.y, name: n.name});
    });
  });
  svg.querySelectorAll('.envelope').forEach(el => el.remove());
  groups.forEach((pts, cat) => {
    if (pts.length < 2) return;
    const color = catColor(cat);
    const cx = pts.reduce((s, p) => s + p.x, 0) / pts.length;
    const cy = pts.reduce((s, p) => s + p.y, 0) / pts.length;
    const maxDist = Math.max(...pts.map(p => Math.sqrt((p.x - cx) ** 2 + (p.y - cy) ** 2)));
    const r = maxDist + 32;
    const d = `M${cx - r},${cy} A${r},${r} 0 1 0 ${cx + r},${cy} A${r},${r} 0 1 0 ${cx - r},${cy} Z`;
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("class", "envelope");
    path.setAttribute("d", d);
    path.setAttribute("fill", color);
    path.setAttribute("fill-opacity", "0.05");
    path.setAttribute("stroke", color);
    path.setAttribute("stroke-dasharray", "5 5");
    path.setAttribute("stroke-width", "1.2");
    path.setAttribute("stroke-opacity", "0.5");
    path.setAttribute("pointer-events", "none");
    svg.insertBefore(path, svg.firstChild);
    // 分类名称标签
    const fontSize = Math.max(11, Math.min(Math.round(r / 5), 26));
    const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
    text.setAttribute("class", "envelope");
    text.setAttribute("x", cx);
    text.setAttribute("y", cy);
    text.setAttribute("text-anchor", "middle");
    text.setAttribute("dominant-baseline", "central");
    text.setAttribute("fill", color);
    text.setAttribute("fill-opacity", "0.35");
    text.setAttribute("font-size", fontSize);
    text.setAttribute("font-weight", "600");
    text.setAttribute("pointer-events", "none");
    text.textContent = cat;
    svg.insertBefore(text, svg.firstChild);
  });
}

function renderList(nodes) {
  const box = $("skillList");
  box.innerHTML = "";
  nodes.forEach((n) => {
    const div = document.createElement("div");
    div.className = "item" + (selected === n.name ? " active" : "");
    div.innerHTML =
      '<div class="name">/' + escapeHtml(n.name) + '</div>' +
      '<div class="meta">' + escapeHtml(nodeCats(n).join(", ")) + ' · ' +
      escapeHtml(n.scope || "unknown") + ' · ' + escapeHtml(n.status || "") + '</div>' +
      '<div class="meta">' + escapeHtml(truncate(n.purpose || "", 74)) + '</div>';
    div.onclick = () => { selected = n.name; panelDirty = true; };
    box.appendChild(div);
  });
}

function relationRows(n) {
  const rel = n.relations || {};
  const rows = [];
  Object.entries(DATA.relationLabels).forEach(([key, label]) => {
    const arr = rel[key] || [];
    if (arr.length) {
      rows.push('<tr><td>' + escapeHtml(label) + '</td><td>' +
        arr.map((x) => '<code>/' + escapeHtml(x) + '</code>').join(' ') +
        '</td></tr>');
    }
  });
  if (!rows.length) return '<div class="small">暂无显式关系。</div>';
  return '<table class="table"><tbody>' + rows.join("") + '</tbody></table>';
}

function renderDetail() {
  const node = DATA.nodes.find((n) => n.name === selected);
  if (!node) {
    $("detail").innerHTML = "点击左侧列表或图中的节点查看详情。";
    return;
  }
  const notes = (node.notes && node.notes.length)
    ? '<ul>' + node.notes.map((x) => '<li>' + escapeHtml(x) + '</li>').join("") + '</ul>'
    : '<div class="small">无备注。</div>';
  $("detail").innerHTML =
    '<h3>/' + escapeHtml(node.name) + '</h3>' +
    '<div>' +
      '<span class="badge">' + escapeHtml(nodeCats(node).join(", ")) + '</span>' +
      '<span class="badge gray">' + escapeHtml(node.scope || "unknown") + '</span>' +
      '<span class="badge green">' + escapeHtml(node.status || "unknown") + '</span>' +
      '<span class="badge gray">v' + escapeHtml(node.version || "") + '</span>' +
    '</div>' +
    '<div class="kv"><strong>标题</strong>' + escapeHtml(node.title || "") + '</div>' +
    '<div class="kv"><strong>用途</strong>' + escapeHtml(node.purpose || "") + '</div>' +
    '<div class="kv"><strong>更新时间</strong>' + escapeHtml(node.updated || "") + '</div>' +
    '<div class="kv"><strong>路径</strong><code>' + escapeHtml(node._dir || "") + '</code></div>' +
    '<div class="kv"><strong>Metadata</strong><code>' + escapeHtml(node._path || "") + '</code></div>' +
    '<div class="kv"><strong>关系</strong>' + relationRows(node) + '</div>' +
    '<div class="kv"><strong>备注</strong>' + notes + '</div>';
}

function renderWarnings() {
  const box = $("warnings");
  if (!DATA.warnings.length) {
    box.innerHTML = '<span class="badge green">没有发现关系警告</span>'; return;
  }
  box.innerHTML = DATA.warnings.map((w) => '<div class="notice">' + escapeHtml(w) + '</div>').join("");
}

function renderIsolated() {
  const box = $("isolated");
  if (!DATA.isolated.length) {
    box.innerHTML = '<span class="badge green">没有孤立节点</span>'; return;
  }
  box.innerHTML = DATA.isolated.map((n) => '<span class="badge warn">/' + escapeHtml(n) + '</span>').join("");
}

function svgEl(tag) { return document.createElementNS(SVG_NS, tag); }

// 简易力导向布局
function layout(nodes, edges, w, h) {
  const N = nodes.length;
  if (N === 0) return new Map();
  const cx = w / 2, cy = h / 2;
  const R = N <= 1 ? 0 : Math.min(cx, cy) - 90;
  const pos = new Map();
  // 按主分类分组，同分类节点聚集在同一扇区
  const groups = new Map();
  nodes.forEach((n) => {
    const cat = nodeCats(n)[0];
    if (!groups.has(cat)) groups.set(cat, []);
    groups.get(cat).push(n);
  });
  const groupList = [...groups.values()];
  let angleStart = -Math.PI / 2;
  const totalAngle = Math.PI * 2;
  groupList.forEach((group) => {
    const sectorSize = (group.length / N) * totalAngle;
    group.forEach((n, j) => {
      const a = group.length === 1
        ? angleStart + sectorSize / 2
        : angleStart + (sectorSize * (j + 0.5)) / group.length;
      pos.set(n.name, { x: cx + Math.cos(a) * R, y: cy + Math.sin(a) * R });
    });
    angleStart += sectorSize;
  });
  if (N <= 2) return pos;

  const idx = new Map(nodes.map((n, i) => [n.name, i]));
  const arr = nodes.map((n) => ({ ...pos.get(n.name) }));
  const links = edges
    .map((e) => [idx.get(e.source), idx.get(e.target)])
    .filter(([a, b]) => a != null && b != null);

  const REPULSE = 3000, SPRING = 0.006, IDEAL = 100, DAMP = 0.85;
  const vel = arr.map(() => ({ x: 0, y: 0 }));
  for (let step = 0; step < 220; step++) {
    // 斥力
    for (let i = 0; i < N; i++) {
      for (let j = i + 1; j < N; j++) {
        const dx = arr[i].x - arr[j].x, dy = arr[i].y - arr[j].y;
        const d2 = dx * dx + dy * dy + 0.01;
        const f = REPULSE / d2;
        const d = Math.sqrt(d2);
        const fx = (dx / d) * f, fy = (dy / d) * f;
        vel[i].x += fx; vel[i].y += fy;
        vel[j].x -= fx; vel[j].y -= fy;
      }
    }
    // 引力（异类边弹力减弱）
    for (const [a, b] of links) {
      const dx = arr[b].x - arr[a].x, dy = arr[b].y - arr[a].y;
      const d = Math.sqrt(dx * dx + dy * dy) + 0.01;
      const k = jaccard(nodes[a], nodes[b]) ? SPRING : SPRING * 0.25;
      const f = (d - IDEAL) * k;
      const fx = (dx / d) * f, fy = (dy / d) * f;
      vel[a].x += fx; vel[a].y += fy;
      vel[b].x -= fx; vel[b].y -= fy;
    }
    // 向心力
    for (let i = 0; i < N; i++) {
      vel[i].x += (cx - arr[i].x) * 0.005;
      vel[i].y += (cy - arr[i].y) * 0.005;
      vel[i].x *= DAMP; vel[i].y *= DAMP;
      arr[i].x += vel[i].x;
      arr[i].y += vel[i].y;
      arr[i].x = Math.max(80, Math.min(w - 80, arr[i].x));
      arr[i].y = Math.max(80, Math.min(h - 80, arr[i].y));
    }
  }
  nodes.forEach((n, i) => pos.set(n.name, arr[i]));
  return pos;
}

function startDrag(evt, nodeName, svg) {
  isDragging = true;
  draggedNode = nodeName;
  dragSvg = svg;
  velMap.clear();
  const p = posMap.get(nodeName);
  const pt = svg.createSVGPoint();
  pt.x = evt.clientX; pt.y = evt.clientY;
  const svgP = pt.matrixTransform(svg.getScreenCTM().inverse());
  offsetX = svgP.x - p.x;
  offsetY = svgP.y - p.y;
  lastDragPos = {x: p.x, y: p.y, t: performance.now()};
  evt.currentTarget.style.cursor = "grabbing";
  svg.setPointerCapture(evt.pointerId);
  evt.stopPropagation();
}

// 以下绑定在 SVG 元素上，全局响应 pointermove/pointerup
function onSvgDrag(evt) {
  if (isPanning) {
    evt.preventDefault();
    const dx = (evt.clientX - panStartX) * vbW / dragSvg.clientWidth;
    const dy = (evt.clientY - panStartY) * vbH / dragSvg.clientHeight;
    vbX = panVbX - dx;
    vbY = panVbY - dy;
    updateViewBox();
    return;
  }
  if (!isDragging || !draggedNode) return;
  evt.preventDefault();
  const svg = dragSvg;
  const pt = svg.createSVGPoint();
  pt.x = evt.clientX; pt.y = evt.clientY;
  const svgP = pt.matrixTransform(svg.getScreenCTM().inverse());
  const nx = svgP.x - offsetX, ny = svgP.y - offsetY;
  posMap.set(draggedNode, {x: nx, y: ny});
  // 差分计算拖拽节点即时速度
  const now = performance.now();
  const dt = Math.max((now - lastDragPos.t) / 16.67, 0.3);
  velMap.set(draggedNode, {vx: (nx - lastDragPos.x) / dt * 0.35, vy: (ny - lastDragPos.y) / dt * 0.35});
  lastDragPos = {x: nx, y: ny, t: now};
  // 碰撞和渲染统一由 physicsTick 驱动，保证帧率一致
}

function onSvgDragEnd(evt) {
  if (isPanning) {
    isPanning = false;
    dragSvg.releasePointerCapture(evt.pointerId);
    dragSvg.style.cursor = "grab";
    dragSvg = null;
    return;
  }
  if (!isDragging) return;
  if (dragSvg && draggedNode) {
    dragSvg.releasePointerCapture(evt.pointerId);
    const g = dragSvg.querySelector('[data-name="' + draggedNode + '"]');
    if (g) g.style.cursor = "grab";
  }
  isDragging = false;
  lastDragPos = null;
  draggedNode = null;
  dragSvg = null;
  panelDirty = true;
}

// 碰撞检测：纯斥力迭代，避免节点重叠
function resolveCollisions() {
  const nodes = visibleNodes();
  if (nodes.length < 2) return;
  const N = nodes.length;
  const arr = nodes.map((n) => ({...posMap.get(n.name)}));
  const MIN_DIST = 20;        // 最小间距（2 × 半径 + 14px padding）
  const svgW = 1200, svgH = 800;

  for (let step = 0; step < 80; step++) {
    let maxOverlap = 0;
    for (let i = 0; i < N; i++) {
      for (let j = i + 1; j < N; j++) {
        const dx = arr[i].x - arr[j].x;
        const dy = arr[i].y - arr[j].y;
        const d = Math.sqrt(dx * dx + dy * dy) + 0.001;
        if (d < MIN_DIST) {
          const overlap = MIN_DIST - d;
          maxOverlap = Math.max(maxOverlap, overlap);
          const fx = (dx / d) * overlap * 0.5;
          const fy = (dy / d) * overlap * 0.5;
          arr[i].x += fx;
          arr[i].y += fy;
          arr[j].x -= fx;
          arr[j].y -= fy;
        }
      }
    }
    // 边界约束
    for (let i = 0; i < N; i++) {
      arr[i].x = Math.max(80, Math.min(svgW - 80, arr[i].x));
      arr[i].y = Math.max(80, Math.min(svgH - 80, arr[i].y));
    }
    // 边弹簧：拉向理想距离（异类边弹力减弱）
    const IDEAL = 100, SPRING_K = 0.005;
    const visEdges = DATA.edges.filter(e => nodes.some(n => n.name === e.source) && nodes.some(n => n.name === e.target));
    for (const e of visEdges) {
      const ai = nodes.findIndex(n => n.name === e.source);
      const bi = nodes.findIndex(n => n.name === e.target);
      if (ai < 0 || bi < 0) continue;
      const a = arr[ai], b = arr[bi];
      const dx = b.x - a.x, dy = b.y - a.y;
      const d = Math.sqrt(dx * dx + dy * dy) + 0.001;
      const k = jaccard(nodes[ai], nodes[bi]) ? SPRING_K : SPRING_K * 0.25;
      const f = (d - IDEAL) * k;
      a.x += (dx / d) * f;
      a.y += (dy / d) * f;
      b.x -= (dx / d) * f;
      b.y -= (dy / d) * f;
    }
    if (maxOverlap < 0.5) break;
  }

  nodes.forEach((n, i) => posMap.set(n.name, arr[i]));
}

// 拖拽时实时碰撞：只处理被拖拽节点推开周围节点，不进行全量 O(N²)
function resolveDragCollisions() {
  if (!draggedNode) return;
  const nodes = visibleNodes();
  if (nodes.length < 2) return;
  const dragPos = posMap.get(draggedNode);
  if (!dragPos) return;
  const MIN_DIST = 20;
  const svgW = 1200, svgH = 800;

  const IDEAL = 100, SPRING = 0.005;
  const visEdges = DATA.edges.filter(e => nodes.some(n => n.name === e.source) && nodes.some(n => n.name === e.target));
  // 推拉交错：每步同时做碰撞推开 + 弹簧拉回
  for (let step = 0; step < 10; step++) {
    // a) 被拖节点推开周围节点（冻结节点抵抗）
    for (const n of nodes) {
      if (n.name === draggedNode) continue;
      if ((selected ===n.name)) continue;
      const p = posMap.get(n.name);
      if (!p) continue;
      const dx = dragPos.x - p.x;
      const dy = dragPos.y - p.y;
      const d = Math.sqrt(dx * dx + dy * dy) + 0.001;
      if (d < MIN_DIST) {
        const overlap = MIN_DIST - d;
        const fx = (dx / d) * overlap;
        const fy = (dy / d) * overlap;
        p.x -= fx;
        p.y -= fy;
        p.x = Math.max(80, Math.min(svgW - 80, p.x));
        p.y = Math.max(80, Math.min(svgH - 80, p.y));
        const prev = velMap.get(n.name) || {vx: 0, vy: 0};
        velMap.set(n.name, {vx: prev.vx - fx * 0.3, vy: prev.vy - fy * 0.3});
      }
    }
    // b) 全量边弹簧（每步都拉，异类边减弱，跳过被拖节点）
    for (const e of visEdges) {
      const a = posMap.get(e.source), b = posMap.get(e.target);
      if (!a || !b) continue;
      const dx = b.x - a.x, dy = b.y - a.y;
      const d = Math.sqrt(dx * dx + dy * dy) + 0.001;
      const srcNode = nodes.find(n => n.name === e.source);
      const tgtNode = nodes.find(n => n.name === e.target);
      const k = (srcNode && tgtNode && jaccard(srcNode, tgtNode)) ? SPRING : SPRING * 0.25;
      const f = (d - IDEAL) * k;
      const srcIsDrag = e.source === draggedNode;
      const tgtIsDrag = e.target === draggedNode;
      if (!srcIsDrag && !(selected ===e.source)) { a.x += (dx / d) * f * 0.5; a.y += (dy / d) * f * 0.5; }
      if (!tgtIsDrag && !(selected ===e.target)) { b.x -= (dx / d) * f * 0.5; b.y -= (dy / d) * f * 0.5; }
    }
    // c) 全量节点对互推（最后几步）
    if (step >= 7) {
      for (let i = 0; i < nodes.length; i++) {
        if (nodes[i].name === draggedNode) continue;
        if ((selected ===nodes[i].name)) continue;
        const a = posMap.get(nodes[i].name);
        if (!a) continue;
        for (let j = i + 1; j < nodes.length; j++) {
          if (nodes[j].name === draggedNode) continue;
          if ((selected ===nodes[j].name)) continue;
          const b = posMap.get(nodes[j].name);
          if (!b) continue;
          const dx2 = a.x - b.x, dy2 = a.y - b.y;
          const d2 = Math.sqrt(dx2 * dx2 + dy2 * dy2) + 0.001;
          if (d2 < MIN_DIST) {
            const overlap = MIN_DIST - d2;
            const fx = (dx2 / d2) * overlap * 0.5;
            const fy = (dy2 / d2) * overlap * 0.5;
            a.x += fx; a.y += fy;
            b.x -= fx; b.y -= fy;
            a.x = Math.max(80, Math.min(svgW - 80, a.x));
            a.y = Math.max(80, Math.min(svgH - 80, a.y));
            b.x = Math.max(80, Math.min(svgW - 80, b.x));
            b.y = Math.max(80, Math.min(svgH - 80, b.y));
          }
        }
      }
    }
  }
  // 硬约束：最终确保拖拽节点不与任何节点重叠
  for (const n of nodes) {
    if (n.name === draggedNode) continue;
    const p = posMap.get(n.name);
    if (!p) continue;
    const dx = dragPos.x - p.x, dy = dragPos.y - p.y;
    const d = Math.sqrt(dx * dx + dy * dy) + 0.001;
    if (d < MIN_DIST) {
      p.x = dragPos.x - (dx / d) * MIN_DIST;
      p.y = dragPos.y - (dy / d) * MIN_DIST;
    }
  }
  // 统一 Jaccard 力（引力+斥力连续混合）
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const a = posMap.get(nodes[i].name);
      const b = posMap.get(nodes[j].name);
      if (!a || !b) continue;
      const dx = b.x - a.x, dy = b.y - a.y;
      const d2 = dx * dx + dy * dy + 1;
      const d = Math.sqrt(d2);
      const sim = jaccard(nodes[i], nodes[j]);
      const f = sim * (d2 * 0.00003) - (1 - sim) * (6000 / d2);
      if (!(selected ===nodes[i].name)) { a.x += (dx / d) * f; a.y += (dy / d) * f; }
      if (!(selected ===nodes[j].name)) { b.x -= (dx / d) * f; b.y -= (dy / d) * f; }
    }
  }
}

// 持续物理循环：固定时间步长 + 累积器，保证物理一致性
let lastPhysTime = 0;
let frameSkip = false;
function physicsTick(now) {
  requestAnimationFrame(physicsTick);
  const nodes = visibleNodes();
  if (!nodes.length) return;

  // 固定时间步长 1/60s，累积追赶
  const FIXED_DT = 1 / 60;
  if (!lastPhysTime) lastPhysTime = now;
  let acc = Math.min((now - lastPhysTime) / 1000, 0.1);  // cap 100ms
  lastPhysTime = now;
  let physRan = false;

  while (acc >= FIXED_DT) {
    acc -= FIXED_DT;
    physRan = true;
    // 拖拽碰撞
    if (isDragging) resolveDragCollisions();

    // 随机游走
    const RW = 0.04;
    for (const n of nodes) {
      if (isDragging && n.name === draggedNode) continue;
      if ((selected ===n.name)) continue;
      let v = velMap.get(n.name);
      if (!v) { v = {vx: 0, vy: 0}; velMap.set(n.name, v); }
      v.vx += (Math.random() - 0.5) * RW;
      v.vy += (Math.random() - 0.5) * RW;
    }

    // 半隐式 Euler：先摩擦，再位移
    for (const n of nodes) {
      if (isDragging && n.name === draggedNode) continue;
      if ((selected ===n.name)) continue;
      const v = velMap.get(n.name);
      const p = posMap.get(n.name);
      if (!p || !v) continue;
      v.vx *= 0.95; v.vy *= 0.95;
      p.x += v.vx; p.y += v.vy;
      if (p.x < 80) { p.x = 80; v.vx = Math.abs(v.vx) * 0.4; }
      if (p.x > 1200 - 80) { p.x = 1200 - 80; v.vx = -Math.abs(v.vx) * 0.4; }
      if (p.y < 80) { p.y = 80; v.vy = Math.abs(v.vy) * 0.4; }
      if (p.y > 800 - 80) { p.y = 800 - 80; v.vy = -Math.abs(v.vy) * 0.4; }
    }

    // 清理低速
    for (const [k, v] of velMap) {
      if (Math.abs(v.vx) < 0.02 && Math.abs(v.vy) < 0.02) velMap.delete(k);
    }

    // 碰撞 + 弹簧 + 边-节点排斥（每物理步都跑）
    const MIN_DIST = 20;
    const arr = nodes.map(n => { const pp = posMap.get(n.name); return pp ? {x: pp.x, y: pp.y} : null; });
    for (let iter = 0; iter < 2; iter++) {
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          if (isDragging && (nodes[i].name === draggedNode || nodes[j].name === draggedNode)) continue;
          const a = arr[i], b = arr[j];
          if (!a || !b) continue;
          const dx = a.x - b.x, dy = a.y - b.y;
          const d = Math.sqrt(dx * dx + dy * dy) + 0.001;
          const frozenA = (selected ===nodes[i].name);
          const frozenB = (selected ===nodes[j].name);
          if (frozenA && frozenB) continue;
          if (d < MIN_DIST) {
            const overlap = MIN_DIST - d;
            const fx = (dx / d) * overlap * (frozenA || frozenB ? 1 : 0.5);
            const fy = (dy / d) * overlap * (frozenA || frozenB ? 1 : 0.5);
            if (!frozenA) { a.x += fx; a.y += fy; }
            if (!frozenB) { b.x -= fx; b.y -= fy; }
            if (!frozenA) { const va = velMap.get(nodes[i].name) || {vx: 0, vy: 0}; velMap.set(nodes[i].name, {vx: va.vx + fx * 0.2, vy: va.vy + fy * 0.2}); }
            if (!frozenB) { const vb = velMap.get(nodes[j].name) || {vx: 0, vy: 0}; velMap.set(nodes[j].name, {vx: vb.vx - fx * 0.2, vy: vb.vy - fy * 0.2}); }
          }
        }
      }
      for (let i = 0; i < nodes.length; i++) {
        if (!arr[i]) continue;
        arr[i].x = Math.max(80, Math.min(1120, arr[i].x));
        arr[i].y = Math.max(80, Math.min(720, arr[i].y));
      }
    }

    // 边弹簧（异类边弹力减弱）
    const IDEAL = 100, SPRING_K = 0.005;
    const visEdges = DATA.edges.filter(e => nodes.some(n => n.name === e.source) && nodes.some(n => n.name === e.target));
    for (const e of visEdges) {
      const ai = nodes.findIndex(n => n.name === e.source);
      const bi = nodes.findIndex(n => n.name === e.target);
      if (ai < 0 || bi < 0) continue;
      const a = arr[ai], b = arr[bi];
      if (!a || !b) continue;
      const dx = b.x - a.x, dy = b.y - a.y;
      const d = Math.sqrt(dx * dx + dy * dy) + 0.001;
      const k = jaccard(nodes[ai], nodes[bi]) ? SPRING_K : SPRING_K * 0.25;
      const f = (d - IDEAL) * k;
      if (!(selected ===nodes[ai].name)) { a.x += (dx / d) * f; a.y += (dy / d) * f; }
      if (!(selected ===nodes[bi].name)) { b.x -= (dx / d) * f; b.y -= (dy / d) * f; }
    }

    // 统一 Jaccard 力（sim=1纯引力, sim=0纯斥力, 中间连续混合）
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const a = arr[i], b = arr[j];
        if (!a || !b) continue;
        const dx = b.x - a.x, dy = b.y - a.y;
        const d2 = dx * dx + dy * dy + 1;
        const d = Math.sqrt(d2);
        const sim = jaccard(nodes[i], nodes[j]);
        const f = sim * (d2 * 0.00003) - (1 - sim) * (6000 / d2);
        if (!(selected ===nodes[i].name)) { a.x += (dx / d) * f; a.y += (dy / d) * f; }
        if (!(selected ===nodes[j].name)) { b.x -= (dx / d) * f; b.y -= (dy / d) * f; }
      }
    }

    nodes.forEach((n, i) => { if (arr[i]) posMap.set(n.name, arr[i]); });
  }

  // 渲染：拖拽或有动能时 60fps，静止时 30fps
  if (!physRan) return;
  frameSkip = !frameSkip;
  const hasEnergy = !isDragging && [...velMap.values()].some(v => Math.abs(v.vx) > 0.04 || Math.abs(v.vy) > 0.04);
  if (isDragging || hasEnergy || !frameSkip) {
    renderGraph(nodes);
    if (panelDirty) { panelDirty = false; requestAnimationFrame(render); }
  }
}

let svgCache = null;  // { edgeLines: Map, nodeGroups: Map, nodeCircles: Map, lastKey: "" }

function updateViewBox() {
  const svg = $("graph");
  svg.setAttribute("viewBox", `${vbX} ${vbY} ${vbW} ${vbH}`);
  const btn = $("zoomReset");
  const isDefault = Math.abs(vbW - 1240) < 10 && Math.abs(vbH - 840) < 10;
  btn.classList.toggle("visible", !isDefault);
}
function resetZoom() { vbX = -20; vbY = -20; vbW = 1240; vbH = 840; updateViewBox(); }

function renderGraph(nodes) {
  const svg = $("graph");
  svg.setAttribute("viewBox", `${vbX} ${vbY} ${vbW} ${vbH}`);
  svg.setAttribute("preserveAspectRatio", "xMidYMid meet");

  if (!nodes.length) {
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    svgCache = null;
    const t = svgEl("text");
    t.setAttribute("x", 600); t.setAttribute("y", 400);
    t.setAttribute("text-anchor", "middle"); t.setAttribute("fill", "#94a3b8");
    t.textContent = "没有匹配的 skill。";
    svg.appendChild(t);
    return;
  }

  const visible = new Set(nodes.map((n) => n.name));
  const edges = DATA.edges.filter((e) => visible.has(e.source) && visible.has(e.target));
  const key = nodes.map(n => n.name).sort().join(",");

  // 初始化位置
  if (posMap.size === 0 || posMap.size !== nodes.length) {
    posMap = layout(nodes, edges, 1200, 800);
  }

  // 节点集变了 → 全量重建；否则只更新位置
  if (!svgCache || svgCache.lastKey !== key) {
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    svgCache = { edgeLines: new Map(), nodeGroups: new Map(), nodeCircles: new Map(), lastKey: key };

    const defs = svgEl("defs");
    const marker = svgEl("marker");
    marker.setAttribute("id", "arrow");
    marker.setAttribute("markerWidth", "6"); marker.setAttribute("markerHeight", "6");
    marker.setAttribute("refX", "5"); marker.setAttribute("refY", "3");
    marker.setAttribute("orient", "auto"); marker.setAttribute("markerUnits", "strokeWidth");
    const ap = svgEl("path");
    ap.setAttribute("d", "M0,0 L0,6 L9,3 z"); ap.setAttribute("fill", "#94a3b8");
    marker.appendChild(ap); defs.appendChild(marker);
    svg.appendChild(defs);

    edges.forEach((e) => {
      const ek = e.source + "|||" + e.target;
      const line = svgEl("line"); line.setAttribute("class", "edge");
      svg.appendChild(line);
      svgCache.edgeLines.set(ek, line);
    });

    nodes.forEach((n) => {
      const g = svgEl("g"); g.setAttribute("data-name", n.name);
      g.style.cursor = "grab";
      g.addEventListener("pointerdown", (evt) => {
        selected = n.name; panelDirty = true;
        startDrag(evt, n.name, svg);
      });
      g.addEventListener("click", (evt) => {
        if (!isDragging) { selected = n.name; panelDirty = true; }
      });
      const c = svgEl("circle");
      c.setAttribute("r", nodeCats(n).includes("元技能") ? "6" : "5");
      g.appendChild(c);
      const t = svgEl("text");
      const label = n.title || ("/" + n.name);
      t.textContent = label.length > 8 ? label.slice(0, 7) + "…" : label;
      g.appendChild(t);
      const ti = svgEl("title");
      ti.textContent = (n.title || "") + "\n/" + n.name + "\n" + (n.purpose || "");
      g.appendChild(ti);
      svg.appendChild(g);
      svgCache.nodeGroups.set(n.name, g);
      svgCache.nodeCircles.set(n.name, c);
    });
  }

  // 更新边位置
  svgCache.edgeLines.forEach((line, ek) => {
    const [src, tgt] = ek.split("|||");
    const a = posMap.get(src), b = posMap.get(tgt);
    if (!a || !b) { line.setAttribute("visibility", "hidden"); return; }
    line.setAttribute("visibility", "visible");
    const edx = b.x - a.x, edy = b.y - a.y;
    const edist = Math.sqrt(edx * edx + edy * edy) || 1;
    const sNode = nodes.find(n => n.name === src);
    const tNode = nodes.find(n => n.name === tgt);
    const sR = (sNode && nodeCats(sNode).includes("元技能") ? 6 : 5) + 1;
    const tR = (tNode && nodeCats(tNode).includes("元技能") ? 6 : 5) + 2;
    line.setAttribute("x1", a.x + (edx / edist) * sR);
    line.setAttribute("y1", a.y + (edy / edist) * sR);
    line.setAttribute("x2", b.x - (edx / edist) * tR);
    line.setAttribute("y2", b.y - (edy / edist) * tR);
    const hl = selected === src || selected === tgt;
    line.setAttribute("class", "edge" + (hl ? " highlight" : ""));
  });

  // 更新节点位置
  const magnified = getMagnified();
  svgCache.nodeGroups.forEach((g, name) => {
    const p = posMap.get(name);
    const n = nodes.find(nn => nn.name === name);
    if (!p || !n) { g.setAttribute("visibility", "hidden"); return; }
    g.setAttribute("visibility", "visible");
    g.setAttribute("transform", `translate(${p.x},${p.y})`);
    const isMeta = nodeCats(n).includes("元技能");
    const isWarn = DATA.isolated.includes(name);
    g.setAttribute("class", "node " + (isMeta ? "meta " : "domain ") + (isWarn ? "warn " : "") + (selected === name ? "selected" : ""));
    // 半径：选中 2×，关联 1.5×
    const baseR = nodeCats(n).includes("元技能") ? 6 : 5;
    const mag = magnified.has(name);
    const isSel = selected === name;
    const r = isSel ? baseR * 4 : (mag ? Math.round(baseR * 1.5) : baseR);
    const c = svgCache.nodeCircles.get(name);
    if (c) c.setAttribute("r", r);
    // 文本：仅 magnified 节点显示
    const t = g.querySelector('text');
    if (t) {
      if (mag) {
        const label = n.title || ("/" + n.name);
        t.textContent = label;
        t.setAttribute("visibility", "visible");
        if (isSel) t.setAttribute("font-size", "14");
        else t.setAttribute("font-size", "12");
      } else {
        t.setAttribute("visibility", "hidden");
      }
    }
  });
  drawEnvelopes(svg, nodes);
}

function render() {
  const nodes = visibleNodes();
  if (selected && !nodes.some((n) => n.name === selected)) selected = null;
  renderList(nodes);
  renderGraph(nodes);
  renderDetail();
  renderWarnings();
  renderIsolated();
}

["search", "category", "scope", "status"].forEach((id) => {
  $(id).addEventListener("input", render);
  $(id).addEventListener("change", render);
});

// SVG 层级拖拽事件（全局捕获，快速移动不丢节点）
const svgElm = $("graph");
svgElm.addEventListener("pointerdown", (evt) => {
  // 点击 SVG 空白区域 → 平移画布（不干扰节点拖拽）
  if (isDragging) return;
  if (evt.target === svgElm || evt.target.tagName === "line" || evt.target.classList.contains("envelope")) {
    isPanning = true;
    dragSvg = svgElm;
    panStartX = evt.clientX;
    panStartY = evt.clientY;
    panVbX = vbX;
    panVbY = vbY;
    svgElm.style.cursor = "grabbing";
    svgElm.setPointerCapture(evt.pointerId);
    evt.stopPropagation();
  }
});
svgElm.addEventListener("pointermove", onSvgDrag);
svgElm.addEventListener("pointerup", onSvgDragEnd);
svgElm.addEventListener("pointercancel", onSvgDragEnd);
svgElm.addEventListener("contextmenu", (evt) => {
  evt.preventDefault();
  selected = null;
  panelDirty = true;
});
svgElm.addEventListener("wheel", (evt) => {
  evt.preventDefault();
  const pt = svgElm.createSVGPoint();
  pt.x = evt.clientX; pt.y = evt.clientY;
  const svgP = pt.matrixTransform(svgElm.getScreenCTM().inverse());
  const mx = svgP.x, my = svgP.y;
  const scale = evt.deltaY > 0 ? 1.15 : 0.87;
  const nw = vbW * scale, nh = vbH * scale;
  if (nw < 200 || nw > 4000) return;
  const rx = (mx - vbX) / vbW, ry = (my - vbY) / vbH;
  vbX = mx - rx * nw; vbY = my - ry * nh;
  vbW = nw; vbH = nh;
  updateViewBox();
}, {passive: false});

render();
requestAnimationFrame(physicsTick);
</script>
</body>
</html>
"""

def safe_json_for_script_tag(obj) -> str:
    """把 JSON 安全地塞进 <script type="application/json"> 里。"""
    s = json.dumps(obj, ensure_ascii=False)
    return s.replace("</", "<\\/").replace("<!--", "<\\!--").replace("-->", "--\\>")


def generate_html(root: Path, metas: List[Dict[str, Any]], warnings: List[str]) -> str:
    edges, edge_warnings = build_edges(metas)
    all_warnings = warnings + edge_warnings
    isolated = detect_isolated(metas, edges)

    cat_set = set()
    for m in metas:
        for c in m.get("categories", [m.get("category", "未分类")]):
            cat_set.add(c)
    categories = [c for c in CATEGORY_ORDER_ZH if c in cat_set]
    for c in sorted(cat_set):
        if c not in categories:
            categories.append(c)

    scopes = sorted({str(m.get("scope", "unknown")) for m in metas})
    statuses = sorted({str(m.get("status", "unknown")) for m in metas})

    data = {
        "generated": today(),
        "root": str(root),
        "nodes": metas,
        "edges": edges,
        "warnings": all_warnings,
        "isolated": isolated,
        "categories": categories,
        "scopes": scopes,
        "statuses": statuses,
        "relationLabels": RELATION_LABELS_ZH,
    }

    return HTML_TEMPLATE.replace("__DATA_JSON__", safe_json_for_script_tag(data))


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="生成 Claude Code 本地 skill 的中文版 HTML 关系图。")
    p.add_argument("--root", default=str(Path.home() / ".claude" / "skills"))
    p.add_argument("--out", default=None)
    p.add_argument("--overwrite-meta", action="store_true")
    p.add_argument("--init-meta-only", action="store_true")
    p.add_argument("--graph-only", action="store_true")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(os.path.expanduser(args.root)).resolve()
    out_path = Path(os.path.expanduser(args.out)).resolve() if args.out else root / "SKILL_GRAPH.html"

    if not root.exists():
        raise SystemExit(f"Skills 根目录不存在：{root}")

    if not args.graph_only:
        created, preserved = ensure_meta_files(root, overwrite=args.overwrite_meta)
        print(f"创建 metadata 文件：{len(created)}")
        print(f"保留已有 metadata 文件：{len(preserved)}")
        for path in created:
            print(f"  + {path}")

    if args.init_meta_only:
        return

    metas, warnings = load_all_metadata(root)
    html_doc = generate_html(root, metas, warnings)
    out_path.write_text(html_doc, encoding="utf-8")
    print(f"已生成 HTML 图：{out_path}")
    print(f"包含 skill 数量：{len(metas)}")


if __name__ == "__main__":
    main()