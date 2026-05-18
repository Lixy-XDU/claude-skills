---
name: nature
description: 学术写作全流程工作台。仅当用户进行学术写作相关任务时调用——润色、写作、图表、引用、数据声明、审稿回复、文献检索。调用后先展示功能菜单让用户选择。
argument-hint: "[任务描述或子命令]"
allowed-tools: Read Write Edit Glob Grep Bash(python3 *) WebSearch WebFetch
---

# Nature 学术写作工作台

一站式学术写作工具集。调用后先展示菜单，根据用户选择进入对应工作流。

## 功能菜单

| 序号 | 功能 | 说明 |
|------|------|------|
| 1 | 学术润色 | 将中文初稿或英文草稿打磨为 Nature 风格学术英语 |
| 2 | 论文写作 | 从声明、结果、笔记起草或重构论文章节 |
| 3 | 论文图表 | 生成符合 Nature 排版标准的多面板科学图表（Python/R） |
| 4 | 文献引用 | 为文稿自动匹配 Nature/CNS 系列引用并导出参考文献 |
| 5 | 数据声明 | 准备或审计 Nature 数据可用性声明和 FAIR 元数据 |
| 6 | 审稿回复 | 起草或审计 Nature 系列期刊逐点审稿回复信 |
| 7 | 文献检索 | 多源文献搜索、引文验证、引文文件管理 |

## 工作流

1. 展示上方菜单，让用户选择
2. 根据选择执行对应功能的具体流程（见下方各节）
3. 完成后汇报结果

## 各功能流程

### 1. 学术润色

- 中译英：中文初稿 → 逐段翻译 → 学术措辞优化 → Nature 风格打磨
- 英文润色：按 Nature 写作策略（简洁、精确、主动语态）逐句优化
- 使用 Academic Phrasebank 和 Nature Communications 语料作为措辞参考
- 保留技术术语、数据、引用不变

### 2. 论文写作

- 根据用户提供的声明（claims）、结果（results）、图表引用起草论文章节
- 支持：Abstract、Introduction、Results、Discussion、Conclusion、Methods
- 遵循 Nature 风格：结论先行、逻辑链清晰、段落短小聚焦
- 可以基于中文草稿重构为英文，也可以从零起草

### 3. 论文图表

- 开始前先问"Python 还是 R？"
- 定义图表要传达的结论和证据逻辑
- Python 路径：matplotlib/seaborn  → 排版优化 → SVG/PDF/TIFF 导出
- R 路径：ggplot2/patchwork/ComplexHeatmap → 同上
- 导出前检查：字号 ≥ 8pt、线条 ≥ 0.5pt、色彩色盲友好、多面板对齐

### 4. 文献引用

- 将用户文稿按声明拆分段落
- 为每段在 Nature Portfolio / Science / Cell Press 期刊中搜索支撑文献
- 按时间范围和期刊等级筛选
- 输出：正文中 `[n]` 标注 + 参考文献列表（EndNote/RIS/BibTeX）

### 5. 数据声明

- 检查或起草 Nature 风格的 Data Availability 声明
- 推荐合适的数据仓库（Figshare、Zenodo、Dryad、GEO 等）
- 涉及受限数据时提供访问说明模板
- 生成 FAIR 元数据检查清单

### 6. 审稿回复

- 读取 reviewer comments 和 editor decision
- 按逐点回复格式起草：Reviewer 原文 → Response（礼貌、具体、有证据）→ Action taken
- 区分 major/minor revision 的处理深度
- 输出格式适合直接粘贴到投稿系统

### 7. 文献检索

- 多源并行搜索：PubMed（MeSH 策略）、CrossRef、arXiv
- 支持 .nbib / .ris / .bib 引文文件管理和格式转换
- 检索结果去重、按年份/引用量排序
- 输出结构化文献列表

## 路由规则

- "润色/抛光/polish" → 1
- "写作/draft/write/introduction/abstract" → 2
- "画图/图表/figure/plot" → 3
- "引用/citation/参考文献" → 4
- "数据声明/data availability" → 5
- "审稿/回复/reviewer/response/rebuttal" → 6
- "检索/search/PubMed/文献" → 7
- 只说"学术写作/写论文"未指定 → 展示菜单
