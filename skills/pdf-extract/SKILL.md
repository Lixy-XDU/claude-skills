---
name: pdf-extract
description: 从 PDF 文件中提取纯文本，支持加密 PDF（qpdf 解密）与扫描版 OCR。三级策略：PyMuPDF 直接提取 → qpdf 解密 → tesseract OCR。适用场景：任何 skill 需要从 PDF 获取文本时，委托给本 skill 处理，禁止各 skill 自行实现 PDF 解析。
argument-hint: "[pdf-path]"
disable-model-invocation: true
---

# PDF 文本提取

提供 PDF 文本提取的单一入口。任何 skill 需要从 PDF 获取文本内容时，调用本 skill 的提取脚本，不自行实现 PyMuPDF / qpdf / OCR 逻辑。

核心流程：

```text
PDF 路径 → pdf_extractor.py → .txt（纯文本）+ .meta.json（提取元信息）
```

## 使用场景

- 任何 skill 或任务需要从 PDF 提取文本
- PDF 是加密的（需要 qpdf 解密）
- PDF 是扫描版（需要 OCR）
- 需要知道 PDF 的提取质量（走的是 Tier 1/2/3）

## 不使用场景

- 只需要读 PDF 元数据（页数、作者等）→ 直接用 Read 工具
- PDF 已经是纯文本格式 → 直接读
- 用户只是想查看 PDF 内容而非提取入库 → 直接用 Read 工具

## 脚本位置

```text
~/.claude/skills/pdf-extract/scripts/pdf_extractor.py
```

Skill 执行时，用相对于 SKILL.md 所在目录的路径调用：

```text
<SKILL_DIR>/scripts/pdf_extractor.py
```

## 路径询问协议

按 CLAUDE.md 第 2 节规则，首次使用前向用户询问 PDF 路径。若 `config.local.yaml` 中已配置 `tools.qpdf` / `tools.tesseract`，优先使用配置值。

> 请提供 PDF 文件或文件夹路径（Windows 格式，如 `D:\xxx\yyy`）：

## 脚本调用协议

### 调用方式

Windows 下 `python` 和 `py` 可能只有一个可用。**先尝试 `python`，失败则尝试 `py`**：

```bash
python "<SKILL_DIR>/scripts/pdf_extractor.py" "<pdf-path>" --out "<text-output-dir>" || py "<SKILL_DIR>/scripts/pdf_extractor.py" "<pdf-path>" --out "<text-output-dir>"
```

PowerShell 示例：

```powershell
python "$env:USERPROFILE\.claude\skills\pdf-extract\scripts\pdf_extractor.py" `
    "D:\Papers\paper.pdf" `
    --out ".\_extracted"
```

### 输入/输出约定

- **位置参数**：PDF 文件路径或包含 PDF 的目录
- **`--out`**：文本输出目录（可选，默认 `./_extracted`，相对于当前工作目录）
- **输出**：
  - 每个 PDF 对应 `<stem>.txt`（纯文本，含页分隔符）
  - `<stem>.meta.json`（元信息：tier、encrypted、ocr、pages、chars）
- **退出码**：`0` 成功，非 `0` 失败（stderr 有原因）

### meta.json 格式

```json
{
  "source": "paper.pdf",
  "tier": 1,
  "encrypted": false,
  "ocr_used": false,
  "pages": 18,
  "chars": 42315
}
```

## 三级读取策略

| 级别 | 触发条件 | 处理方式 |
|---|---|---|
| Tier 1 普通 PDF | 能直接抽文本 | PyMuPDF (`fitz.open().get_text()`) |
| Tier 2 加密 PDF | PyMuPDF 报加密 / 文本异常 | `qpdf --decrypt` 先解密再抽文本；失败则询问密码 |
| Tier 3 扫描 PDF | 抽到的文本字符数 < 阈值（默认 800） | `pdf2image` + `pytesseract`（`eng+chi_sim`，300 dpi） |

## 依赖（Windows）

```powershell
# Python 依赖
pip install pymupdf pdf2image pillow pytesseract

# 系统工具
choco install qpdf
choco install tesseract
```

## 反模式

- 在各自 skill 里自行实现 `fitz.open()` / `qpdf` / `pytesseract` 调用 — 应一律调本 skill 脚本
- 硬编码绝对路径调用脚本 — 必须用相对于 SKILL.md 的相对定位
- 忽略 `meta.json` 的 tier 字段 — Tier 3 OCR 结果需要额外警惕公式识别质量
- 不检查脚本退出码就继续处理 — 提取失败应终止或提示用户

## 调用示例（在其他 skill 中）

在 `literature-paper-reading` 或 `literature-to-math` 等消费方 skill 中：

```text
1. 调 pdf-extract 脚本: python <pdf-extract>/scripts/pdf_extractor.py <pdf> --out <dir>
2. 检查退出码和 meta.json
3. 读取 .txt 进行后续处理
4. 若 tier==3，标注 OCR 不确定性
```

## 输出期望

1. 每个输入 PDF 对应 `<stem>.txt` + `<stem>.meta.json`
2. 终端输出处理摘要（文件名、tier、页数、字符数）
3. 退出码正确反映成败

---

## Index handoff

Recommended category: 工具
Recommended scope: personal
Recommended path: ~/.claude/skills/pdf-extract/SKILL.md

Index entry:

| `pdf-extract` | personal | PDF 文本提取（三级策略：PyMuPDF → qpdf 解密 → OCR），供其他 skill 委托调用 | `/pdf-extract` |
