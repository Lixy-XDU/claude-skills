#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把简单 LaTeX/mathtext 公式渲染成 PNG，用于 PPT 中等比插入。"""

from __future__ import annotations

import sys
from pathlib import Path


def render_formula(latex: str, output_path: str | Path, color: str = "#00326E") -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        import matplotlib.pyplot as plt
        fig = plt.figure(figsize=(8, 1.2), dpi=240)
        fig.patch.set_alpha(0)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis("off")
        text = latex.strip()
        if not (text.startswith("$") and text.endswith("$")):
            text = f"${text}$"
        ax.text(0.5, 0.5, text, ha="center", va="center", fontsize=24, color=color)
        fig.savefig(output, transparent=True, bbox_inches="tight", pad_inches=0.08)
        plt.close(fig)
        return output
    except Exception:
        # fallback：写一张提示图，避免主流程崩溃
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new("RGBA", (1600, 260), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", 34)
        except Exception:
            font = ImageFont.load_default()
        draw.text((30, 90), latex, fill=(0, 50, 110, 255), font=font)
        img.save(output)
        return output


def main() -> int:
    if len(sys.argv) < 3:
        print("Usage: render_formula.py <latex> <output_png>")
        return 2
    render_formula(sys.argv[1], sys.argv[2])
    print(sys.argv[2])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
