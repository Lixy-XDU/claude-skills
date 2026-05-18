# PPTX → JSON 逆向还原工作流

## 目的

当用户手动在 PowerPoint 中调整了文本框位置、字体大小等排版参数后，通过逆向读取 `.pptx` 文件，将实际排版参数还原为 JSON 配置，从而更新 Skill 的默认模板参数。

## 方法

利用 python-pptx 读取 PPTX 中每个 shape 的绝对坐标（`left/top/width/height`）和文本样式（`font.size/font.name/font.bold`），与 `template_layouts_16x9.json` 中定义的 slot bbox 做匹配，还原出 `layout_plan.json` 结构和实际的排版偏差。

## 步骤

### 1. 提取所有 shape 的绝对坐标和字体

```python
from pptx import Presentation
prs = Presentation('deck.pptx')

for slide in prs.slides:
    for shape in slide.shapes:
        # 跳过背景图片 (shape_type == 13)
        x_in = shape.left / 914400   # EMU → inch
        y_in = shape.top / 914400
        w_in = shape.width / 914400
        h_in = shape.height / 914400

        # 文本和字体
        if shape.has_text_frame:
            for p in shape.text_frame.paragraphs:
                for r in p.runs:
                    size_pt = r.font.size / 12700  # EMU → pt
                    font_name = r.font.name
                    is_bold = r.font.bold
```

### 2. Shape → Slot 匹配

用 shape 中心点匹配最近的 slot bbox（欧几里得距离）：

```python
def bbox_center(bbox):
    return (bbox[0] + bbox[2]/2, bbox[1] + bbox[3]/2)

def match_slot(shape_cx, shape_cy, layout_name, all_layouts):
    best_slot, best_dist = None, float('inf')
    for sname, spec in all_layouts[layout_name]['slots'].items():
        bc = bbox_center(spec['bbox'])
        d = ((shape_cx - bc[0])**2 + (shape_cy - bc[1])**2) ** 0.5
        if d < best_dist:
            best_dist = d
            best_slot = sname
    return best_slot if best_dist < 4.0 else None  # 超过 4 inch 视为不匹配
```

### 3. 公式检测

OMML 原生公式的 TextBox 有 `text_frame` 但无 `runs`（文本 runs 为空），且位于 `formula` slot 的 bbox 附近：

```python
has_runs = any(p.runs for p in shape.text_frame.paragraphs)
if not has_runs and matched_slot == 'formula':
    # 这是 OMML 原生公式
```

### 4. 输出 delta（用户调整量）

```python
delta = [
    actual_x - template_x,
    actual_y - template_y,
    actual_w - template_w,
    actual_h - template_h,
]
# 正值 = 右移/下移/变宽/变高
```

## 关键发现

### 字体问题

- 新鲜渲染的 PPTX 中，所有 run 级 `font.size` 都是显式设定的
- 用户在 PPT 中编辑后，PPT 会**清除 run 级字号**（变为 `None`/inherit），将格式移到段落级
- 对比新鲜渲染 vs 用户修改版的字号差异，就能提取用户偏好

### 位置问题

- 用户通常不会大幅移动文本框，位置 delta 大多 < 0.05 inch
- 高度差异通常来自 PPT 的自动收缩（auto-fit）

## 使用示例

```bash
# 1. 提取 PPTX 所有 shape 原始数据
cd paper-note-to-ppt-template
python3 -c "
from pptx import Presentation
import json
prs = Presentation('outputs/deck.pptx')
# ... 提取逻辑 ...
json.dump(result, open('pptx_raw_shapes.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
"

# 2. 对比 template_defaults 和 actual，计算 delta
# 3. 更新 theme_tokens.json 或 template_layouts_16x9.json
```

## 相关文件

| 文件 | 作用 |
|------|------|
| `layouts/theme_tokens.json` | 字体大小、颜色、粗体等样式定义 |
| `layouts/template_layouts_16x9.json` | 各 slot 的 bbox 位置和约束 |
| `scripts/render_deck.py` | 渲染引擎 |
| `scripts/validate_layout.py` | 布局校验 |
