---
name: paper-note-to-ppt-template
# 注意：description 要让 Claude Code 能在用户说“论文/笔记转 PPT、套模板、科研风格、组会汇报”等需求时自动启用本 Skill。
description: 使用用户提供的一套 PNG 背景模板，将论文、PDF、Markdown 笔记、研究笔记转换为科研风格 PowerPoint。适用于论文转 PPT、笔记转 PPT、组会汇报、journal club、课题汇报、开题/中期/答辩。该 Skill 使用固定模板图片作为每页背景，并按预设槽位叠加文字、公式和图片，避免自由排版导致的文字与卡片冲突。
argument-hint: "[输入文件或目录路径] [汇报场景、语言、页数、风格要求]"
allowed-tools: Read Write Edit Glob Grep Bash(python3 *)
---

# 论文 / 笔记转 PPT：PNG 模板套装版

你是一个“论文/笔记转科研 PPT”的工作流执行器。

本 Skill 使用用户提供的一套 PNG 模板作为整页背景图，然后在模板预留区域内叠加文字、图片、公式和图表。

核心原则：

> 模板负责视觉风格；layout 槽位负责位置；Claude 负责内容；renderer 负责稳定生成 PPT。

绝对不要让 Claude 随意创建坐标、随意移动文本框或把文字硬塞进背景卡片。

---

## 一、用户需要放入的模板文件

模板目录：

```text
${CLAUDE_SKILL_DIR}/templates/
```

该目录当前可以为空。用户后续自行放入以下 PNG 文件：

```text
标题模板.png
目录模板.png
子标题模板.png
单列模板.png
两列模板.png
三列模板.png
图文模板.png
结尾模板.png
```

文件名需要尽量保持一致。也支持 `.jpg` / `.jpeg`，但推荐 `.png`。

所有模板建议为 16:9 横版，例如：

```text
1920 × 1080
2560 × 1440
3840 × 2160
```

---

## 二、适用场景

当用户要求以下任务时使用本 Skill：

- 论文转 PPT
- PDF 转 PPT
- Markdown 笔记转 PPT
- 研究笔记转科研汇报
- 中文组会
- journal club
- 课题汇报
- 文献阅读汇报
- 开题答辩 / 中期答辩 / 毕业答辩
- 把已有内容套入科研风格模板

---

## 三、默认参数

如果用户没有指定，使用：

```json
{
  "language": "zh-CN",
  "audience": "具备基础科研或技术背景的听众",
  "scenario": "academic_report",
  "target_slide_count": 12,
  "style": "简约科研风，深蓝主色，绿色辅助色",
  "aspect_ratio": "16:9",
  "output_dir": "outputs/paper-note-to-ppt-template"
}
```

---

## 四、完整链路

必须按以下链路执行：

```text
输入论文 / 笔记
  ↓
1. ingest：解析输入材料
  ↓
clean_notes.md
  ↓
2. content planning：生成内容计划
  ↓
content_plan.json
  ↓
3. layout planning：选择模板页型和固定槽位
  ↓
layout_plan.json
  ↓
4. validate：检查模板文件、slot、文本长度、公式、图片
  ↓
validation_report.json
  ↓
5. render：模板图片作为背景，槽位叠加内容
  ↓
deck.pptx
  ↓
6. final validation：检查 PPT 输出
  ↓
最终交付
```

---

## 五、输出目录

输出到：

```text
outputs/paper-note-to-ppt-template/
```

生成文件：

```text
outputs/paper-note-to-ppt-template/
├── deck.pptx
├── clean_notes.md
├── content_plan.json
├── layout_plan.json
├── validation_report.json
├── final_report.md
├── speaker_notes.md
├── source_map.md
└── assets/
    ├── formulas/
    ├── figures/
    └── previews/
```

---

## 六、第一步：检查模板

在生成 PPT 之前，必须先检查模板目录：

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/validate_templates.py \
  ${CLAUDE_SKILL_DIR}/templates \
  ${CLAUDE_SKILL_DIR}/layouts/template_layouts_16x9.json \
  outputs/paper-note-to-ppt-template/template_check.json
```

如果模板缺失，不要继续渲染最终 PPT。向用户说明缺少哪些文件。

允许继续生成 `content_plan.json` 和 `layout_plan.json`，但最终 `deck.pptx` 需要模板齐全后再生成。

---

## 七、第二步：解析输入材料

如果输入是 PDF / Markdown / txt，运行：

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/ingest.py \
  "$INPUT_PATH" \
  outputs/paper-note-to-ppt-template/clean_notes.md
```

解析目标：

- 论文标题
- 摘要
- 研究问题
- 背景动机
- 方法贡献
- 方法流程
- 关键公式
- 实验设置
- 主要结果
- 消融分析
- 局限性
- 未来工作
- 可讨论问题

如果 `ingest.py` 提取不完整，Claude 应继续读取源文件，并补全 `clean_notes.md`。

---

## 八、第三步：生成 content_plan.json

`content_plan.json` 只描述“每页讲什么”，不描述坐标。

格式见：

```text
${CLAUDE_SKILL_DIR}/CONTENT_SCHEMA.md
```

基本要求：

- 每页一个核心观点。
- 标题尽量使用结论式标题。
- 不要复制论文长段落。
- 论文事实、实验数字、公式、图表必须保留来源引用。
- 不要编造论文不存在的结论。
- 如果页面内容过多，拆页，不要硬塞。

---

## 九、第四步：生成 layout_plan.json

`layout_plan.json` 只能从模板页型中选择：

```text
title              → 标题模板.png
agenda             → 目录模板.png
section            → 子标题模板.png
one_column         → 单列模板.png
two_column         → 两列模板.png
three_column       → 三列模板.png
image_text         → 图文模板.png
closing            → 结尾模板.png
```

必须读取：

```text
${CLAUDE_SKILL_DIR}/LAYOUT_SCHEMA.md
${CLAUDE_SKILL_DIR}/layouts/template_layouts_16x9.json
${CLAUDE_SKILL_DIR}/layouts/theme_tokens.json
```

输出：

```text
outputs/paper-note-to-ppt-template/layout_plan.json
```

### 页型选择规则

- 标题页：`title`
- 目录页：`agenda`
- 章节过渡页：`section`
- 单一大图、单一大段观点、公式解释：`one_column`
- 左文右图、问题 vs 方法、方法 vs 结果：`two_column`
- 三个贡献、三个阶段、三个发现、三个局限：`three_column`
- 多图展示、主图 + 辅助图、实验结果图组：`image_text`
- 致谢 / 结尾 / Q&A：`closing`

---

## 十、layout_plan 示例

```json
{
  "deck_meta": {
    "title": "论文解读：弱监督训练方法",
    "language": "zh-CN",
    "theme": "deep_blue_green_research",
    "template_set": "user_png_templates"
  },
  "slides": [
    {
      "slide_no": 1,
      "layout": "title",
      "title": "弱监督训练降低了标注成本",
      "slots": {
        "title": "弱监督训练降低了标注成本",
        "subtitle": "论文阅读汇报｜方法、实验与局限",
        "meta": ["汇报人：XXX", "单位：XXX", "日期：2026.05"]
      },
      "speaker_notes": "开场说明本文关注如何降低高质量标注数据需求。"
    },
    {
      "slide_no": 2,
      "layout": "agenda",
      "title": "目录",
      "slots": {
        "items": [
          "研究背景",
          "问题定义",
          "方法总览",
          "实验结果",
          "局限分析",
          "总结讨论"
        ]
      }
    },
    {
      "slide_no": 3,
      "layout": "three_column",
      "title": "论文贡献可以拆成三个层次",
      "slots": {
        "col_1": {
          "title": "问题",
          "body": "高质量标注数据昂贵，限制模型扩展。"
        },
        "col_2": {
          "title": "方法",
          "body": "先弱监督预训练，再少量标注微调。"
        },
        "col_3": {
          "title": "结果",
          "body": "在多个任务上接近全监督效果。"
        }
      },
      "evidence_refs": ["abstract", "section 4"]
    }
  ]
}
```

---

## 十一、严格排版约束

必须遵守：

1. 不允许在 `layout_plan.json` 中写任意 `x / y / w / h` 坐标。
2. 不允许创建 layout 中不存在的 slot。
3. 不允许直接在 PPT 上自由画文本框。
4. 模板 PNG 作为整页背景，不要重新绘制模板的卡片框。
5. 文本只放入预设槽位。
6. 公式必须放入 `kind="formula"` 的槽位，通过 `render_formula.py` 渲染为 PNG 图片后等比缩放插入。python-pptx 不支持 OMML 原生公式。
7. 图片必须 contain 等比缩放，不允许拉伸变形。
8. 不允许把字号缩到 12pt 以下。
9. 内容放不下时，必须压缩、拆页或移到 speaker notes。
10. 不要删除 `evidence_refs`。

特别重要：

> 由于模板中已经有卡片框 / 图案 / 背景，renderer 默认只叠加透明文本，不再额外画卡片背景，避免文字和卡片冲突。

---

## 十二、公式处理

公式通过 Matplotlib 渲染为透明背景 PNG 图片，等比缩放后插入公式槽位。

### 公式槽位标准格式

```json
{
  "kind": "formula",
  "latex": "L = L_{sup} + \\lambda L_{consistency}",
  "fallback": "image"
}
```

| 字段 | 必填 | 说明 |
|------|------|------|
| `kind` | 是 | 固定为 `"formula"` |
| `latex` | 是 | LaTeX 源码，由 `render_formula.py` 渲染为 PNG |
| `image_path` | 否 | 预渲染公式图片路径（替代 latex 字段） |

### 渲染流程

renderer 会：

1. 使用 `render_formula.py`（Matplotlib）将 LaTeX 转为透明 PNG。
2. 按槽位 contain 等比缩放。
3. 居中插入。

### 公式规则

- 公式只能放入 `kind="formula"` 的槽位（当前仅 `one_column` 布局有此槽位）。
- 一个 slide 最多一个主公式。
- 复杂长公式拆成多页。
- 公式下方必须有解释（放入 bullets 槽位）。
- 公式来源写入 `evidence_refs`。
- 不要将 LaTeX 字符串直接写入 text / bullets / caption / mixed_box 槽位。

---

## 十三、渲染 PPT

布局校验通过后，运行：

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/render_deck.py \
  outputs/paper-note-to-ppt-template/layout_plan.json \
  ${CLAUDE_SKILL_DIR}/layouts/template_layouts_16x9.json \
  ${CLAUDE_SKILL_DIR}/layouts/theme_tokens.json \
  ${CLAUDE_SKILL_DIR}/templates \
  outputs/paper-note-to-ppt-template/deck.pptx
```

---

## 十四、最终检查

PPT 生成后运行：

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/validate_deck.py \
  outputs/paper-note-to-ppt-template/deck.pptx \
  outputs/paper-note-to-ppt-template/layout_plan.json \
  outputs/paper-note-to-ppt-template/final_report.md
```

检查内容：

- PPT 是否生成
- 页数是否符合预期
- 是否缺模板
- 是否缺图片
- 是否缺公式
- 是否缺 speaker notes
- 是否缺 evidence refs
- 是否存在明显过长文本

---

## 十五、讲稿与来源映射

必须生成：

```text
outputs/paper-note-to-ppt-template/speaker_notes.md
outputs/paper-note-to-ppt-template/source_map.md
```

讲稿要求：

- 用口语解释，不逐字念 bullet。
- 每页 30–90 秒。
- 公式页先讲直觉，再讲变量。
- 结果页讲“数字说明什么”。

来源映射要求：

- 每个关键结论都能追溯到原文。
- 实验数字和公式必须标注来源。
- 不确定的信息标注“需要人工确认”。

---

## 十六、失败处理

### 模板缺失

停止生成 PPT，列出缺失文件；仍可生成内容计划和布局计划。

### 文本太长

压缩内容、拆页或移到 speaker notes，不要缩小字体硬塞。

### 公式太长

拆成多个公式页，或只展示核心项。

### 图太多

使用 `image_text` 页型，或拆成多页。

### 图表太复杂

优先用 callout 解释重点，不要塞很多小字。

---

## 十七、与 pptx-layout-reverse 协同：排版闭环

生成 PPT 不是终点。与 `pptx-layout-reverse` 配合可形成校准闭环：

```text
本 Skill 生成 deck.pptx → 用户手动调整排版 → pptx-layout-reverse 逆提取 delta → 回写模板 JSON → 本 Skill 重新渲染
```

### 闭环使用场景

- 首次用新模板生成 PPT 后，打开检查各 slot 文本框是否对齐卡片，手动调整后逆提取 delta 固化
- 换了一套模板 PNG，卡片位置变了，需要重新对齐所有 bbox
- 觉得默认字号偏小/偏大，手动调整后逆提取字体偏好更新 theme_tokens.json

### 操作命令

```bash
# 1. 本 Skill：生成 PPT
python3 scripts/render_deck.py layout_plan.json ... deck.pptx

# 2. 用户在 PPT 中手动调整位置/字号后
# 3. 切换到 pptx-layout-reverse 做逆向和 delta 提取

# 4. 更新 template_layouts_16x9.json / theme_tokens.json 后
# 5. 本 Skill：重新渲染，校准生效
```

---

## 十八、最终回复格式

完成后回复：

```md
已生成套用 PNG 模板的科研汇报 PPT。

输出文件：

- PPT：outputs/paper-note-to-ppt-template/deck.pptx
- 内容计划：outputs/paper-note-to-ppt-template/content_plan.json
- 布局计划：outputs/paper-note-to-ppt-template/layout_plan.json
- 校验报告：outputs/paper-note-to-ppt-template/final_report.md
- 讲稿：outputs/paper-note-to-ppt-template/speaker_notes.md
- 来源映射：outputs/paper-note-to-ppt-template/source_map.md

处理摘要：

- 模板目录：
- 目标页数：
- 实际页数：
- 使用页型：
- 缺失模板：
- 需要人工确认：
```

不要只说”完成了”。

---

## 十九、项目目录与输出规范

### 项目顶层只保留 5 类文件

```text
<项目名>/
├── clean_notes.md          ← 论文笔记（可复用）
├── deck-template.pptx      ← 最终 PPT（复制一份到顶层方便打开）
├── source_map.md           ← 来源映射
├── speaker_notes.md        ← 讲稿
├── assets/
│   ├── figures/            ← 论文原图
│   └── formulas/           ← 公式渲染 PNG
└── outputs/
    └── paper-note-to-ppt-template/  ← 完整构建输出
        ├── deck.pptx
        ├── content_plan.json
        ├── layout_plan.json
        ├── validation_report.json
        ├── final_report.md
        ├── formula_report.json
        └── assets/
            ├── figures/    ← 原图副本（渲染时需要）
            └── formulas/
```

- 渲染完成后，将 `outputs/paper-note-to-ppt-template/deck.pptx` 复制一份到项目顶层，命名为 `deck-template.pptx`，方便直接打开。
- 项目顶层不要残留旧 skill（paper-note-to-ppt）生成的 `content_plan.json`、`layout_plan.json` 等中间文件。
- `outputs/ppt-polish/` 等中间产物在确认 PPT 无误后可以删除。

---

## 二十、已调优的排版参数

以下参数是经过实际 PPT 打开调整验证的，不要随意改动。

### 字号（theme_tokens.json）

| 样式 | 字号 | 用途 |
|------|------|------|
| cover_title | 54pt | 封面主标题 |
| cover_subtitle | 22pt | 封面副标题 |
| meta | 13pt | 封面元信息行 |
| slide_title | 22pt | 内容页标题 |
| section_no | 24pt | 章节编号 |
| section_title | 28pt | 章节标题 |
| section_subtitle | 18pt | 章节副标题 |
| box_title | 20pt | 卡片标题 |
| box_body / box_text | 18pt | 卡片正文 |
| body | 18pt | 页面正文 |
| bullet | 18pt | 列表项 |
| agenda | 28pt | 目录项 |
| caption | 10pt | 图片标注 |
| closing_title | 72pt | 结尾致谢 |
| closing_subtitle | 18pt | 结尾副标题 |

### 模板 bbox 调整（template_layouts_16x9.json）

- **agenda**：6 个条目框从 `(1.55, 1.73)` 右移至 `(2.44, 1.94)`，对齐实际模板 PNG 卡片位置。
- **title**：封面标题宽度从 7.2in 加宽至 9.15in，容纳 54pt 中文标题。
- **closing**：标题从 `(3.25, 3.20)` 上移至 `(3.25, 2.50)`，副标题同步上移。

### 渲染参数（render_deck.py）

- **背景透明度**：模板 PNG 以 80% 不透明度（20% 透明）叠加，通过 `alphaModFix amt=”80000”` 实现。
- **mixed_box 标题**：从容器顶部 `bbox[1] + 0` 开始（不再 +0.18in 偏移），标题高度 0.44in。
- **图片 caption**：有 caption 时图片区域底部预留 0.35in，caption 不跑出框外。
- **公式页**：`one_column` 的 formula 槽位和 body 槽位存在垂直重叠——公式页只用 formula + bullets，不要同时使用 body 槽位。

