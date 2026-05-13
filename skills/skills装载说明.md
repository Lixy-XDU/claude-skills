# Skills 迁移后路径装载说明文档

> **设计目标**：实现代码与运行环境的完全解耦。所有 Skill 脚本中不出现任何绝对路径，机器相关的配置统一通过本地 YAML 文件管理，便于跨机器迁移。

---

## 1. 核心文件结构

迁移完成后，`skills` 目录应保持以下结构：

```text
~/.claude/skills/
├── config.local.yaml           # 本机专用配置文件（加入 .gitignore，绝不提交）
├── config.local.example.yaml   # 配置模板（随代码仓库分发）
└── _shared/
    └── load_config.py          # 统一路径加载器（所有 Skill 共用）
```

---

## 2. 配置 `config.local.yaml`

这是迁移到新机器后**唯一需要手动修改**的文件。

### 创建步骤

```powershell
cd $env:USERPROFILE\.claude\skills
Copy-Item config.local.example.yaml config.local.yaml
notepad config.local.yaml
```

### 配置示例

```yaml
# ~/.claude/skills/config.local.yaml
# 请根据新机器的实际路径修改

paths:
  papers_root:     "D:/Research/Papers"              # 文献 PDF 总目录
  obsidian_vault:  "D:/Obsidian/MainVault"           # Obsidian 主仓库根目录
  obsidian_inbox:  "D:/Obsidian/MainVault/00-Inbox"  # 收件箱路径
  math_method_lib: "D:/Obsidian/MainVault/20-MathMethods"  # 数学方法库

tools:
  qpdf:      "qpdf"        # 优先使用 PATH 中的命令
  tesseract: "tesseract"
  python:    "python"
```

**注意事项**：
- 推荐使用正斜杠 `/`
- 路径末尾不要加多余的斜杠
- 支持环境变量覆盖（见第 5 节）

---

## 3. 统一加载器 `_shared/load_config.py`

```python
"""加载本机配置，所有 Skill 脚本统一从这里读取路径"""

from pathlib import Path
import os
import sys

try:
    import yaml
except ImportError:
    sys.exit("请先安装依赖: pip install pyyaml")

SKILLS_ROOT = Path(__file__).resolve().parent.parent

def load_config() -> dict:
    cfg_path = SKILLS_ROOT / "config.local.yaml"
    if not cfg_path.exists():
        sys.exit(
            f"未找到配置文件: {cfg_path}\n"
            f"请复制 config.local.example.yaml 为 config.local.yaml 并填写路径。"
        )
    
    with cfg_path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    
    # 支持环境变量覆盖
    for k, v in (cfg.get("paths") or {}).items():
        env_key = f"CLAUDE_SKILLS_{k.upper()}"
        if env_key in os.environ:
            cfg["paths"][k] = os.environ[env_key]
    
    return cfg
```

---

## 4. 在 Skill 脚本中使用

所有 Skill 脚本的标准调用方式：

```python
import sys
from pathlib import Path

# 添加共享模块搜索路径
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_shared"))
from load_config import load_config

# 加载配置
cfg = load_config()

# 使用路径（推荐转为 Path 对象）
papers_root = Path(cfg["paths"]["papers_root"])
inbox       = Path(cfg["paths"]["obsidian_inbox"])
vault       = Path(cfg["paths"]["obsidian_vault"])

# 后续代码直接使用以上变量
print(f"文献库路径: {papers_root}")
```

---

## 5. 环境变量覆盖（高级功能）

支持临时覆盖配置，无需修改 YAML 文件：

```powershell
$env:CLAUDE_SKILLS_PAPERS_ROOT = "E:/Backup/Papers"
python your_skill.py
```

---

## 6. 迁移后自检清单

1. [ ] 已创建并正确填写 `config.local.yaml`
2. [ ] 运行 `python _shared\load_config.py` 无报错
3. [ ] `pyyaml` 已安装（`pip show pyyaml`）
4. [ ] 所有引用的目录在新机器上真实存在
5. [ ] `config.local.yaml` 未被加入 Git

---

**优势总结**：  
以后每次迁移或换新电脑，只需**复制模板 → 修改一个 YAML 文件**，所有 Skill 代码无需任何改动即可正常运行。