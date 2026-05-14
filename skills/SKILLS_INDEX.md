# Claude Skills Index

## Quick routing map

| Need | Use | Purpose |
|---|---|---|
| 找本地已有 skill | `/find-local-skills` | 查本地安装的 skill，避免重复 |
| 找外部新 skill | `/find-skills` | 搜索社区/外部 skill |
| 把经验沉淀成 skill | `/skill-distiller` | 从笔记、调试记录、项目经验中提炼 SKILL.md |
| skill 路由/分类/索引管理 | `/skill-index` | 为本文件维护提供路由和分类决策 |
| skill 关系图/元数据健康 | `/skill-graph` | 生成 SKILL_GRAPH.html 和检查 metadata |
| 读论文做结构化笔记 | `/literature-paper-reading` | 按 10 维度框架读论文输出 Obsidian 笔记 |
| 从论文提取数学方法 | `/literature-to-math` | PDF → 数学方法 → math-method-lib 入库 |
| 管理数学方法库条目 | `/math-method-lib` | 按 16 节模板创建或审查方法条目 |
| MATLAB 传统 GUI 开发 | `/matlab-traditional-gui` | figure + uicontrol 的 GUI 编码/重构/审查 |
| Markdown 转 HTML | `/markdown-to-html` | 微信兼容主题的 MD→HTML 转换 |
| 从 PDF 提取文本 | `/pdf-extract` | 三级策略提取 PDF 文本，供其他 skill 委托调用 |
| 构建图可视化物理引擎 | `/force-graph-physics` | 力导向图渲染性能、物理模拟、碰撞检测的权威参考 |

---

## 元技能

| Skill | Scope | Purpose | Invocation |
|---|---|---|---|
| `skill-index` | personal | 路由、分类、协调、审计本地 skill 系统 | `/skill-index` |
| `skill-distiller` | personal | 从实践经验中蒸馏出可复用的 SKILL.md | `/skill-distiller` |
| `skill-graph` | personal | 维护 skill.meta.yaml 并生成中文 HTML 关系图 | `/skill-graph` |
| `skill-creator` | external | 创建、修改、评估和优化 skill | `/skill-creator` |
| `find-local-skills` | personal | 查找、列出、审查本地已安装的 skill | `/find-local-skills` |
| `find-skills` | personal | 搜索和发现外部/社区 skill | `/find-skills` |

## 数学与方法库

| Skill | Scope | Purpose | Invocation |
|---|---|---|---|
| `math-method-lib` | personal | 按 16 节模板创建或审查数学方法条目 | `/math-method-lib` |
| `literature-to-math` | personal | 从学术文献 PDF 中提取数学方法入库 | `/literature-to-math` |
| `literature-paper-reading` | personal | 按 10 维度框架系统阅读论文并产出结构化 Obsidian 笔记 | `/literature-paper-reading` |

## 文档与写作

| Skill | Scope | Purpose | Invocation |
|---|---|---|---|
| `markdown-to-html` | external | Markdown 转微信兼容主题 HTML | `/markdown-to-html` |

## 设计与界面

| Skill | Scope | Purpose | Invocation |
|---|---|---|---|
| `matlab-traditional-gui` | personal | MATLAB 传统 figure/uicontrol GUI 开发、重构与审查 | `/matlab-traditional-gui` |

## 工具

| Skill | Scope | Purpose | Invocation |
|---|---|---|---|
| `pdf-extract` | personal | PDF 文本提取（三级策略：PyMuPDF → qpdf 解密 → OCR），供其他 skill 委托调用 | `/pdf-extract` |
| `force-graph-physics` | personal | 图可视化物理引擎权威参考，skill-graph 遵循其规则 | `/force-graph-physics` |
| `desktop-computer-automation` | personal | 基于 Midscene 的视觉驱动桌面自动化 | `/desktop-computer-automation` |

## 未分类

（暂无）

---

## Cleanup recommendations

- `skill-creator` scope 为 external，如需本地定制可 fork 为 personal skill
- `markdown-to-html` scope 为 external，若未来有本地修改需更新 scope
