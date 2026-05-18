# pptx-layout-reverse Claude Code Skill

这是一个用于 **PPTX 版式逆向还原** 的 Claude Code Skill。

它支持两种工作流：

1. 将用户手动编辑过的 PPTX 与已有 `template_layouts_16x9.json` 对比，恢复文本框位置、大小、字体和 slot delta。
2. 在没有模板文件的情况下，直接从现有 PPTX 生成新的 layout 文件，并总结整套 PPT 的布局特点。

## 安装

个人级安装：

```bash
mkdir -p ~/.claude/skills
cp -R pptx-layout-reverse ~/.claude/skills/
```

项目级安装：

```bash
mkdir -p .claude/skills
cp -R pptx-layout-reverse .claude/skills/
```

然后在项目中启动 Claude Code，并调用：

```text
/pptx-layout-reverse outputs/deck.pptx
```

## 能做什么

- 从 `.pptx` 中提取文本框坐标和字体元数据。
- 根据 bbox 中心点距离，把 shape 匹配到已有模板的 slot。
- 识别可能的 OMML 原生公式文本框。
- 计算实际 bbox 与模板 bbox 的 delta。
- 对比“新鲜渲染版”和“用户编辑版”，推断用户的字号/字体偏好变化。
- 在没有现有模板时，直接从 PPTX 生成 `template_layouts_16x9.generated.json`。
- 聚类相似页面，生成可复用 layout。
- 输出 `layout_analysis.md`，总结重复版式、slot 角色、边距、字体、图片/表格/图表/公式使用和整体布局特点。

## 依赖

```bash
python3 -m pip install python-pptx
```

## 常用命令

### 对照已有模板恢复 delta

```bash
python3 .claude/skills/pptx-layout-reverse/scripts/extract_pptx_shapes.py \
  outputs/deck.pptx \
  --output pptx_raw_shapes.json

python3 .claude/skills/pptx-layout-reverse/scripts/recover_layout_deltas.py \
  --raw pptx_raw_shapes.json \
  --layouts layouts/template_layouts_16x9.json \
  --layout-plan layout_plan.json \
  --output layout_deltas.recovered.json
```

### 从现有 PPTX 直接生成 layout 文件

```bash
python3 .claude/skills/pptx-layout-reverse/scripts/reverse_pptx_to_layout.py \
  outputs/deck.pptx \
  --output-dir reverse_layout_out
```

生成文件：

```text
reverse_layout_out/
├── template_layouts_16x9.generated.json
├── layout_plan.generated.json
├── layout_analysis.json
├── layout_analysis.md
└── pptx_slide_slot_model.json
```

## 文件说明

- `SKILL.md`：Claude Code Skill 的中文操作说明。
- `scripts/extract_pptx_shapes.py`：提取 PPTX 原始 shape 数据。
- `scripts/recover_layout_deltas.py`：slot 匹配和 delta 计算。
- `scripts/compare_font_preferences.py`：新鲜渲染版 vs 用户编辑版的字体偏好对比。
- `scripts/reverse_pptx_to_layout.py`：无模板 PPTX → layout JSON + 布局分析。
- `references/pptx_reverse_workflow.md`：原始中文工作流。
- `examples/`：示例输入和输出格式。

## 重要说明

JSON 字段名保持英文，例如 `bbox`、`role`、`kind`、`source_slide_indexes`，这样更便于和渲染脚本、校验脚本或已有模板系统兼容。说明文档、CLI 帮助、终端输出、代码注释和分析报告均已中文化。
