---
name: skill-graph
description: Generate Chinese HTML relationship maps for local Claude Code skills, create or maintain skill.meta.yaml files, and visualize how skills cooperate. Use when the user wants a visual skill graph, metadata health check, relationship map, or Chinese HTML overview of local skills.
argument-hint: "[skills-root-or-graph-task]"
disable-model-invocation: true
---

# Skill Graph

Use this skill to maintain a Chinese HTML relationship graph for local Claude Code skills.

This skill has two responsibilities:

```text
1. Ensure each local skill has skill.meta.yaml metadata.
2. Generate a Chinese single-file HTML graph from that metadata.
```

This skill is not the routing layer. Routing and taxonomy decisions belong to `/skill-index`.

The graph visualization physics and rendering follow rules defined in `/force-graph-physics`. All modifications to `generate_skill_graph_html.py` must consult that skill for optimization patterns, anti-patterns, and troubleshooting.

## Use when

Use this skill when the user asks to:

- Generate a visual graph of local skills.
- Create or update `skill.meta.yaml` for every skill.
- Generate a Chinese HTML skill relationship map.
- See how `/find-local-skills`, `/find-skills`, `/skill-distiller`, `/skill-index`, `/skill-graph`, and domain skills cooperate.
- Detect isolated skills.
- Detect broken relationships.
- Inspect metadata health.
- Track how the skill system evolves over time.

## Do not use when

Do not use this skill when:

- The user wants to decide which skill should handle a task. Use `/skill-index`.
- The user wants to inspect actual installed skills without graphing. Use `/find-local-skills`.
- The user wants to create or refactor a single skill from experience. Use `/skill-distiller`.
- The user wants to find external skills. Use `/find-skills`.
- The user only needs a simple text list.

## Expected directory structure

Personal skills:

```bash
~/.claude/skills/<skill-name>/SKILL.md
~/.claude/skills/<skill-name>/skill.meta.yaml
```

This skill itself should live at:

```bash
~/.claude/skills/skill-graph/SKILL.md
```

The command should be:

```text
/skill-graph
```

Do not create nested category folders under `skills/`.

Correct:

```bash
~/.claude/skills/skill-distiller/SKILL.md
~/.claude/skills/skill-index/SKILL.md
~/.claude/skills/skill-graph/SKILL.md
```

Incorrect:

```bash
~/.claude/skills/meta/skill-distiller/SKILL.md
~/.claude/skills/meta/skill-graph/SKILL.md
```

## Metadata file

Each skill should have a metadata file:

```bash
skill.meta.yaml
```

Minimal example:

```yaml
name: skill-name
title: Skill Title
category: 未分类
scope: personal
status: active
version: 0.1.0
updated: 2026-05-12

purpose: One-sentence purpose.

relations:
  coordinates: []
  cooperates_with: []
  upstream: []
  downstream: []
  should_run_before: []
  should_run_after: []
  supersedes: []
  overlaps_with: []

notes:
  - Add short notes only when they improve graph interpretation.
```

Relation targets must be skill names without leading slash.

Good:

```yaml
relations:
  downstream:
    - skill-index
```

Bad:

```yaml
relations:
  downstream:
    - /skill-index
```

## Relation meanings

Use these relation fields consistently:

| Relation | Chinese label | Meaning |
|---|---|---|
| `coordinates` | 协调 | This skill governs or coordinates another skill |
| `cooperates_with` | 协同 | This skill works peer-to-peer with another skill |
| `upstream` | 上游 | This skill depends on another skill's output |
| `downstream` | 下游 | This skill feeds another skill |
| `should_run_before` | 先于 | This skill usually runs before another skill |
| `should_run_after` | 后于 | This skill usually runs after another skill |
| `supersedes` | 替代 | This skill replaces an older skill |
| `overlaps_with` | 重叠 | This skill overlaps with another and may need cleanup |

## Main command

Generate personal skill graph:

```bash
python ~/.claude/skills/skill-graph/scripts/generate_skill_graph_html.py
```

Generate graph for a project skill directory:

```bash
python ~/.claude/skills/skill-graph/scripts/generate_skill_graph_html.py --root .claude/skills
```

Only create missing metadata:

```bash
python ~/.claude/skills/skill-graph/scripts/generate_skill_graph_html.py --init-meta-only
```

Only generate HTML from existing metadata:

```bash
python ~/.claude/skills/skill-graph/scripts/generate_skill_graph_html.py --graph-only
```

Write to a custom HTML path:

```bash
python ~/.claude/skills/skill-graph/scripts/generate_skill_graph_html.py --out ./SKILL_GRAPH.html
```

Overwrite existing metadata intentionally:

```bash
python ~/.claude/skills/skill-graph/scripts/generate_skill_graph_html.py --overwrite-meta
```

Use `--overwrite-meta` carefully because it can replace hand-edited relationships.

## Default output

The script writes:

```bash
~/.claude/skills/SKILL_GRAPH.html
```

The HTML is Chinese, single-file, and offline-friendly.

It includes:

- Search box
- Category filter
- Scope filter
- Status filter
- Interactive SVG relationship graph
- Clickable skill details
- Relationship table
- Metadata warnings
- Isolated skill list
- Inventory table

## Current expected local skills

The current local skill set may include:

```text
/find-local-skills
/find-skills
/math-method-lib
/matlab-traditional-gui
/skill-distiller
/skill-graph
/skill-index
```

The script should not hardcode this list, but it may infer useful default relationships for these names.

## Recommended coordination model

Use this mental model:

```text
/find-local-skills  → 查本地已有 skill，避免重复
/find-skills        → 找外部新 skill
/skill-distiller    → 把经验沉淀成 SKILL.md
/skill-index        → 路由、分类、治理 skill 系统
/skill-graph        → 生成可视化关系图和 metadata 健康检查
```

Domain skills such as `/matlab-traditional-gui`, `/math-method-lib` should usually be graph leaves unless their metadata explicitly declares relationships.

## Safety rules

- Do not execute arbitrary scripts from other skill folders.
- Do not overwrite existing `skill.meta.yaml` unless explicitly requested.
- Do not infer dangerous tool permissions from metadata.
- Do not treat external skills as safe just because they appear in the graph.
- Do not turn the graph into the routing source of truth. Use `/skill-index` for routing.
- Keep this skill focused on metadata and visualization.

## Output expectations

When this skill is used:

- Provide the exact command to run the graph generator.
- Explain where `skill.meta.yaml` files will be created.
- Explain where `SKILL_GRAPH.html` will be generated.
- Summarize isolated skills and broken relationships.
- Recommend `/skill-index` for taxonomy and routing changes.
- Recommend `/find-local-skills` for actual duplicate audits.
- Keep the architecture simple: `skill.meta.yaml + Python + Chinese single-file HTML + Git`.

## Final rule

Use this separation:

```text
/skill-graph       → visual relationships and metadata health
/skill-index       → routing, taxonomy, and governance
/find-local-skills → actual local inventory
/skill-distiller   → individual skill creation
/find-skills       → external skill discovery
```
