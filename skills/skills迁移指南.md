# Skills 本地迁移指南

> 核心思路：将「数据与配置」和「代码与规则」分离，机器相关内容抽成外部配置，其余全部可移植。

---

## 一、定位机器相关内容

在 skills 根目录执行全局扫描，找出绑死在本机的内容：

```powershell
cd $env:USERPROFILE\.claude\skills

# 绝对路径（Windows 盘符）
Select-String -Path *\*.md,*\*.yaml,*\*.py,*\*.m -Pattern '[A-Za-z]:\\' -CaseSensitive

# 用户名
Select-String -Path *\*.md,*\*.yaml,*\*.py,*\*.m -Pattern $env:USERNAME

# 硬编码的 home 目录
Select-String -Path *\*.md,*\*.yaml,*\*.py,*\*.m -Pattern 'C:\\Users\\'
```

**重点检查：**
- `SKILL.md` / `skill.meta.yaml` 中写死的 vault 路径、文献库路径
- 脚本中的 `cd "D:\..."`、`open("C:\\Users\\...")` 等硬编码
- 配置文件（`*.json`、`*.yaml`）里的绝对路径

---

## 二、抽取机器配置到中心文件

在 skills 根目录创建 `config.local.yaml`（加入 `.gitignore`，不随仓库同步）：

```yaml
# ~/.claude/skills/config.local.yaml
paths:
  papers_root:       "D:/Research/Papers"
  obsidian_vault:    "D:/Obsidian/MainVault"
  obsidian_inbox:    "D:/Obsidian/MainVault/00-Inbox"
  math_method_lib:   "D:/Obsidian/MainVault/20-MathMethods"

tools:
  qpdf:      "qpdf"       # 依赖 PATH；特殊情况才填绝对路径
  tesseract: "tesseract"
  python:    "python"
```

同时提交一份模板 `config.local.example.yaml`（随仓库走）：

```yaml
paths:
  papers_root:    "<PATH_TO_PAPERS>"
  obsidian_vault: "<PATH_TO_OBSIDIAN_VAULT>"
  # ...
```

### 共用配置加载器

创建 `skills/_shared/load_config.py`，所有 skill 脚本统一调用：

```python
"""加载本机配置。所有 skill 脚本统一从这里读路径。"""
from pathlib import Path
import os, sys

try:
    import yaml
except ImportError:
    sys.exit("请先安装 pyyaml: pip install pyyaml")

SKILLS_ROOT = Path(__file__).resolve().parent.parent

def load_config() -> dict:
    cfg_path = SKILLS_ROOT / "config.local.yaml"
    if not cfg_path.exists():
        sys.exit(
            f"未找到 {cfg_path}\n"
            f"请复制 config.local.example.yaml 为 config.local.yaml 并填写本机路径。"
        )
    with cfg_path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    # 允许环境变量覆盖
    for k, v in (cfg.get("paths") or {}).items():
        env_key = f"CLAUDE_SKILLS_{k.upper()}"
        if env_key in os.environ:
            cfg["paths"][k] = os.environ[env_key]
    return cfg
```

---

## 三、改造现有 Skill 脚本

所有脚本通过 `load_config()` 获取路径，彻底移除绝对路径：

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_shared"))
from load_config import load_config

cfg = load_config()
papers_root = Path(cfg["paths"]["papers_root"])
inbox       = Path(cfg["paths"]["obsidian_inbox"])
```

`SKILL.md` 中若引用了 vault 路径，同样从 `config.local.yaml` 读取，不写死。

---

## 四、打包迁移（三步走）

**旧机器 — 打包：**
```powershell
cd $env:USERPROFILE\.claude
Compress-Archive -Path skills\* -DestinationPath skills_backup.zip -Force
# 确认 zip 内不含 config.local.yaml、__pycache__、.venv、_extracted
```

**传输** `skills_backup.zip` 到新机器后：

**新机器 — 解压并配置：**
```powershell
cd $env:USERPROFILE\.claude
Expand-Archive skills_backup.zip -DestinationPath skills

cd skills
Copy-Item config.local.example.yaml config.local.yaml
notepad config.local.yaml   # 填写新机器的路径
```

---

## 五、用 Git 管理（推荐）

```powershell
cd $env:USERPROFILE\.claude\skills
git init
```

`.gitignore` 至少包含：

```gitignore
# 本机配置
config.local.yaml

# 生成产物
SKILL_GRAPH.html
**/_extracted/
**/__pycache__/
**/*.pyc

# 虚拟环境
.venv/
```

日后在任何机器上 `git clone` 后，只需复制模板并修改 `config.local.yaml`，skill 本身无需改动。

---

## 六、迁移后自检

在新机器首次使用时执行：

```powershell
cd $env:USERPROFILE\.claude\skills

# 1. 验证配置加载
python _shared\load_config.py

# 2. 刷新关系图
python generate_skills_graph.py --graph-only

# 3. 测试单个 skill
# 例如：literature-to-math-extractor --check-deps
```

> **排错提示：** 若某个 skill 报错找不到路径，必定是 `config.local.yaml` 中漏填了对应字段，补全即可，无需改代码。
