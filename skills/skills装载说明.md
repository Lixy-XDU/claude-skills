# Skills 装载说明

> 从 GitHub 克隆 skill 库到新机器，或从零搭建 skill 运行环境。

---

## 1. 获取 skills

```powershell
# 克隆到本地
git clone git@github.com:<your-username>/claude-skills.git $env:USERPROFILE\.claude\skills
```

或从备份解压到 `~/.claude/skills/`。

---

## 2. 目录结构

```text
~/.claude/skills/
├── SKILLS_INDEX.md            # 技能索引（14 个 skill，6 个类别）
├── SKILL_GRAPH.html           # 关系图谱（由 skill-graph 生成）
├── CHANGELOG.md               # 更新日志
├── config.local.example.yaml  # 配置模板
├── config.local.yaml          # 本机配置（.gitignore，手动创建）
├── _shared/
│   └── load_config.py         # 统一配置加载器
├── pdf-extract/               # 工具：PDF 文本提取
├── force-graph-physics/       # 工具：图可视化物理引擎
├── math-method-lib/           # 数学方法库管理
├── literature-to-math/        # 文献数学方法提炼
├── literature-paper-reading/  # 论文系统阅读
├── matlab-traditional-gui/    # MATLAB GUI 开发
├── skill-index/               # 元技能：索引管理
├── skill-graph/               # 元技能：关系图生成
├── skill-distiller/           # 元技能：经验蒸馏
├── find-local-skills/         # 元技能：本地查找
├── find-skills/               # 元技能：外部搜索
├── skill-creator/             # 外部：skill 创建器
├── baoyu-markdown-to-html/    # 外部：Markdown → HTML
└── desktop-computer-automation/  # 外部：桌面自动化
```

---

## 3. 配置本机环境

```powershell
cd $env:USERPROFILE\.claude\skills
Copy-Item config.local.example.yaml config.local.yaml
notepad config.local.yaml
```

填写本机路径：

```yaml
paths:
  papers_root:     "D:/Research/Papers"
  obsidian_vault:  "D:/Obsidian/MainVault"
  obsidian_inbox:  "D:/Obsidian/MainVault/00-Inbox"
  math_method_lib: "D:/Obsidian/MainVault/20-MathMethods"

tools:
  qpdf:      "qpdf"
  tesseract: "tesseract"
  python:    "python"
```

---

## 4. 安装依赖

```powershell
# Python 基础依赖
pip install pyyaml pymupdf pdf2image pillow pytesseract

# 系统工具（二选一）
choco install qpdf tesseract
# 或手动下载加入 PATH
```

---

## 5. 验证

```powershell
cd $env:USERPROFILE\.claude\skills

# 验证配置加载
python _shared\load_config.py

# 重建关系图
python skill-graph\scripts\generate_skill_graph_html.py

# 测试 PDF 提取
python pdf-extract\scripts\pdf_extractor.py --help
```

---

## 6. Skill 委托关系

| 共享 skill | 被委托方 |
|---|---|
| `pdf-extract` | `literature-to-math`、`literature-paper-reading` |
| `force-graph-physics` | `skill-graph`（及任何需要图可视化的 skill） |

规则见 `~/.claude/CLAUDE.md` 第 3 节。
