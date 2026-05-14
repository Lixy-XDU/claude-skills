# Skills 更新日志

## 2026-05-14
- **修复**: `baoyu-markdown-to-html` — MathJax 注入三级回退：`</head>` 不存在时依次尝试 `<body`、`</title>`，解决 baoyu-md 输出无 `</head>` 时静默跳过注入导致公式无法渲染的问题；注入检测改为区分大小写的 `MathJax`
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
