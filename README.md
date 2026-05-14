# Claude Code Skills & Global Constraints

我的 Claude Code 全局约束和 skill 库。

## 仓库结构

```
CLAUDE.md          # 全局约束（模板，使用时替换占位符）
skills/            # 15 个 skill，6 个类别
  ├── SKILL_GRAPH.html      # 关系图谱
  ├── SKILLS_INDEX.md       # 技能索引
  └── CHANGELOG.md          # 更新日志
```

## 一键装载

```powershell
git clone git@github.com:Lixy-XDU/claude-skills.git $env:USERPROFILE\.claude\skills; Copy-Item $env:USERPROFILE\.claude\skills\CLAUDE.md $env:USERPROFILE\.claude\CLAUDE.md -Force; Copy-Item $env:USERPROFILE\.claude\skills\config.local.example.yaml $env:USERPROFILE\.claude\skills\config.local.yaml
```

安装依赖（如需 PDF 提取功能）：

```powershell
pip install pyyaml pymupdf pdf2image pillow pytesseract
```

> 安装后编辑 `~/.claude/skills/config.local.yaml` 填入本地路径，然后运行 `/skill-updater` 验证。

## 配置 `config.local.yaml`

```yaml
paths:
  papers_root:     "D:/Research/Papers"
  obsidian_vault:  "D:/Obsidian/MainVault"
  obsidian_inbox:  "D:/Obsidian/MainVault/00-Inbox"
  math_method_lib: "D:/Obsidian/MainVault/20-MathMethods"

tools:
  qpdf:      "qpdf"
  tesseract: "tesseract"
```

## Skill 类别

| 类别 | Skill |
|---|---|
| 元技能 | `skill-updater`, `skill-index`, `skill-graph`, `skill-distiller`, `find-local-skills`, `find-skills` |
| 数学与方法库 | `math-method-lib`, `literature-to-math`, `literature-paper-reading` |
| 工具 | `pdf-extract`, `force-graph-physics`, `desktop-computer-automation` |
| 设计与界面 | `matlab-traditional-gui` |
| 文档与写作 | `markdown-to-html` |
| 外部 | `skill-creator` |

## Skill 委托规则

| 共享 skill | 被委托方 | 规则 |
|---|---|---|
| `pdf-extract` | `literature-to-math`, `literature-paper-reading` | PDF 文本提取统一入口，禁止自行实现 |
| `force-graph-physics` | `skill-graph` 等 | 力导向图渲染和物理引擎遵循统一规范 |

详见 `CLAUDE.md` 第 3 节。

## 生态系统维护

新增/修改/删除 skill 后的标准流程：

1. `/skill-index` → 更新 `SKILLS_INDEX.md`
2. `/skill-graph` → 重建 `SKILL_GRAPH.html`
3. 更新 `CHANGELOG.md`
4. 递增 `skill.meta.yaml` 版本号
5. 脱密 → `git commit` → `git push`

## 装载后验证

```powershell
cd $env:USERPROFILE\.claude\skills

python _shared\load_config.py                           # 验证配置
python skill-graph\scripts\generate_skill_graph_html.py  # 重建关系图
python pdf-extract\scripts\pdf_extractor.py --help       # 测试 PDF 提取
type SKILLS_INDEX.md                                     # 查看索引
```

## 自动更新

安装后，随时运行以下命令一键更新所有 skills：

```
/skill-updater
```

该 skill 会：
- `git pull` 拉取最新 skills
- 更新 `~/.claude/CLAUDE.md`（备份旧版）
- 重建 `SKILL_GRAPH.html`

无需手动管理 git。

## 贡献

本仓库的 master 副本位于作者本机（私有），所有更新以本机为准，经脱密后推送至此。
