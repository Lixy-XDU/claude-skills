"""加载本机配置。所有 skill 脚本统一从这里读路径。"""
from pathlib import Path
import os
import sys

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


if __name__ == "__main__":
    cfg = load_config()
    print("配置加载成功:")
    for k, v in (cfg.get("paths") or {}).items():
        print(f"  {k}: {v}")
