# Claude Skills Index

## Quick routing map

| Need | Use | Purpose |
|---|---|---|
| 找本地已有 skill | `/find-local-skills` | 查本地安装的 skill，避免重复 |
| 找外部新 skill | `/find-skills` | 搜索社区/外部 skill |
| 把经验沉淀成 skill | `/skill-distiller` | 从笔记、调试记录、项目经验中提炼 SKILL.md |
| 更新 skills 到最新版本 | `/skill-updater` | 一键 git pull 最新 skills 和 CLAUDE.md |
| skill 路由/分类/索引管理 | `/skill-index` | 为本文件维护提供路由和分类决策 |
| skill 关系图/元数据健康 | `/skill-graph` | 生成 SKILL_GRAPH.html 和检查 metadata |
| 读论文做结构化笔记 | `/literature-paper-reading` | 按 10 维度框架读论文输出 Obsidian 笔记 |
| 从论文提取数学方法 | `/literature-to-math` | PDF → 数学方法 → math-method-lib 入库 |
| 管理数学方法库条目 | `/math-method-lib` | 按 16 节模板创建或审查方法条目 |
| 从 MATLAB 代码重建数学模型 | `/ml-model-reconstructor` | 代码 → 数学模型 → 变量 → 推导 → 公式 |
| MATLAB 传统 GUI 开发 | `/ml-traditional-gui` | figure + uicontrol 的 GUI 编码/重构/审查 |
| Markdown 转 HTML | `/markdown-to-html` | 微信兼容主题的 MD→HTML 转换 |
| 从 PDF 提取文本 | `/pdf-extract` | 三级策略提取 PDF 文本，供其他 skill 委托调用 |
| 构建图可视化物理引擎 | `/force-graph-physics` | 力导向图渲染性能、物理模拟、碰撞检测的权威参考 |
| 学术英语润色/翻译 | `/nature-polishing` | 12 步流水线打磨至 Nature 风格，含中译英 |
| 论文图表绘制 | `/nature-figure` | 生成符合 Nature 排版标准的多面板图表（Python/R） |
| 论文写作/重构 | `/nature-writing` | 从声明、结果、笔记起草 Nature 风格论文章节 |
| 文献检索 | `/nature-academic-search` | 多源文献搜索、引文验证、MeSH 策略 |
| 论文转 PPT | `/nature-paper2ppt` | 从论文构建中文 PPT 演示文稿 |
| 审稿回复 | `/nature-response` | 起草或审计 Nature 系列期刊逐点审稿回复信 |
| 论文全文解读 | `/nature-reader` | 中英对照全文解读，图文表定位，带源锚点 |

---

## 元技能

| Skill | Scope | Purpose | Invocation |
|---|---|---|---|
| `skill-updater` | personal | 一键检查并拉取 claude-skills 最新更新 | `/skill-updater` |
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
| `ml-model-reconstructor` | personal | 从 MATLAB 代码逆向重建数学模型、推导与公式 | `/ml-model-reconstructor` |

## 文档与写作

| Skill | Scope | Purpose | Invocation |
|---|---|---|---|
| `markdown-to-html` | external | Markdown 转微信兼容主题 HTML | `/markdown-to-html` |

## 工具

| Skill | Scope | Purpose | Invocation |
|---|---|---|---|
| `pdf-extract` | personal | PDF 文本提取（三级策略：PyMuPDF → qpdf 解密 → OCR），供其他 skill 委托调用 | `/pdf-extract` |
| `force-graph-physics` | personal | 图可视化物理引擎权威参考，skill-graph 遵循其规则 | `/force-graph-physics` |
| `desktop-computer-automation` | personal | 基于 Midscene 的视觉驱动桌面自动化 | `/desktop-computer-automation` |

## 学术写作与出版

| Skill | Scope | Purpose | Invocation |
|---|---|---|---|
| `nature-polishing` | personal | 12 步润色流水线，学术英语打磨至 Nature 风格（含中译英） | `/nature-polishing` |
| `nature-writing` | personal | 从声明/结果/笔记起草或重构 Nature 风格论文章节 | `/nature-writing` |
| `nature-citation` | personal | 为文稿自动匹配 Nature/CNS 系列引用并导出参考文献 | `/nature-citation` |
| `nature-data` | personal | 准备或审计 Nature 数据可用性声明和 FAIR 元数据 | `/nature-data` |
| `nature-paper2ppt` | personal | 从论文构建 Nature 风格中文 PPT 演示文稿 | `/nature-paper2ppt` |
| `nature-reader` | personal | 中英对照全文解读，图文表定位，源锚点保持 | `/nature-reader` |
| `nature-response` | personal | 起草或审计 Nature 系列期刊逐点审稿回复信 | `/nature-response` |
| `nature-academic-search` | personal | 多源文献搜索、引文验证、引文文件管理 | `/nature-academic-search` |

## 设计与界面

| Skill | Scope | Purpose | Invocation |
|---|---|---|---|
| `ml-traditional-gui` | personal | MATLAB 传统 figure/uicontrol GUI 开发、重构与审查 | `/ml-traditional-gui` |
| `nature-figure` | personal | 符合 Nature 排版标准的多面板科学图表（Python/R） | `/nature-figure` |

## 未分类

（暂无）

---

## Cleanup recommendations

- `skill-creator` scope 为 external，如需本地定制可 fork 为 personal skill
- `markdown-to-html` scope 为 external，若未来有本地修改需更新 scope
