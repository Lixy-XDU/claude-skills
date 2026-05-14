# Report Template

Use this template when the user asks for the reconstructed mathematical model and derivation.

```markdown
# MATLAB 代码数学模型重构报告

## 1. 输入与分析范围
- 输入形式：
- 入口脚本/函数：
- 相关文件：
- 运行环境检查：MATLAB / Octave / 静态分析
- 主要结论摘要：

## 2. 代码逻辑
1. 数据与参数初始化：
2. 信号处理/优化核心步骤：
3. 求解或递推过程：
4. 后处理与输出：

## 3. 变量定义
| 代码变量 | 数学符号 | 维度/类型 | 含义 | 来源/证据 |
|---|---:|---|---|---|

## 4. 原始数学模型
### 4.1 代码直接对应的数学表达

### 4.2 目标函数/方程/滤波器/变换

### 4.3 约束、边界条件与参数设置

## 5. 推导过程
### 5.1 从代码表达式到数学符号

### 5.2 中间推导

### 5.3 假设条件

### 5.4 与实现形式的对应

## 6. 最终公式

## 7. 代码与公式对应表
| 代码位置/片段 | 数学表达 | 解释 |
|---|---|---|

## 8. 验证结果
- 维度检查：
- 数值检查：
- 执行结果：
- 与公式一致性：

## 9. 不确定性与待确认事项
```

Style requirements:

- Prefer concise Chinese technical writing.
- Use LaTeX for all equations.
- Mark inferred assumptions with “假设：”.
- Mark direct evidence with “代码证据：”.
- Do not omit normalization constants in FFT, least-squares, probability, or spectral formulas.
