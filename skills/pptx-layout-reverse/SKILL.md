---
name: pptx-layout-reverse
description: 将 PowerPoint PPTX 逆向还原为 JSON layout/template 配置。用户想提取文本框坐标、字体样式、slot 匹配、OMML 公式框、layout delta，从现有 PPT 生成 template_layouts_16x9.json，或总结分析版式特点时使用。
allowed-tools: Read Write Edit Bash Glob Grep LS
---

# PPTX 版式逆向还原

## 目的

使用本 Skill 将 `.pptx` 演示文稿逆向为可复用的 JSON 版式/模板配置。

它支持两条工作流：

1. **基于现有模板恢复调整量**：将用户编辑过的 PPTX 与已有 `layouts/template_layouts_16x9.json` 对比，恢复实际文本框 `left/top/width/height`、字体大小/字体名/加粗、slot 匹配、OMML 公式候选，以及 bbox delta。
2. **无模板直接生成 layout**：只给一个现有 PPTX，直接推断可复用 slide layout，生成 slot bbox，输出 `template_layouts_16x9.generated.json`、`layout_plan.generated.json`，并总结整套 PPT 的布局特点。

适用场景：用户在 PowerPoint 中手动调整了文本框位置、字号或排版，希望把这些变化固化到默认模板；或者用户只有一份完成版 PPT，希望反推出可复用的 layout/template JSON。

## 输入文件

如果仓库里已经有明显的文件路径，直接执行，不要反复询问。

### A. 基于现有模板恢复调整量

通常使用：

- 编辑后的 PPTX，例如 `outputs/deck.pptx` 或用户另存的调整版。
- layout 定义，例如 `layouts/template_layouts_16x9.json`。
- 可选的 layout plan，例如 `layout_plan.json`，用于建立 slide index → layout name 映射。
- 可选的新鲜渲染 PPTX，用于和编辑版对比字号偏好。

### B. 无模板直接生成 layout

只需要源 PPTX：

- 现有 PPTX，例如 `input/deck.pptx`、`outputs/deck.pptx` 或用户提供的文件。

## 工作流 A：对照现有模板恢复 delta

1. **检查仓库结构**
   - 查找编辑后的 PPTX、`layouts/template_layouts_16x9.json`、`layouts/theme_tokens.json`、`layout_plan.json`、`scripts/render_deck.py`、`scripts/validate_layout.py`。
   - 除非用户明确要求原地更新，否则不要直接覆盖现有模板 JSON。

2. **提取 PPTX 原始 shape 数据**
   - 使用本 Skill 的 `scripts/extract_pptx_shapes.py`。
   - 坐标单位：EMU → inch，公式为 `value / 914400`。
   - 字号单位：EMU → pt，优先使用 python-pptx 的 `.pt`，否则用 `value / 12700`。
   - 默认跳过 `shape_type == 13` 的图片/背景图；除非用户要求分析图片。

3. **建立 slide → layout name 映射**
   - 优先使用已有 `layout_plan.json`。
   - 也可使用类似 `examples/layout_map.example.json` 的映射文件。
   - 如果没有映射，则把 shape 中心点与所有候选 layout 的 slot 中心点做距离比较，选择平均距离最小的 layout。

4. **Shape → Slot 匹配**
   - 对每个文本 shape 计算 bbox 中心点 `(x + w/2, y + h/2)`。
   - 在选定 layout 内匹配最近的 slot bbox 中心点。
   - 默认距离超过 4 inch 的匹配视为不可靠，归入 unmatched。

5. **公式检测**
   - OMML 原生公式文本框通常有 `text_frame`，但没有文本 runs。
   - 如果 shape 没有 runs，且匹配到 `formula` slot，则标记为原生公式候选。
   - 如果 XML 中包含 `<m:oMath>` 或 `<m:oMathPara>`，也标记为公式候选。

6. **计算 delta**
   - 对每个成功匹配的 shape 计算：
     `[actual_x - template_x, actual_y - template_y, actual_w - template_w, actual_h - template_h]`
   - 正的 x/y 表示右移/下移；正的 w/h 表示变宽/变高。
   - 对重复出现的 layout-slot 样本聚合平均值、中位数和最大绝对偏差。

7. **谨慎处理字体继承**
   - 新鲜渲染的 PPTX 往往有显式 run 级 `font.size`。
   - 用户在 PowerPoint 中编辑后，run 级字号可能变成 `None`，格式转移到段落级或继承样式。
   - 推断用户字号偏好时，优先比较“新鲜渲染版”和“用户编辑版”的 raw shape dump。

## 工作流 B：从现有 PPT 直接生成 layout 文件

当用户说“把现有 PPT 逆向为 layout 文件”“总结布局特点”“从 PPT 生成 template_layouts_16x9.json”“分析这套 PPT 的版式”时，使用本流程。

1. **提取有用内容 shape**
   - 使用 `scripts/reverse_pptx_to_layout.py`。
   - 纳入文本框、表格、图表、图片、OMML/公式候选。
   - 默认排除铺满整页的背景图，因为背景通常不应该成为可复用内容 slot。
   - 只有当背景图本身也是模板的一部分时，才使用 `--include-backgrounds`。

2. **推断 slot 角色**
   - 将 shape 归类为 `title`、`subtitle`、`section_header`、`body`、`formula`、`table`、`chart`、`image`、`caption`、`footer`、`page_number` 等角色。
   - 使用几何位置、字号、文本长度、垂直区域、对象类型等启发式规则。
   - 保留原始 bbox 和文本预览，便于人工检查推断结果。

3. **聚类相似页面为可复用 layout**
   - 对比 role 序列、归一化 bbox 中心点和尺寸。
   - 距离低于阈值的页面合并为同一个 layout。
   - 如果用户希望每页都生成独立 layout，使用 `--no-cluster`。

4. **生成 layout JSON**
   - 输出 `template_layouts_16x9.generated.json`。
   - 每个 slot 包含：
     - `bbox`: `[x, y, width, height]`，单位 inch
     - `role` 和 `kind`
     - 来源 slide index
     - 样本数
     - 稳定性/方差指标
     - 可用时附带 style 摘要：字体名、字号、加粗、颜色、对齐、文本框内边距、自动缩放、自动换行

5. **生成 layout plan**
   - 输出 `layout_plan.generated.json`，把每个源 slide index 映射到生成的 layout name。

6. **总结布局特点**
   - 输出 `layout_analysis.json` 和 `layout_analysis.md`。
   - 总结页数、layout 数量、layout 使用情况、slot 角色分布、按角色统计的字体、典型边距、重复版式、单栏/多栏结构、图片/表格/图表/公式区，以及启发式推断的不确定性。

7. **采用前必须复核**
   - 自动生成的 layout 名称和 slot 角色是建议值。
   - 用户确认前，不要替换生产环境的 `template_layouts_16x9.json`。
   - 如果仓库里有 render/validate 脚本，生成后应渲染一版新 PPT，并再次抽取对比。

## 推荐命令

### A. 对照现有模板恢复 delta

在目标仓库根目录执行：

```bash
python3 -m pip install python-pptx

python3 .claude/skills/pptx-layout-reverse/scripts/extract_pptx_shapes.py \
  outputs/deck.pptx \
  --output pptx_raw_shapes.json

python3 .claude/skills/pptx-layout-reverse/scripts/recover_layout_deltas.py \
  --raw pptx_raw_shapes.json \
  --layouts layouts/template_layouts_16x9.json \
  --layout-plan layout_plan.json \
  --output layout_deltas.recovered.json
```

分析字体偏好时，使用新鲜渲染版和用户编辑版：

```bash
python3 .claude/skills/pptx-layout-reverse/scripts/extract_pptx_shapes.py \
  outputs/fresh_deck.pptx \
  --output fresh_raw_shapes.json

python3 .claude/skills/pptx-layout-reverse/scripts/compare_font_preferences.py \
  --fresh fresh_raw_shapes.json \
  --edited pptx_raw_shapes.json \
  --output font_preferences.recovered.json
```

### B. 从现有 PPTX 直接生成 layout 文件

```bash
python3 -m pip install python-pptx

python3 .claude/skills/pptx-layout-reverse/scripts/reverse_pptx_to_layout.py \
  outputs/deck.pptx \
  --output-dir reverse_layout_out
```

预期输出：

```text
reverse_layout_out/
├── template_layouts_16x9.generated.json
├── layout_plan.generated.json
├── layout_analysis.json
├── layout_analysis.md
└── pptx_slide_slot_model.json
```

常用选项：

```bash
# 不聚类相似页面，每页生成一个 layout
python3 .claude/skills/pptx-layout-reverse/scripts/reverse_pptx_to_layout.py \
  outputs/deck.pptx \
  --output-dir reverse_layout_out \
  --no-cluster

# 把整页背景图也作为 slot 纳入 layout
python3 .claude/skills/pptx-layout-reverse/scripts/reverse_pptx_to_layout.py \
  outputs/deck.pptx \
  --output-dir reverse_layout_out \
  --include-backgrounds

# 调整相似页面合并阈值；数值越小越严格
python3 .claude/skills/pptx-layout-reverse/scripts/reverse_pptx_to_layout.py \
  outputs/deck.pptx \
  --output-dir reverse_layout_out \
  --cluster-threshold 0.05
```

## 汇报标准

### A. 恢复 delta 时，汇报：

- 源 PPTX 路径和 layout JSON 路径。
- 分析的 slide 数和文本 shape 数。
- 匹配/未匹配 shape 数。
- layout-slot delta 的表格或 JSON 摘要。
- 公式候选。
- 字号、字体名、加粗变化，并标注置信度。
- 写出的文件路径。
- 明确说明是否未自动应用模板更新。

### B. 生成 layout 时，汇报：

- 源 PPTX 路径。
- 输出目录和具体文件。
- slide 数、生成 layout 数、内容 slot 数。
- 重复 layout 及其来源 slide index。
- 主要布局特点：标题/正文结构、单栏/多栏、图片/图表/表格/公式 slot、页脚/页码、典型边距、字体模式。
- 提醒用户：slot 名称、角色和聚类均为启发式结果，替换生产模板前需要复核。

## 与 paper-note-to-ppt-template 协同：PPT 排版闭环

两个技能构成一条完整的"生成→调整→逆向→校准"闭环：

```text
                        ┌─────────────────────────┐
                        │ paper-note-to-ppt-template │
                        │  生成 deck.pptx（模板渲染）  │
                        └────────────┬────────────┘
                                     ↓
                        ┌─────────────────────────┐
                        │   用户打开 PPT 手动调整     │
                        │  （改位置、改字号、改间距）   │
                        └────────────┬────────────┘
                                     ↓
                        ┌─────────────────────────┐
                        │    pptx-layout-reverse    │
                        │  逆向提取实际坐标和字号      │
                        └────────────┬────────────┘
                                     ↓
                        ┌─────────────────────────┐
                        │   对比模板基准，计算 delta   │
                        │   输出 layout_deltas.json  │
                        └────────────┬────────────┘
                                     ↓
                        ┌─────────────────────────┐
                        │  回写更新模板参数 JSON       │
                        │  - template_layouts_16x9   │
                        │  - theme_tokens            │
                        └────────────┬────────────┘
                                     ↓
                        ┌─────────────────────────┐
                        │ paper-note-to-ppt-template │
                        │    重新渲染，校准生效       │
                        └─────────────────────────┘
```

### 何时走这个闭环

- 用户打开生成的 PPT 后发现某个 slot 文本框偏移 → 手动对齐 → 逆提取 delta → 更新 bbox
- 用户觉得字号整体偏小 → 手动放大 → 逆提取字体偏好 → 更新 theme_tokens.json
- 模板 PNG 换新版后卡片位置变化 → 手动对齐所有 slot → 逆提取整批 delta → 批量更新

### 闭环操作命令

```bash
# 1. 生成 PPTX（paper-note-to-ppt-template）
python3 scripts/render_deck.py layout_plan.json \
  layouts/template_layouts_16x9.json layouts/theme_tokens.json \
  templates deck.pptx

# 2. 用户手动调整后，逆提取（pptx-layout-reverse）
python3 ../pptx-layout-reverse/scripts/extract_pptx_shapes.py \
  deck.pptx --output pptx_raw_shapes.json

# 3. 与模板对比，计算 delta
python3 ../pptx-layout-reverse/scripts/recover_layout_deltas.py \
  --raw pptx_raw_shapes.json \
  --layouts layouts/template_layouts_16x9.json \
  --output layout_deltas.recovered.json

# 4. 根据 delta 更新 template_layouts_16x9.json 和 theme_tokens.json

# 5. 重新渲染验证（回到步骤 1）
```

## 配套文件

- `scripts/extract_pptx_shapes.py`：提取坐标、文本、run 字体、段落字体、文本框元数据和 shape 元数据。
- `scripts/recover_layout_deltas.py`：把 shape 匹配到现有模板 slot，并计算 delta 和补丁建议。
- `scripts/compare_font_preferences.py`：对比新鲜渲染版和用户编辑版，推断字体变化。
- `scripts/reverse_pptx_to_layout.py`：从现有 PPTX 直接生成 layout 文件和布局分析。
- `references/pptx_reverse_workflow.md`：原始工作流说明。
- `examples/`：示例输入和输出格式。

## 注意事项

- 不要静默覆盖用户的 layout/theme 文件。
- 不要把 `font.size == None` 简单理解成“没有字号变化”；应检查段落字体，并尽可能和新鲜渲染版对比。
- 不要默认相信最近 slot 匹配；需要输出距离和置信度。
- 不要忽略未匹配 shape；应列出以便人工复核。
- 输出 JSON 中的坐标统一用 inch，字号统一用 pt。
- 无模板生成 layout 时，必须说明 slot 角色和 layout 聚类是启发式结果。
- 默认排除整页背景图，除非用户明确希望背景图也成为 slot。
