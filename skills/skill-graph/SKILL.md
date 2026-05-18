---
name: skill-graph
description: 生成中文 HTML 技能关系图，创建或维护 skill.meta.yaml 文件，可视化技能之间的协作关系。触发场景：用户要技能关系图、元数据健康检查、关系映射、中文 HTML 技能概览。
argument-hint: "[skills-root-or-graph-task]"
disable-model-invocation: true
---

# 技能关系图

维护本地技能的中文 HTML 关系图，两大职责：

```text
1. 确保每个本地技能有 skill.meta.yaml
2. 从元数据生成中文单文件 HTML 图
```

此技能不负责路由。路由和分类属于 `/skill-index`。

图可视化物理和渲染遵循 `/force-graph-physics` 的规则。

## 适用场景

- 生成技能可视化图
- 创建或更新 `skill.meta.yaml`
- 生成中文 HTML 关系图
- 查看技能间协作关系
- 检测孤立技能
- 检测断裂关系
- 元数据健康检查

## 不适用场景

- 决定用哪个技能 → `/skill-index`
- 查看技能列表 → `/find-local-skills`
- 创建或重构技能 → `/skill-creator`
- 找外部技能 → `/find-skills`

## 目录结构

```bash
~/.claude/skills/<skill-name>/SKILL.md
~/.claude/skills/<skill-name>/skill.meta.yaml
```

禁止嵌套分类目录。

## 元数据文件

每个技能须有 `skill.meta.yaml`：

```yaml
name: skill-name
title: 技能标题
category: 未分类
scope: personal
status: active
version: 0.1.0
updated: 2026-05-12
source: local

purpose: 一句话用途描述。

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
  - 仅在能改善图解读时添加简短说明
```

关系目标必须是技能名，不加斜杠前缀。

## 关系含义

| 关系 | 含义 |
|------|------|
| `coordinates` | 此技能治理或协调另一技能 |
| `cooperates_with` | 对等协作 |
| `upstream` | 此技能依赖另一技能的输出 |
| `downstream` | 此技能为另一技能提供输入 |
| `should_run_before` | 通常先于另一技能运行 |
| `should_run_after` | 通常在另一技能之后运行 |
| `supersedes` | 替代旧技能 |
| `overlaps_with` | 与另一技能重叠，可能需要清理 |

## 工作流

每次调用本技能时，必须按以下顺序执行：

1. **扫描缺失元数据**：列出 `~/.claude/skills/` 下所有有 `SKILL.md` 但缺少 `skill.meta.yaml` 的技能
2. **报告并确认**：将缺失清单展示给用户，询问是否需要补建。不要静默自动生成空壳
3. **补建元数据**（用户确认后）：根据 SKILL.md 的 frontmatter 和内容手工填写 `skill.meta.yaml`，确保 title、purpose、category、relations 等字段准确
4. **生成图**：`--graph-only` 重建 `SKILL_GRAPH.html`
5. **报告结果**：汇总节点数、新增/更新元数据数、孤立节点、断裂关系

## 主要命令

```bash
# 生成个人技能图
python ~/.claude/skills/skill-graph/scripts/generate_skill_graph_html.py

# 生成项目技能目录的图
python ~/.claude/skills/skill-graph/scripts/generate_skill_graph_html.py --root .claude/skills

# 仅创建缺失的元数据
python ~/.claude/skills/skill-graph/scripts/generate_skill_graph_html.py --init-meta-only

# 仅从现有元数据生成 HTML
python ~/.claude/skills/skill-graph/scripts/generate_skill_graph_html.py --graph-only

# 自定义输出路径
python ~/.claude/skills/skill-graph/scripts/generate_skill_graph_html.py --out ./SKILL_GRAPH.html

# 覆盖已有元数据（谨慎使用）
python ~/.claude/skills/skill-graph/scripts/generate_skill_graph_html.py --overwrite-meta
```

`--overwrite-meta` 会替换手动编辑的关系，谨慎使用。

## 默认输出

```bash
~/.claude/skills/SKILL_GRAPH.html
```

中文单文件 HTML，离线可用。包含：搜索框、分类筛选、范围筛选、状态筛选、交互式 SVG 关系图、可点击技能详情、关系表、元数据警告、孤立技能列表、清单表。

## 推荐协调模型

```text
/find-local-skills → 查本地已有
/find-skills       → 找外部新增
/skill-creator     → 从经验蒸馏/创建/改进
/skill-index       → 路由、分类、治理
/skill-graph       → 可视化、元数据健康
```

## 安全规则

- 不执行其他技能目录中的任意脚本
- 未被明确要求时不覆盖已有 `skill.meta.yaml`
- 不从元数据推断危险权限
- 不因在图中出现就假设外部技能安全
- 图不做路由源（用 `/skill-index`）
