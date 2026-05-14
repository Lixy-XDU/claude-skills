#!/usr/bin/env python3
"""
薄包装 — 委托给 pdf-extract 的通用 PDF 提取器。

本文件保留是为了向后兼容。新代码请直接调用：
    python <pdf-extract>/scripts/pdf_extractor.py <args>
"""

import sys
from pathlib import Path

# pdf-extract 的脚本相对于本文件位于 ../../../pdf-extract/scripts/
_real_script = Path(__file__).resolve().parents[2] / "pdf-extract" / "scripts" / "pdf_extractor.py"

if not _real_script.exists():
    sys.exit(
        f"PDF 提取脚本已迁移。请使用 /pdf-extract：\n"
        f"  python \"{_real_script}\" <pdf-path> --out <dir>\n"
        f"原脚本路径: {Path(__file__).resolve()}"
    )

# 将参数透传给真正的脚本
sys.argv[0] = str(_real_script)
exec(compile(_real_script.read_text(encoding="utf-8"), str(_real_script), "exec"))
