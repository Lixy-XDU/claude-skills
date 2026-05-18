# Claude Skills Index

## Quick routing map

| Need | Use | Purpose |
|---|---|---|
| 找本地已有 skill | `/find-local-skills` | 查本地安装的 skill，避免重复 |
| 找外部新 skill | `/find-skills` | 搜索社区/外部 skill |
| 把经验沉淀成 skill | `/skill-creator` | 从笔记、调试记录、项目经验中提炼 SKILL.md |
| 更新 skills 到最新版本 | `/skill-updater` | 一键 git pull 最新 skills 和 CLAUDE.md |
| skill 路由/分类/索引管理 | `/skill-index` | 为本文件维护提供路由和分类决策 |
| skill 关系图/元数据健康 | `/skill-graph` | 生成 SKILL_GRAPH.html 和检查 metadata |
| 读论文做结构化笔记 | `/literature-paper-reading` | 按 10 维度框架读论文输出 Obsidian 笔记 |
| 从论文提取数学方法 | `/literature-to-math` | PDF → 数学方法 → math-method-lib 入库 |
| 管理数学方法库条目 | `/math-method-lib` | 按 16 节模板创建或审查方法条目 |
| 从 MATLAB 代码重建数学模型 | `/ml-model-reconstructor` | 代码 → 数学模型 → 变量 → 推导 → 公式 |
| Markdown 转 HTML | `/markdown-to-html` | 微信兼容主题的 MD→HTML 转换 |
| 从 PDF 提取文本 | `/pdf-extract` | 三级策略提取 PDF 文本，供其他 skill 委托调用 |
| 构建图可视化物理引擎 | `/force-graph-physics` | 力导向图渲染性能、物理模拟、碰撞检测的权威参考 |
| 学术写作全流程 | `/nature` | 润色/写作/图表/引用/数据/审稿/检索，调用后展示菜单 |
| 内容转幻灯片 | `/paper-note-to-ppt-template` | PNG 模板 + python-pptx 生成科研风格 PPT |
| 论文全文解读/对照阅读 | `/literature-paper-reading` | 中英对照全文解读，图文表定位，源锚点追溯 |

---

## 元技能

| Skill | Scope | Purpose | Invocation |
|---|---|---|---|
| `skill-updater` | personal | 一键检查并拉取 claude-skills 最新更新 | `/skill-updater` |
| `skill-index` | personal | 路由、分类、协调、审计本地 skill 系统 | `/skill-index` |
| `skill-creator` | personal | 创建、改进、测试和从经验中蒸馏技能（distill/create/improve） | `/skill-creator` |
| `skill-graph` | personal | 维护 skill.meta.yaml 并生成中文 HTML 关系图 | `/skill-graph` |
| `find-local-skills` | personal | 查找、列出、审查本地已安装的 skill | `/find-local-skills` |
| `find-skills` | personal | 搜索和发现外部/社区 skill | `/find-skills` |
| `skill-lifecycle` | personal | 统一管理技能生命周期——删除、禁用、启用 | `/skill-lifecycle` |

## 数学与方法库

| Skill | Scope | Purpose | Invocation |
|---|---|---|---|
| `math-method-lib` | personal | 按 16 节模板创建或审查数学方法条目 | `/math-method-lib` |
| `literature-to-math` | personal | 从学术文献 PDF 中提取数学方法入库 | `/literature-to-math` |
| `literature-paper-reading` | personal | 按 10 维度框架系统阅读论文并产出结构化 Obsidian 笔记；支持中英逐段对照全文阅读、图表裁剪嵌入、源锚点追溯 | `/literature-paper-reading` |
| `ml-model-reconstructor` | personal | 从 MATLAB 代码逆向重建数学模型、推导与公式 | `/ml-model-reconstructor` |
| `ml-research-coder` | personal | 将方法笔记/文献笔记转为 MATLAB 开发环境，含项目脚手架、实验、测试 | `/ml-research-coder` |

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
| `nature` | personal | 学术写作全流程工作台：润色、写作、图表、引用、数据声明、审稿回复、文献检索，调用后展示菜单选择 | `/nature` |

## 演示与文档

| Skill | Scope | Purpose | Invocation |
|---|---|---|---|
| `paper-note-to-ppt-template` | personal | PNG 模板 + python-pptx 渲染，论文/笔记转科研风格 PPT（组会/答辩/汇报） | `/paper-note-to-ppt-template` |
| `pptx-layout-reverse` | personal | PPTX 逆向还原为 JSON 布局配置，提取坐标/字号/公式框 | `/pptx-layout-reverse` |

## 设计与界面

| Skill | Scope | Purpose | Invocation |
|---|---|---|---|

| `nature-figure` | personal | 符合 Nature 排版标准的多面板科学图表（Python/R） | `/nature-figure` |

## 未分类

（暂无）

---

## Cleanup recommendations

- `markdown-to-html` scope 为 external，若未来有本地修改需更新 scope
