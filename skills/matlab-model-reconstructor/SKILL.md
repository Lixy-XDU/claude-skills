---
name: matlab-model-reconstructor
description: reconstruct original mathematical models and derivations from matlab code for signal processing and optimization workflows. use when asked to analyze .m files, pasted matlab snippets, project folders, or runnable matlab/octave code to recover variables, equations, objectives, constraints, algorithms, assumptions, and full derivation steps; especially for dsp pipelines, filters, fft/spectral analysis, estimation, least squares, convex/nonlinear optimization, and code-to-formula documentation.
---

# MATLAB Model Reconstructor

## Purpose

Use this skill to analyze MATLAB code and reconstruct the underlying mathematical model, derivation chain, and final formulas. Prefer Chinese output unless the user asks otherwise. The default report structure is:

`代码逻辑 → 数学模型 → 变量定义 → 推导过程 → 最终公式`

The skill is optimized for signal processing and optimization code. It supports static analysis plus optional MATLAB/Octave execution when available.

## Core Workflow

1. **Identify the input form automatically**
   - Pasted MATLAB code: save to a temporary `.m` file for analysis when helpful.
   - Single `.m` file: inspect the full file and related local functions.
   - Project folder/repository: enumerate `.m`, `.mlx`, `.mat`, `.slx`, `.mdl`, and test files; identify likely entry points.
   - Multiple scripts/functions: build a call/variable map before deriving formulas.
   - Simulink artifacts: if MATLAB is available, use MATLAB metadata commands only; otherwise report limited static findings.

2. **Build an evidence map before deriving**
   - Run `scripts/matlab_inventory.py <path>` when a file or folder is available.
   - Inspect entry-point scripts manually after the scan.
   - Track each major formula back to code evidence: file, function, assignment, loop, solver call, or MATLAB built-in.
   - Separate **directly supported conclusions** from **reasonable inferred modeling assumptions**.

3. **Use execution when available**
   - If MATLAB is installed, prefer `matlab -batch` for non-destructive probes.
   - If MATLAB is unavailable but Octave is installed, use `octave --eval` for compatible scripts.
   - Never overwrite source files. Create temporary drivers under a scratch directory.
   - Use small synthetic inputs to validate dimensionality, matrix shapes, function outputs, and equivalence between reconstructed formulas and code.
   - If code has side effects, file writes, external devices, network calls, or long-running loops, do not execute it until it is isolated or stubbed.

4. **Reconstruct the model**
   - Convert scalar loops into vector/matrix notation when possible.
   - Convert iterative updates into recurrence relations or optimization algorithms.
   - Recover objective functions, constraints, regularizers, penalties, stopping criteria, and solver settings.
   - For signal processing, recover discrete-time signals, sampling assumptions, transforms, windows, filters, spectra, convolution/correlation operations, and frequency-domain interpretations.
   - For optimization, recover decision variables, objective, equality/inequality constraints, bounds, gradients/KKT conditions when derivable, and numerical solver mapping.

5. **Complete the derivation**
   - Start from the raw equations implied by the code.
   - State assumptions explicitly: real/complex domain, sampling interval, stationarity, convexity, noise model, boundary conditions, normalization, dimensions.
   - Derive intermediate equations step by step, not only the final result.
   - When derivation requires an assumption not present in code, label it as an assumption and explain why it is plausible.
   - When code implements an algorithm rather than a closed-form model, present both: the optimization/model problem and the algorithmic update equations.

6. **Validate and report uncertainty**
   - Check reconstructed formulas against code behavior using dimensions, synthetic numerical examples, or symbolic simplification when possible.
   - Report unresolved ambiguities instead of inventing hidden model intent.
   - Highlight places where variable names are misleading or where implementation differs from the canonical formula.

## Required Output Structure

Use this structure by default. Adapt section titles only when needed.

```markdown
# MATLAB 代码数学模型重构报告

## 1. 输入与分析范围
- 输入形式：文件/文件夹/粘贴代码/项目
- 入口点：...
- 是否执行 MATLAB/Octave：是/否，原因：...
- 关键文件与函数：...

## 2. 代码逻辑
按执行顺序说明主要模块：数据读入、预处理、核心计算、求解器、后处理、输出。

## 3. 变量定义
| 代码变量 | 数学符号 | 维度/类型 | 物理或算法含义 | 证据位置 |
|---|---:|---|---|---|

## 4. 原始数学模型
给出从代码直接还原的方程、目标函数、约束、滤波器、变换或递推关系。

## 5. 推导过程
从原始模型逐步推导到代码中的实现形式或最终公式。每一步说明依据和假设。

## 6. 最终公式
汇总最终模型、闭式解/更新式/频域表达/优化问题。

## 7. 代码与公式对应表
| 代码片段/函数 | 数学表达 | 说明 |
|---|---|---|

## 8. 验证结果
说明维度检查、数值一致性检查、MATLAB/Octave 运行结果或未执行原因。

## 9. 不确定性与待确认事项
列出无法从代码确定的假设、参数含义、边界条件、单位或数据来源。
```

## Signal Processing Reconstruction Rules

Use `references/signal-processing-patterns.md` for detailed mapping. Key rules:

- Treat vectors as discrete-time signals by default: `x[n]`, `n = 0,...,N-1`, unless code uses one-based indexing explicitly in formulas.
- Infer sampling frequency from variables such as `fs`, `Fs`, `Ts`, `dt`, `t`, `f`, `freq`, and `omega`.
- For `fft(x,N)`, state MATLAB's unnormalized DFT convention and check whether code divides by `N`, doubles one-sided spectra, or uses `fftshift`.
- For `filter(b,a,x)`, reconstruct the difference equation and transfer function.
- For convolution/correlation, distinguish linear convolution, circular convolution, matched filtering, and autocorrelation based on function calls and padding.
- For windows/spectral estimates, include normalization and leakage assumptions if the code applies window scaling.

## Optimization Reconstruction Rules

Use `references/optimization-patterns.md` for detailed mapping. Key rules:

- Identify decision variables from solver calls, anonymous functions, initial guesses, bounds, and reshaping operations.
- Map `fmincon`, `quadprog`, `lsqnonlin`, `lsqcurvefit`, `linprog`, custom gradient descent, ADMM, or alternating minimization into canonical optimization notation.
- Reconstruct constraints from `A,b,Aeq,beq,lb,ub,nonlcon`, penalty terms, projection steps, clipping, or manually coded feasibility checks.
- If least squares is detected, derive normal equations when valid and state rank/conditioning assumptions.
- If convexity is not guaranteed by code evidence, do not claim global optimality.
- If code uses numerical solvers, distinguish mathematical problem, solver algorithm, and implementation details.

## Using the Inventory Script

Run the script for file/folder inputs:

```bash
python scripts/matlab_inventory.py /path/to/matlab/project --output inventory.json
```

Use the JSON only as a starting map. Always inspect important source files directly before finalizing equations.

## Quality Bar

A good reconstruction must include:

- A clear variable-to-symbol table.
- At least one code-to-equation mapping table.
- Full derivation steps, not just final formulas.
- Explicit assumptions and unresolved ambiguities.
- Evidence-based language: “the code implements…”, “this implies…”, “assuming…, the model becomes…”.
- Validation details when MATLAB/Octave execution is possible.
