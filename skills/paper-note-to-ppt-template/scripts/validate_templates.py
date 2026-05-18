#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查用户 PNG 模板是否已经放入 templates/。"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def find_template(template_dir: Path, aliases: list[str]) -> str | None:
    for name in aliases:
        p = template_dir / name
        if p.exists():
            return str(p)
    # 容错：忽略大小写和扩展名
    stems = {Path(a).stem.lower() for a in aliases}
    for p in template_dir.glob("*"):
        if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg"}:
            if p.stem.lower() in stems:
                return str(p)
    return None


def main() -> int:
    if len(sys.argv) != 4:
        print("Usage: validate_templates.py <template_dir> <layouts_json> <output_report.json>")
        return 2

    template_dir = Path(sys.argv[1]).expanduser().resolve()
    layouts_json = Path(sys.argv[2]).expanduser().resolve()
    output = Path(sys.argv[3]).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    data = json.loads(layouts_json.read_text(encoding="utf-8"))
    aliases = data.get("template_aliases", {})

    found = {}
    missing = []
    for key, names in aliases.items():
        hit = find_template(template_dir, names)
        if hit:
            found[key] = hit
        else:
            missing.append({"template_key": key, "expected": names})

    report = {
        "template_dir": str(template_dir),
        "status": "pass" if not missing else "fail",
        "found": found,
        "missing": missing
    }
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    if missing:
        print("Missing templates:")
        for m in missing:
            print(f"- {m['template_key']}: {', '.join(m['expected'])}")
        return 1

    print("All templates found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
