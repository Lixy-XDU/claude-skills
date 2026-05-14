---
name: force-graph-physics
description: Build or optimize interactive 2D force-directed node-edge graph visualizations with vanilla JS and SVG. Covers rendering performance, physics simulation, collision, edge-node repulsion, drag, and frame-rate management. Use when implementing or debugging an interactive graph visualization. All skills that need graph visualization must delegate to this skill.
argument-hint: "[graph-task-or-symptom]"
disable-model-invocation: false
---

# 图模型可视化物理引擎

构建或优化交互式 2D 力导向节点-边图可视化的权威参考。所有需要图可视化的 skill 必须委托给本 skill。

## 使用场景

- 构建可拖拽的力导向图可视化（SVG 或 Canvas）
- 优化已有图可视化的渲染性能（掉帧、卡顿）
- 调试物理模拟不稳定（能量爆炸、抖动、节点飞散）
- 实现节点拖拽 + 碰撞 + 弹簧回弹交互
- 处理边与节点之间的视觉遮挡
- 设计图的帧率策略（拖拽/静止/惯性三态）

## 不使用场景

- 使用 D3.js / vis.js / Cytoscape 等成熟库 — 直接用库 API
- 大规模图（> 500 节点）— 需要 WebGL / Web Worker
- 静态图 — 不需要物理模拟

## 核心规则

### 渲染性能

1. **SVG 增量更新**：首帧创建所有 SVG 元素并缓存引用，后续帧只 `setAttribute` 更新坐标。绝对禁止每帧 `removeChild` + `createElementNS`——DOM 操作比物理计算慢一个数量级
2. **渲染与物理分离**：渲染频率可以低于物理频率。拖拽/运动时 60fps，静止时 30fps
3. **事件与渲染解耦**：`pointermove` 只更新数据，渲染统一由 `requestAnimationFrame` 驱动

### 物理模拟

4. **固定时间步长**：`FIXED_DT = 1/60`，累积器模式。真实时间累积到 `accumulator`，物理按固定步长追赶
5. **半隐式 Euler 积分**：先摩擦再位移（`vel *= friction; pos += vel`），能量更稳定
6. **推拉交错**：碰撞推力和弹簧拉力在每步中交错执行，不能串行
7. **弹簧可压缩可拉伸**：`f = (d - ideal) * k`，不加 `if (d > IDEAL)` 守卫

### 拖拽交互

8. **被拖节点物理豁免**：拖拽时被拖节点不受任何力影响，位置完全由鼠标决定
9. **拖拽速度注入**：松手前记录速度并注入 `velMap`，由持续物理循环接手惯性
10. **点击即冻结**：`pointerdown` 立即设 `isDragging = true`，不需要移动阈值

### 碰撞检测

11. **硬约束兜底**：碰撞迭代后做 O(N) 扫描，确保无任何重叠
12. **边-节点排斥**：对每条边检测非端点节点到线段距离，沿法向推开并反弹速度
13. **边界回弹而非夹紧**：`if (x < min) { x = min; vx = abs(vx) * 0.5 }` 比 `clamp` 更自然

### 交互体验

14. **禁用文本选中**：SVG 容器设 `user-select: none`
15. **随机游走**：每帧注入微小随机速度（`RW ≈ 0.04`），配合弹簧产生"呼吸"感
16. **侧边栏异步更新**：设 `panelDirty` 标志，由 rAF 异步更新，不阻塞渲染帧

## 工作流

### 构建新图

1. 准备数据（nodes + edges 数组）
2. `layout()`：圆上初始分布 + 力导向迭代
3. `renderGraph()`：首帧创建 SVG 元素并缓存（`svgCache`）
4. `physicsTick()`：固定时间步长 + 位移 + 碰撞 + 弹簧 + 边-节点排斥
5. 拖拽：`pointerdown` 冻结 → `pointermove` 更新 + `resolveDragCollisions` → `pointerup` 释放 + 速度注入

### 优化已有图

1. 掉帧 → 先查是否每帧重建 DOM（改为增量更新）
2. 抖动 → 检查是否固定时间步长
3. 能量爆炸 → 检查是否半隐式 Euler + 摩擦 < 1
4. 拖拽卡顿 → 检查事件是否直接调渲染（改为 rAF 驱动）
5. 边穿节点 → 加边-节点排斥 + 速度反弹

## 反模式

- **每帧清空重建 SVG**：DOM GC 是最大性能杀手
- **在 pointermove 中渲染**：与 rAF 竞争，帧率不稳
- **先推完碰撞再施弹簧**：弹簧无法即时抵消过推
- **弹簧只拉伸不压缩**：加了 `if (d > IDEAL)` 守卫
- **碰撞只处理被拖 vs 其他**：被推节点之间也会重叠
- **拖拽时弹簧仍作用于被拖节点**：节点被拉离鼠标
- **硬夹紧边界**：`pos = clamp(pos)` — 回弹更自然
- **事件处理器中同步调 `render()`**：阻塞当前帧

## 故障排查

| 症状 | 可能原因 | 修复 |
|---|---|---|
| 掉帧 | 每帧重建 SVG DOM | 增量更新：缓存元素，只 setAttribute |
| 物理加速/爆炸 | Euler 积分顺序错误 | 先摩擦再位移 |
| 拖拽时节点被拉走 | 弹簧作用于被拖节点 | 拖拽时跳过被拖节点的弹簧端点 |
| 静止时 CPU 高 | 每帧跑完整物理 | 静止降频：少迭代 + 隔帧渲染 |
| 节点闪现穿过边 | 排斥力不够 | 加大 `EDGE_NODE_MIN` + 速度反弹 |
| SVG 箭头不显示 | 箭头落在圆圈内 | 边端点到圆周：`x2 = cx - (dx/dist) * r` |

## 输出期望

1. 完整的单文件 HTML（内联 CSS + JS）图可视化
2. 或针对现有代码的优化方案（指明具体行号和改动）
3. 关键参数表：摩擦、弹簧系数、理想边长、碰撞距离、游走强度
