# LAYOUT_SCHEMA.md

`layout_plan.json` 用来选择 PNG 模板页型和填充固定槽位。

## 允许的 layout

```text
title        标题页，对应 标题模板.png
agenda       目录页，对应 目录模板.png
section      子标题 / 章节页，对应 子标题模板.png
one_column   单列页，对应 单列模板.png
two_column   两列页，对应 两列模板.png
three_column 三列页，对应 三列模板.png
image_text   图文 / 多图页，对应 图文模板.png
closing      结尾 / 致谢页，对应 结尾模板.png
```

## 顶层结构

```json
{
  "deck_meta": {
    "title": "",
    "language": "zh-CN",
    "theme": "deep_blue_green_research",
    "template_set": "user_png_templates"
  },
  "slides": [
    {
      "slide_no": 1,
      "layout": "title",
      "title": "",
      "slots": {},
      "speaker_notes": "",
      "evidence_refs": []
    }
  ]
}
```

## 各 layout 的 slots

### title

```json
{
  "title": "主标题",
  "subtitle": "副标题",
  "meta": ["汇报人：XXX", "单位：XXX", "日期：2026.05"]
}
```

### agenda

```json
{
  "items": ["第一部分", "第二部分", "第三部分", "第四部分", "第五部分", "第六部分"]
}
```

### section

```json
{
  "section_no": "01",
  "title": "研究背景",
  "subtitle": "为什么这个问题重要"
}
```

### one_column

```json
{
  "title": "页面标题",
  "body": "正文（无公式时使用）",
  "bullets": ["要点 1", "要点 2", "要点 3"],
  "formula": {
    "kind": "formula",
    "latex": "L = L_{sup} + \\lambda L_{cons}"
  },
  "image": {"image_path": "assets/figures/figure_1.png", "caption": "图注"}
}
```

> **注意**：`body`（y=1.15, h=1.2）与 `formula`（y=1.50, h=1.50）在垂直方向重叠。
> 公式页**只用 formula + bullets**，不要同时使用 body 槽位。无公式页才用 body + bullets。


### two_column

```json
{
  "title": "页面标题",
  "left": {"title": "左侧标题", "body": "左侧正文", "bullets": []},
  "right": {"title": "右侧标题", "body": "右侧正文", "bullets": []}
}
```

也可以在 `left` 或 `right` 中使用 image：

```json
{"image_path": "...", "caption": "..."}
```

### three_column

```json
{
  "title": "页面标题",
  "col_1": {"title": "", "body": "", "bullets": []},
  "col_2": {"title": "", "body": "", "bullets": []},
  "col_3": {"title": "", "body": "", "bullets": []}
}
```

### image_text

```json
{
  "title": "页面标题",
  "main_image": {"image_path": "...", "caption": ""},
  "side_1": {"title": "", "body": ""},
  "side_2": {"title": "", "body": ""},
  "bottom_1": {"title": "", "body": ""},
  "bottom_2": {"title": "", "body": ""}
}
```

### closing

```json
{
  "title": "谢谢",
  "subtitle": "欢迎提问",
  "contact": ""
}
```

## 禁止事项

- 不要写 `x/y/w/h`。
- 不要新增未定义 slot。
- 不要把公式当普通文字。
- 不要把长段落塞入卡片槽位。
- 不要删除 evidence_refs。
- 不要在 text / bullets / caption / inline_meta slot 中嵌入 LaTeX 公式模式（`$...$`、`$$...$$`、`\(...\)`、`\[...\]` 等）。
- 不要在 mixed_box 中使用 `latex` 字段。
- 不要在 text slot 中写入 LaTeX 命令（`\frac`、`\sum`、`\int`、`\lambda` 等）。
- 公式只能放入 `kind` 为 `"formula"` 的 slot。
