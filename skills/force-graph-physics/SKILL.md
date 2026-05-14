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

1. **SVG 增量更新**：首帧创建所有 SVG 元素并缓存引用（`svgCache`），后续帧只 `setAttribute` 更新坐标。绝对禁止每帧 `removeChild` + `createElementNS`——DOM 操作比物理计算慢一个数量级
2. **渲染与物理分离**：渲染频率可以低于物理频率。拖拽/运动时 60fps，静止时 30fps
3. **事件与渲染解耦**：`pointermove` 只更新数据，渲染统一由 `requestAnimationFrame` 驱动

### 物理模拟

4. **固定时间步长**：`FIXED_DT = 1/60`，累积器模式。真实时间累积到 `accumulator`，物理按固定步长追赶
5. **半隐式 Euler 积分**：先摩擦再位移（`vel *= friction; pos += vel`），能量更稳定
6. **推拉交错**：碰撞推力和弹簧拉力在每步中交错执行，不能串行
7. **弹簧可压缩可拉伸**：`f = (d - ideal) * k`，不加 `if (d > IDEAL)` 守卫

### 分类力学（核心新增）

8. **同分类平方正比引力**：同 category 节点间施加 `f = d² * k`（`k ≈ 0.00003`），距离越远引力越强，形成自然聚类
9. **异分类平方反比斥力**：不同 category 节点间施加 `f = C / d²`（`C ≈ 6000`），同分类聚拢的同时保持分类间分离
10. **分类优先级**：分类力 > 边弹簧力（`k_cat=0.00003` vs `k_edge=0.005`），聚类优先于拓扑连接

### 拖拽交互

11. **被拖节点物理豁免**：拖拽时被拖节点不受任何力影响，位置完全由鼠标决定
12. **拖拽速度注入**：松手前记录速度并注入 `velMap`，由持续物理循环接手惯性
13. **选中即冻结**：点击选中节点后，该节点不参与随机游走、Euler 位移、碰撞、弹簧及分类力。其他节点仍会绕开它（碰撞检测中冻结节点作为障碍物但不位移）

### 碰撞检测

14. **硬约束兜底**：碰撞迭代后做 O(N) 扫描，确保无任何重叠
15. **边界回弹而非夹紧**：`if (x < min) { x = min; vx = abs(vx) * 0.5 }` 比 `clamp` 更自然
16. **节点半径缩放**：默认节点极小（5-6px），MIN_DIST 同步缩小至 20px。选中节点放大 4×，边关联节点放大 1.5×，文本仅放大节点可见

### 交互体验

17. **禁用文本选中**：SVG 容器设 `user-select: none`
18. **随机游走**：每帧注入微小随机速度（`RW ≈ 0.04`），配合弹簧产生"呼吸"感
19. **侧边栏异步更新**：设 `panelDirty` 标志，由 rAF 异步更新，不阻塞渲染帧

### 视觉增强

20. **分类包络**：同分类节点周围绘制半透明虚线圆（质心为圆心，maxDist+32px 为半径），圆心标注分类名，字号随半径缩放（r/5，clamp 11-26px）
21. **边简化**：边无文字标签，描边 0.8px + 透明度 0.35，箭头按比例缩小。高亮边仅加粗（1.6px）和提升透明度（0.6）
22. **初始布局**：按主分类（第一个 category）分扇区初始放置，同分类节点在相邻角度

## 工作流

### 构建新图

1. 准备数据（nodes + edges 数组，nodes 含 `categories` 数组）
2. `layout()`：按主分类分扇区初始分布 + 力导向迭代（含分类引力/斥力）
3. `renderGraph()`：首帧创建 SVG 元素并缓存（`svgCache`，含 `nodeCircles` 引用）
4. `physicsTick()`：固定时间步长 + 随机游走 + Euler 位移 + 碰撞 + 边弹簧 + 同分类引力 + 异分类斥力
5. `drawEnvelopes()`：每帧按 category 分组计算圆形包络并绘制
6. 拖拽：`pointerdown` 选中 → `pointermove` 更新 + `resolveDragCollisions` → `pointerup` 释放 + 速度注入

### 优化已有图

1. 掉帧 → 先查是否每帧重建 DOM（改为增量更新）
2. 抖动 → 检查是否固定时间步长
3. 能量爆炸 → 检查是否半隐式 Euler + 摩擦 < 1
4. 拖拽卡顿 → 检查事件是否直接调渲染（改为 rAF 驱动）
5. 分类不聚拢 → 增大同分类引力系数或减小 IDEAL 边距

## 反模式

- **每帧清空重建 SVG**：DOM GC 是最大性能杀手
- **在 pointermove 中渲染**：与 rAF 竞争，帧率不稳
- **先推完碰撞再施弹簧**：弹簧无法即时抵消过推
- **弹簧只拉伸不压缩**：加了 `if (d > IDEAL)` 守卫
- **碰撞只处理被拖 vs 其他**：被推节点之间也会重叠
- **拖拽时弹簧仍作用于被拖节点**：节点被拉离鼠标
- **硬夹紧边界**：`pos = clamp(pos)` — 回弹更自然
- **事件处理器中同步调 `render()`**：阻塞当前帧
- **分类力强于边弹簧**：边弹簧系数不能高于同分类引力系数，否则聚类被拓扑牵散
- **在 convex hull 上直接绘图**：包络用正圆而非多边形，既平滑又计算极简
- **边带文字标签**：小节点下边标签会严重干扰视觉，应去掉
- **所有节点等大**：默认极小 + 选中放大可同时展示宏观结构和局部细节

## 故障排查

| 症状 | 可能原因 | 修复 |
|---|---|---|
| 掉帧 | 每帧重建 SVG DOM | 增量更新：缓存元素，只 setAttribute |
| 物理加速/爆炸 | Euler 积分顺序错误 | 先摩擦再位移 |
| 拖拽时节点被拉走 | 弹簧作用于被拖节点 | 拖拽时跳过被拖节点的弹簧端点 |
| 静止时 CPU 高 | 每帧跑完整物理 | 静止降频：少迭代 + 隔帧渲染 |
| 分类不聚拢 | 分类引力系数太小 | 增大 `CAT_ATTRACT`（`d² * k` 中的 k） |
| 分类间分不开 | 异分类斥力不够 | 增大 `CROSS_REPULSE`（`C / d²` 中的 C） |
| SVG 箭头不显示 | 箭头落在圆圈内 | 边端点到圆周：`x2 = cx - (dx/dist) * r` |
| 包络圆覆盖节点 | padding 太小 | 增大包络半径 padding（当前 32px） |

## 输出期望

1. 完整的单文件 HTML（内联 CSS + JS）图可视化
2. 或针对现有代码的优化方案（指明具体行号和改动）
3. 关键参数表：摩擦、弹簧系数、理想边长、碰撞距离、游走强度
