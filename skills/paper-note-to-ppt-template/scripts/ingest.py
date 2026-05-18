#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解析 PDF / Markdown / txt / 目录，输出 clean_notes.md。
这是轻量脚本，复杂论文理解仍由 Claude 完成。
"""

from __future__ import annotations

import sys
from pathlib import Path


def read_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except Exception:
        return f"[PDF 解析需要安装 pypdf]\n文件：{path}\n请运行：pip install pypdf\n"

    reader = PdfReader(str(path))
    chunks = []
    for i, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception as exc:
            text = f"[第 {i} 页解析失败：{exc}]"
        chunks.append(f"\n\n## Page {i}\n\n{text.strip()}")
    return "\n".join(chunks)


def read_text(path: Path) -> str:
    for enc in ("utf-8", "utf-8-sig", "gb18030", "latin-1"):
        try:
            return path.read_text(encoding=enc)
        except Exception:
            continue
    return path.read_bytes().decode("utf-8", errors="ignore")


def collect_from_dir(path: Path) -> str:
    parts = [f"# 输入目录：{path}\n"]
    exts = {".md", ".txt", ".pdf"}
    files = [p for p in sorted(path.rglob("*")) if p.is_file() and p.suffix.lower() in exts]
    for file in files:
        parts.append(f"\n\n# 文件：{file.name}\n")
        if file.suffix.lower() == ".pdf":
            parts.append(read_pdf(file))
        else:
            parts.append(read_text(file))
    if not files:
        parts.append("未发现 .pdf / .md / .txt 文件。\n")
    return "\n".join(parts)


def normalize_text(text: str) -> str:
    lines = [ln.rstrip() for ln in text.splitlines()]
    # 合并连续过多空行
    out = []
    blank = 0
    for ln in lines:
        if ln.strip():
            blank = 0
            out.append(ln)
        else:
            blank += 1
            if blank <= 2:
                out.append(ln)
    return "\n".join(out).strip() + "\n"


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: ingest.py <input_path> <output_clean_notes.md>")
        return 2

    input_path = Path(sys.argv[1]).expanduser().resolve()
    output_path = Path(sys.argv[2]).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        output_path.write_text(f"# 输入不存在\n\n{input_path}\n", encoding="utf-8")
        print(f"Input not found: {input_path}")
        return 1

    if input_path.is_dir():
        text = collect_from_dir(input_path)
    elif input_path.suffix.lower() == ".pdf":
        text = read_pdf(input_path)
    else:
        text = read_text(input_path)

    header = f"# Clean Notes\n\n- Source: `{input_path}`\n\n---\n\n"
    output_path.write_text(header + normalize_text(text), encoding="utf-8")
    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
