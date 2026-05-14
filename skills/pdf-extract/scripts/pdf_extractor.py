#!/usr/bin/env python3
"""
PDF 文本提取器 — 支持加密 PDF（qpdf 解密）与扫描版 OCR。
依赖：pymupdf, pdf2image, pytesseract, pillow, qpdf（系统工具）

路径配置：
  - qpdf / tesseract 路径从 ../../config.local.yaml 的 tools 段读取（若有）
  - 若不配置则使用 PATH 中的默认命令
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Optional

try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit("请安装 PyMuPDF: pip install pymupdf")

try:
    from pdf2image import convert_from_path
except ImportError:
    convert_from_path = None

try:
    import pytesseract
except ImportError:
    pytesseract = None


def _load_skills_config() -> Optional[dict]:
    """从共享配置加载器获取路径。"""
    shared = Path(__file__).resolve().parents[2] / "_shared"
    if not shared.exists():
        return None
    sys.path.insert(0, str(shared))
    try:
        from load_config import load_config
        return load_config()
    except (ImportError, SystemExit):
        return None


_cfg = _load_skills_config()


def _get_tool(name: str, default: str = None) -> str:
    """从配置文件获取工具路径，若无则用 PATH 默认值。"""
    if default is None:
        default = name
    if _cfg and "tools" in _cfg:
        return _cfg["tools"].get(name, default)
    return default


def decrypt_pdf_with_qpdf(pdf_path: Path) -> Path:
    """使用 qpdf 移除 PDF 加密限制，返回解密后文件路径。"""
    output_path = pdf_path.with_name(f"{pdf_path.stem}_decrypted.pdf")
    qpdf_bin = _get_tool("qpdf")

    try:
        result = subprocess.run(
            [qpdf_bin, "--decrypt", str(pdf_path), str(output_path)],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and output_path.exists():
            print(f"  [Tier 2] qpdf 解密成功: {pdf_path.name}")
            return output_path
        else:
            print(f"  [Tier 2] qpdf 解密失败: {result.stderr.strip()}")
            return pdf_path
    except FileNotFoundError:
        print("  [Tier 2] 未找到 qpdf，请安装并加入 PATH")
        return pdf_path
    except subprocess.TimeoutExpired:
        print("  [Tier 2] qpdf 超时")
        return pdf_path


def extract_text_from_pdf(pdf_path: Path) -> dict:
    """
    三级策略提取 PDF 文本。
    返回: {"text": str, "tier": int, "encrypted": bool, "ocr_used": bool, "pages": int}
    """
    result = {"tier": 1, "encrypted": False, "ocr_used": False, "pages": 0}
    original_path = pdf_path
    processed_path = pdf_path
    decrypted_temp = None

    # Tier 2: 尝试 qpdf 解密
    if pdf_path.suffix.lower() == ".pdf":
        decrypted = decrypt_pdf_with_qpdf(pdf_path)
        if decrypted != pdf_path:
            result["encrypted"] = True
            result["tier"] = 2
            processed_path = decrypted
            decrypted_temp = decrypted

    # Tier 1/2: PyMuPDF 提取
    doc = fitz.open(processed_path)
    result["pages"] = doc.page_count
    text = ""

    for page in doc:
        page_text = page.get_text()
        if page_text.strip():
            text += page_text + "\n"

    # Tier 3: 文本太少时启用 OCR
    if len(text.strip()) < 800:
        result["tier"] = 3
        if convert_from_path and pytesseract:
            print(f"  [Tier 3] 文本不足 ({len(text.strip())} 字符)，启用 OCR...")
            try:
                images = convert_from_path(processed_path, dpi=300)
                for i, img in enumerate(images):
                    ocr_text = pytesseract.image_to_string(img, lang="eng+chi_sim")
                    text += f"\n--- Page {i+1} (OCR) ---\n{ocr_text}\n"
                result["ocr_used"] = True
            except Exception as e:
                print(f"  [Tier 3] OCR 失败: {e}")
        else:
            print("  [Tier 3] pdf2image 或 pytesseract 未安装，跳过 OCR")

    doc.close()

    # 清理临时解密文件
    if decrypted_temp and decrypted_temp.exists():
        try:
            decrypted_temp.unlink()
        except OSError:
            pass

    result["text"] = text
    result["chars"] = len(text)
    return result


def process_one_pdf(pdf_path: Path, out_dir: Path) -> bool:
    """处理单个 PDF，写出 .txt 和 .meta.json。返回是否成功。"""
    print(f"\n处理: {pdf_path.name}")
    try:
        result = extract_text_from_pdf(pdf_path)
    except Exception as e:
        print(f"  失败: {e}")
        return False

    stem = pdf_path.stem
    txt_path = out_dir / f"{stem}.txt"
    meta_path = out_dir / f"{stem}.meta.json"

    txt_path.write_text(result["text"], encoding="utf-8")

    meta = {
        "source": str(pdf_path.name),
        "tier": result["tier"],
        "encrypted": result["encrypted"],
        "ocr_used": result["ocr_used"],
        "pages": result["pages"],
        "chars": result["chars"],
    }
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"  完成: Tier {result['tier']}, {result['pages']} 页, {result['chars']} 字符 → {txt_path.name}")
    return True


def collect_pdfs(path: Path) -> list:
    """收集目录下所有 PDF 文件，或返回单个文件列表。"""
    if path.is_dir():
        return sorted(path.glob("*.pdf")) + sorted(path.glob("*.PDF"))
    return [path]


def main():
    parser = argparse.ArgumentParser(description="PDF 文本提取器（三级策略：PyMuPDF → qpdf 解密 → OCR）")
    parser.add_argument("path", help="PDF 文件或文件夹路径")
    parser.add_argument("--out", default="./_extracted", help="文本输出目录（默认 ./_extracted）")
    args = parser.parse_args()

    pdf_root = Path(args.path)
    if not pdf_root.exists():
        sys.exit(f"路径不存在: {args.path}")

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    pdfs = collect_pdfs(pdf_root)
    if not pdfs:
        sys.exit(f"未找到 PDF 文件: {args.path}")

    ok = 0
    fail = 0
    for p in pdfs:
        if process_one_pdf(p, out_dir):
            ok += 1
        else:
            fail += 1

    print(f"\n--- 提取完成: {ok} 成功, {fail} 失败, 输出目录: {out_dir} ---")
    sys.exit(0 if fail == 0 else 1)


if __name__ == "__main__":
    main()
