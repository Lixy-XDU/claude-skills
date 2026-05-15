# Skills 更新日志

## 2026-05-15
- **重构**: `matlab-` → `ml-` 前缀 — `matlab-research-coder` → `ml-research-coder`、`matlab-model-reconstructor` → `ml-model-reconstructor`、`matlab-traditional-gui` → `ml-traditional-gui`；全局引用同步更新，`infer_category` 兼容新旧前缀
- **修改**: `skill-graph` — 全面重构物理与视觉：节点缩至 0.125×、选中放大 4× + 关联放大 1.5×、条件文本显示、同分类平方正比引力 + 异分类平方反比斥力、正圆包络 + 分类名标注、去边标签 + 边细化透明、新增 MATLAB 分类、category 支持逗号分隔多值；版本 0.3.0 → 0.4.0
- **修改**: `force-graph-physics` — 规则从 16 条扩至 22 条，新增分类力学、选中冻结、视觉增强章节；工作流、反模式、故障排查同步更新
- **修改**: `matlab-traditional-gui` — 分类改为 `MATLAB, 设计与界面`（多分类）
- **修改**: `matlab-model-reconstructor` — 分类改为 `MATLAB, 数学与方法库`（多分类）
- **新建**: `matlab-model-reconstructor` — 从 MATLAB 代码（.m 文件、代码片段、项目目录）逆向重建底层数学模型、变量定义、推导过程和最终公式，针对信号处理和优化工作流优化
- **修改**: `SKILLS_INDEX.md` — 路由表和数学与方法库新增 `matlab-model-reconstructor` 条目

## 2026-05-14
- **新建**: `skill-updater` — 一键检查并拉取 claude-skills 最新更新，自动备份旧 CLAUDE.md、重建 SKILL_GRAPH.html、不覆盖 config.local.yaml
- **修复**: `baoyu-markdown-to-html` — MathJax 注入改用 array join 构建脚本字符串，根除 bun/npx 管道中 `$` 符号被截断导致公式无法渲染的问题（`0.1.1` 的三级回退方案未解决 $ 截断根因）
- **修复**: `baoyu-markdown-to-html` — MathJax 注入三级回退：`</head>` 不存在时依次尝试 `<body`、`</title>`，解决 baoyu-md 输出无 `</head>` 时静默跳过注入导致公式无法渲染的问题
- **新建**: `force-graph-physics` — 图可视化物理引擎权威参考，包含渲染性能、物理模拟、碰撞检测、拖拽交互的规则和反模式。所有图模型可视化委托给本 skill
- **新建**: `literature-paper-reading` — 按 10 维度框架系统阅读论文，产出结构化 Obsidian 笔记。前缀 `literature-`，与 `literature-to-math` 同家族
- **新建**: `pdf-extract` — PDF 文本提取共享 skill，三级策略（PyMuPDF → qpdf 解密 → OCR），供其他 skill 委托调用。类别 `工具`
- **修改**: `literature-to-math` — PDF 提取章节删除，改为委托 `/pdf-extract`；旧脚本 `literature_to_math_extractor.py` 改为薄包装
- **修改**: `literature-paper-reading` — PDF 提取章节删除，改为委托 `/pdf-extract`；协作关系 upstream 从 `literature-to-math` 更新为 `pdf-extract`
- **修改**: `skill-index` — `disable-model-invocation: true` → `false`，允许模型自动调用
- **新建**: `SKILLS_INDEX.md` — 技能索引文件，覆盖 12 个 skill（5 个类别），后续新增 `工具` 类别
- **修改**: `CLAUDE.md` — 第 3 节新增 PDF 提取统一委托规则，第 3 节新增更新日志规则
- **修改**: `SKILL_GRAPH.html` — 关系图改为有向图（实线箭头=单向，虚线=协作），节点标签改为中文标题，箭头端点修复（缩到圆周）

## 2026-05-12
- **新建**: `skill-graph` — 维护 skill.meta.yaml 并生成中文 HTML 关系图
- **新建**: `skill-index` — skill 路由、分类、协调与索引管理
- **新建**: `skill-distiller` — 从实践经验中蒸馏可复用 SKILL.md
- **新建**: `literature-to-math` — 从学术文献 PDF 中提取数学方法入库
- **新建**: `math-method-lib` — 按 16 节模板管理数学方法库条目

## 更早
- **新建**: `matlab-traditional-gui` — MATLAB 传统 GUI 开发
- **新建**: `find-local-skills` / `find-skills` — 本地/外部 skill 查找
- **新建**: `skill-creator` / `baoyu-markdown-to-html` / `desktop-computer-automation` — 外部 skill 安装
