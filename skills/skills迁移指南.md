# Skills 迁移指南

> 将 skills 生态系统从旧机器迁移到新机器，或在不同机器间保持同步。

---

## 一、架构概览

当前 skills 生态系统包含：

| 组件 | 路径 | 说明 |
|---|---|---|
| 全局约束 | `~/.claude/CLAUDE.md` | Claude Code 顶层规则 |
| 技能库 | `~/.claude/skills/` | 14 个 skill，6 个类别 |
| 本地仓库 | `D:\git仓库\` | git 跟踪的物理副本 |
| 远程仓库 | `github.com:<user>/claude-skills` | GitHub 公开仓库 |

Skill 类别：元技能 / 数学与方法库 / 工具 / 文档与写作 / 设计与界面 / 未分类。

---

## 二、迁移步骤

### 新机器首次部署

```powershell
# 1. 克隆仓库
git clone git@github.com:<your-username>/claude-skills.git D:\git仓库

# 2. 链接到 Claude Code 目录
New-Item -ItemType Junction -Path $env:USERPROFILE\.claude\skills -Target D:\git仓库\skills
# 或直接复制：
# Copy-Item -Recurse D:\git仓库\skills $env:USERPROFILE\.claude\skills

# 3. 复制 CLAUDE.md 模板
Copy-Item D:\git仓库\CLAUDE.md $env:USERPROFILE\.claude\CLAUDE.md

# 4. 创建本机配置
cd $env:USERPROFILE\.claude\skills
Copy-Item config.local.example.yaml config.local.yaml
notepad config.local.yaml

# 5. 安装依赖
pip install pyyaml pymupdf pdf2image pillow pytesseract
```

### 日常同步

在 `~/.claude/skills/` 或 `~/.claude/CLAUDE.md` 有变更后：

```powershell
# 同步到本地仓库
Copy-Item $env:USERPROFILE\.claude\CLAUDE.md D:\git仓库\ -Force
Copy-Item $env:USERPROFILE\.claude\skills\* D:\git仓库\skills\ -Recurse -Force

# 提交并推送
cd D:\git仓库
git add -A
git commit -m "chore: <简述变更>"
git push
```

---

## 三、配置解耦

所有机器相关路径集中在 `config.local.yaml`，不随仓库同步（已加入 `.gitignore`）。

脚本通过 `_shared/load_config.py` 统一读取：

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_shared"))
from load_config import load_config

cfg = load_config()
papers_root = Path(cfg["paths"]["papers_root"])
```

---

## 四、Skill 委托规则

| 规则 | 说明 |
|---|---|
| PDF 提取 → `/pdf-extract` | 禁止各 skill 自行实现 PyMuPDF / qpdf / OCR |
| 图可视化 → `/force-graph-physics` | 力导向图的渲染和物理引擎遵循统一规范 |

详见 `~/.claude/CLAUDE.md` 第 3 节。

---

## 五、生态系统维护

新增/修改/删除 skill 后的标准流程：

1. 调用 `/skill-index` 更新 `SKILLS_INDEX.md`
2. 调用 `/skill-graph` 重建 `SKILL_GRAPH.html`
3. 更新 `CHANGELOG.md`
4. 递增相关 skill 的 `skill.meta.yaml` 版本号
5. 同步到 `D:\git仓库` → `git commit` → `git push`

---

## 六、迁移后自检

```powershell
cd $env:USERPROFILE\.claude\skills

# 验证配置
python _shared\load_config.py

# 重建关系图
python skill-graph\scripts\generate_skill_graph_html.py

# 测试 PDF 提取
python pdf-extract\scripts\pdf_extractor.py --help

# 检查 skill 索引
type SKILLS_INDEX.md
```
