---
name: skill-creator
description: 创建、改进、测试和从经验中蒸馏技能。支持三种模式——distill（从笔记/调试记录/项目经验提炼 SKILL.md）、create（从零创建并迭代测试）、improve（优化现有技能的触发率和表现）。触发场景：用户说"创建skill""把这个变成skill""从经验提炼skill""改进skill""测试skill""优化触发率"。
---

# 技能创建器

创建新技能并迭代改进。核心流程：确定功能 → 写草稿 → 用测试 prompt 验证 → 评估结果 → 改进 → 重复。你的任务是判断用户在哪个阶段，帮助推进。

## 模式选择

根据用户输入判断使用哪种模式：

| 用户输入特征 | 模式 |
|------------|------|
| "把这个变成 skill""从这次经验提炼"、提供调试记录/项目笔记/失败案例 | **distill** — 从原始经验蒸馏 |
| "创建一个 skill 用于 X"、明确知道要什么 | **create** — 从零创建 + 迭代测试 |
| "改进 skill X""优化触发" | **improve** — 修改现有 skill |

---

## Distill 模式：从经验蒸馏技能

适用场景：用户提供杂乱的笔记、调试记录、项目总结、失败的实现尝试、或说"把这个变成 skill"。

### 判断：该不该变成 skill

满足以下至少两项才值得创建：

- 这个工作流会被重复执行
- 任务有非显而易见的约束
- 已知失败模式
- 需要行为一致性
- 经验包含可复用的判断
- 忘记这条教训的代价很高

不满足则建议放入 `CLAUDE.md` 或项目文档。

### 蒸馏流程

1. 识别可复用的任务类型
2. 提取硬约束（不能做什么）、首选模式（应该怎么做）、反模式（常见错误）
3. 提取验证检查点、定义输出期望
4. 选定技能名（小写、连字符、任务导向）

### 保留 vs 丢弃

**保留**：技术约束、环境约束、版本特定行为、安全默认值、设计模式、调试启发法、边界情况、已知 bug、失败症状、根因、修复模式、验证检查、输出格式、决策规则、安全边界。

**丢弃**：时间叙事、个人评论、冗余背景、一次性实现细节、长日志、完整对话记录、项目名（除非必需）。

### 泛化规则

```
BAD: "在 modulation_ui.m 里窗口一直往上移动。"
GOOD: "不要在 SizeChangedFcn 里给 fig.Position 赋值，会造成 resize 反馈循环。"

BAD: "我改了这一行就修好了。"
GOOD: "这类 bug 首先检查回调是否修改了会重新触发回调的状态。"
```

### 技能命名 / 质量检查 / 输出格式

同 distiller 规范。定稿前检查：目的狭窄清晰、包含规则/反模式/工作流/验证/输出期望、无不安全权限。

---

## 与用户沟通

根据对方的专业程度调整措辞。不确定时简短解释术语。

---

## Create 模式：从零创建 + 迭代测试

### 1. 捕捉意图

从对话中提取：工具、步骤顺序、用户修正、输入/输出格式。回答：技能做什么、何时触发、输出格式、是否需要测试。

### 2. 访谈

主动询问边界情况、输入/输出格式、示例文件、依赖项。利用已有 MCP 并行搜索。

### 3. 写 SKILL.md

- **name**：标识符
- **description**：何时触发。要具体、略主动（Claude 倾向触发不足）
- 正文：适用/不适用场景、核心规则、工作流、输出期望

### 4. 技能结构

```
skill-name/
├── SKILL.md (必需)
└── 可选: scripts/ references/ assets/
```

三级加载：元数据常驻 → SKILL.md 触发时加载 → 可选资源按需。SKILL.md 控制在 500 行内。

### 5. 测试用例

写 2-3 个真实 prompt，存 `<skill>/evals/evals.json`：

```json
{
  "skill_name": "example-skill",
  "evals": [
    {"id": 1, "prompt": "用户任务", "expected_output": "期望结果", "files": []}
  ]
}
```

---

## 运行与评估测试

测试结果放在 `<skill-name>-workspace/`，按 `iteration-N/eval-N/` 组织。

### 执行流程

1. **并行启动**：同时 spawn 带技能和不带技能（baseline）的 subagent
2. **起草断言**：运行期间起草可客观验证的定量断言
3. **捕获耗时**：完成时保存 `timing.json`（`total_tokens`、`duration_ms`）
4. **评分聚合**：grader subagent 评估 → `scripts/aggregate_benchmark` → `benchmark.json`
5. **启动查看器**：`python eval-viewer/generate_review.py <workspace>/iteration-N --skill-name "name" --benchmark <path>/benchmark.json`。无浏览器环境用 `--static`
6. **读取反馈**：用户在查看器中"Submit All Reviews"→ `feedback.json`

### 查看器

- Outputs 标签：prompt、输出、上次输出（迭代 2+）、评分、反馈框
- Benchmark 标签：通过率、耗时、token 统计
- 箭头键翻页，完成后提交评审

---

## 改进技能

原则：
1. **泛化反馈**：不让技能只适用测试用例，找到可复用的规律
2. **保持精简**：去掉无效指令，读 transcript 而非只看输出
3. **解释为什么**：避免 MUST 式指令，解释每个要求的原因
4. **看重复工作**：多测试共用辅助脚本 → 写进 `scripts/`

迭代：修改 → 重跑全部测试 → 查看器（含 `--previous-workspace`）→ 等反馈 → 再改。

---

## 高级：盲测对比

两个技能版本严格对比时，用独立 agent 在不告知来源的情况下判断质量。详见 `agents/comparator.md`。可选，大多数用户不需要。

---

## 描述优化

`description` 是决定触发的主要机制。

1. 生成 20 个触发 eval query（10 应触发 + 10 不应触发，近失配要刁钻）
2. 用 `assets/eval_review.html` 模板让用户审核
3. 运行：`python -m scripts.run_loop --eval-set <path> --skill-path <path> --model <id> --max-iterations 5`
4. 选 `best_description` 更新 SKILL.md

---

## 打包

```bash
python -m scripts.package_skill <path/to/skill-folder>
```

## Claude.ai 专用

无 subagent → 串行执行、跳过基线、跳过定量 benchmark、跳过触发优化。聚焦定性反馈。

## Cowork 专用

有 subagent 但无浏览器 → `--static` 写静态 HTML，反馈通过 `feedback.json` 下载。

## 参考文件

- `agents/grader.md` — 断言评估
- `agents/comparator.md` — 盲测对比
- `agents/analyzer.md` — 胜负分析
- `references/schemas.md` — JSON 结构定义
