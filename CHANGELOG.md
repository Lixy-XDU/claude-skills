# CHANGELOG — claude-skills

## 2026-05-19

- **新增**: `nature` — 学术写作全流程工作台，合并 7 个 nature-* 技能为统一入口，调用后展示功能菜单
- **新增**: `pptx-layout-reverse` — PPTX 逆向还原为 JSON 布局配置，与 paper-note-to-ppt-template 构成排版闭环
- **删除**: `nature-academic-search`, `nature-citation`, `nature-data`, `nature-figure`, `nature-polishing`, `nature-reader`, `nature-response`, `nature-writing` — 全部合并至 nature
- **删除**: `paper-note-to-ppt` — 被 paper-note-to-ppt-template 替代
- **删除**: `content-to-slides` — 被 paper-note-to-ppt-template 替代
- **删除**: `ppt-polish` — 工作表现不符合预期
- **删除**: `pptx-toolkit` — 无实际使用场景
- **重命名**: `baoyu-markdown-to-html` → `markdown-to-html`
- **修改**: `paper-note-to-ppt-template` — 大规模迭代：公式策略改为 PNG 渲染、字号更新（正文统一 18pt）、模板 bbox 调整、背景 80% 透明度、图片 caption 预留空间、mixed_box 标题偏移修正、与 pptx-layout-reverse 协同闭环
- **修改**: `skill-graph` — 增加工作流章节，调用时必须先扫描缺失 skill.meta.yaml
- **修改**: `SKILLS_INDEX.md` — 新增 paper-note-to-ppt-template、pptx-layout-reverse、ml-research-coder、nature；删除过时条目；修复路由表
- **修改**: `skill-graph` — 图脚本只认多行 YAML relations 格式，修复内联格式不解析的问题

## 2026-05-15

- **合并**: `skill-rm` + `skill-disable` → `skill-lifecycle` — 统一为子命令模式
- **合并**: `skill-distiller` → `skill-creator` — distill 作为 skill-creator 的 distill 模式
- **删除**: `ml-traditional-gui` — 移除 MATLAB 传统 GUI 开发技能
- **修改**: `skill-graph` — 画布尺寸从 1200x800 扩大到 1600x1000
- **修改**: `nature-*` 系列 — purpose 中文化 + 填写技能间 relations 关系
- **重构**: `matlab-` → `ml-` 前缀 — `matlab-research-coder` → `ml-research-coder` 等
- **修改**: `force-graph-physics` — 规则从 16 条扩至 22 条

## 2026-05-14

- **新建**: `skill-updater` — 一键检查并拉取 claude-skills 最新更新
- **修复**: `baoyu-markdown-to-html` — MathJax 注入修复
- **新建**: `force-graph-physics` — 图可视化物理引擎权威参考
- **新建**: `literature-paper-reading` — 10 维度框架论文阅读
- **新建**: `pdf-extract` — PDF 文本提取共享 skill
- **新建**: `SKILLS_INDEX.md` — 技能索引文件

## 2026-05-12

- **新建**: `skill-graph`、`skill-index`、`skill-distiller`、`literature-to-math`、`math-method-lib`

## 更早

- **新建**: `matlab-traditional-gui`、`find-local-skills`、`find-skills`、`skill-creator`、`baoyu-markdown-to-html`、`desktop-computer-automation`
