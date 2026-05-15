---
name: matlab-research-coder
description: use this skill when claude code needs to convert local markdown method notes or literature notes into a matlab development environment. trigger for matlab implementations from mathematical derivations, algorithms, numerical methods, research notes, or paper reproduction requests. use for planning project scaffolds, mapping equations to code, creating matlab modules, experiments, tests, examples, and traceability documents from local .md notes.
---

# MATLAB Research Coder

Use this skill to turn local markdown research notes into a MATLAB code development environment. The notes usually come from two user-managed directories:

- `方法库`: reusable mathematical methods, derivations, algorithms, numerical principles, engineering calculations, and implementation notes.
- `文献笔记`: paper-reading notes, literature summaries, reproduction plans, experiment notes, and paper-specific derivations.

Do not assume which directory to use before determining the user's intent. Do not write permanent directory paths into generated code unless the user explicitly provides them for the current task.

## Workflow Overview

0. **确认路径**：开工前向用户确认输入源（`方法库` 或 `文献笔记` 的具体路径）和输出目标（`code-workspace/` 下的项目目录名）。路径未确认之前不得开始搜索笔记或生成代码。
1. Determine whether the task is a general method implementation or a paper/literature reproduction.
2. Select the correct note source.
3. Search and read the relevant `.md` notes.
4. Extract mathematical, algorithmic, and experimental requirements.
5. Build a MATLAB implementation or reproduction plan.
6. Create the MATLAB project scaffold.
7. Implement code, examples, tests, documentation, and traceability files.
8. Report assumptions, unresolved gaps, entry points, and test instructions.

## 1. Determine User Intent

Classify each request into one of two workflows.

### Workflow A: Method Library Implementation

Use `方法库` when the user asks to implement, code, simulate, verify, or build a MATLAB environment for:

- a mathematical method
- a derivation
- an algorithm
- a formula
- a numerical method
- a model principle
- an engineering computation
- a reusable technical method

Example requests:

- “根据我的方法库实现这个控制算法”
- “把这个数学推导写成 MATLAB 代码”
- “为某个数值方法搭建 MATLAB 开发环境”
- “根据方法库里的推导生成函数、测试和示例”

### Workflow B: Paper or Literature Reproduction

If the user mentions any of these concepts, do not immediately access `文献笔记`:

- 论文
- 文献
- 复现
- paper
- literature
- reproduce
- reproduction
- replication
- benchmark
- experiment
- baseline
- ablation

First ask:

```text
你是要复现某一篇论文/文献吗？
如果是，我会从 `文献笔记` 目录读取对应的 `.md` 阅读笔记；如果不是，我会优先从 `方法库` 目录读取方法推导笔记。
```

Only use `文献笔记` after the user clearly confirms that they want to reproduce a paper or literature item.

If the user says no, or clarifies that they only want to implement a general method, use `方法库` instead.

## 2. Workflow A: Implement from `方法库`

Use this workflow when the task is based on reusable mathematical or algorithmic notes.

### Step A1: Locate Relevant Method Notes

Search `方法库` for `.md` files related to the user's requested method, model, equation, algorithm, or mathematical principle.

Search by:

- method name
- model name
- formula name
- algorithm keyword
- physical or engineering concept
- Chinese and English aliases if applicable

If the directory path is not available in the current Claude Code session, ask the user to provide or link the `方法库` directory. If multiple candidate notes are found, summarize the candidates and ask the user which one to use.

### Step A2: Extract Mathematical and Algorithmic Content

From the selected `.md` file or files, extract:

- problem objective
- mathematical assumptions
- variable definitions
- parameter definitions
- input and output definitions
- key equations
- derivation steps
- constraints
- boundary conditions
- initial conditions
- numerical method
- algorithm flow
- convergence or stability requirements
- validation criteria
- known limiting cases
- references to related methods

Do not silently invent missing mathematical details. Mark unclear items as `需要用户确认` or `方法库笔记中未明确`.

### Step A3: Build MATLAB Implementation Plan

Create a MATLAB development plan that maps the method note to code.

The plan should include:

- MATLAB project name
- major modules
- function list
- function inputs and outputs
- equation-to-code mapping
- test cases
- example scripts
- documentation files
- unresolved assumptions

Prefer separating:

- model definition
- numerical solver
- utility functions
- visualization
- validation
- examples

### Step A4: Create MATLAB Project Structure

Use this default structure unless the user requests otherwise:

```text
matlab-project/
├── src/
│   ├── models/
│   ├── solvers/
│   ├── utils/
│   └── visualization/
├── tests/
├── examples/
├── docs/
│   ├── derivation_traceability.md
│   └── assumptions.md
├── data/
├── results/
└── README.md
```

### Step A5: Implement MATLAB Code

When writing MATLAB code:

- use clear function names that reflect the mathematical meaning
- preserve important formulas in comments
- link code blocks to equations or derivation steps
- avoid hard-coding parameters unless the note explicitly defines them as constants
- separate reusable functions from example scripts
- use input validation for public functions
- prefer vectorized MATLAB where it improves clarity
- avoid over-optimizing before correctness is established

### Step A6: Add Verification

Add tests for:

- dimensional consistency
- known analytical cases
- boundary conditions
- invalid inputs
- numerical stability
- limiting cases
- expected outputs from the method note

Create or update `docs/derivation_traceability.md` to map:

- equations to MATLAB functions
- variables to code variables
- assumptions to implementation choices
- validation criteria to tests

## 3. Workflow B: Reproduce from `文献笔记`

Use this workflow only after the user confirms they want to reproduce a paper or literature item.

### Step B1: Locate Relevant Literature Notes

Search `文献笔记` for `.md` files related to the target paper or literature item.

Search by:

- paper title
- author name
- publication year
- method name
- model name
- dataset name
- experiment name
- benchmark name
- keywords provided by the user

If the directory path is not available in the current Claude Code session, ask the user to provide or link the `文献笔记` directory. If multiple candidate notes are found, summarize them and ask the user which paper or note to reproduce.

### Step B2: Extract Reproduction Information

From the selected literature note, extract:

- paper objective
- research problem
- core contribution
- mathematical formulation
- assumptions
- key equations
- algorithm steps
- model architecture
- datasets
- preprocessing steps
- experiment settings
- hyperparameters
- baselines
- evaluation metrics
- figures to reproduce
- tables to reproduce
- ablation studies
- expected numerical results
- implementation details
- missing or ambiguous details

Do not invent missing experimental settings. Mark them as `需要用户确认` or `文献笔记中未明确`.

### Step B3: Build Reproduction Plan

Create a reproduction plan before writing code.

The plan should include:

- target paper or literature note
- reproduction scope
- figures, tables, or experiments to reproduce
- required data
- required MATLAB modules
- algorithm implementation plan
- experiment scripts
- expected outputs
- validation method
- known gaps or assumptions

Create or update `docs/reproduction_plan.md`.

### Step B4: Create MATLAB Reproduction Project Structure

Use this default structure for paper reproduction:

```text
paper-reproduction-project/
├── src/
│   ├── models/
│   ├── solvers/
│   ├── utils/
│   └── visualization/
├── experiments/
│   ├── config/
│   ├── run_main_experiment.m
│   ├── run_ablation.m
│   └── run_benchmark.m
├── tests/
├── examples/
├── docs/
│   ├── reproduction_plan.md
│   ├── paper_traceability.md
│   └── assumptions.md
├── data/
│   └── README.md
├── results/
│   └── README.md
└── README.md
```

### Step B5: Implement Reproduction Code

When implementing reproduction code:

- separate algorithm code from experiment scripts
- keep experiment parameters in config files or config sections
- avoid hard-coding dataset paths
- preserve paper notation in comments where useful
- map equations, algorithms, figures, and tables to code files
- include runnable experiment entry points
- make results reproducible where possible
- document random seeds if stochastic methods are used
- keep visualization scripts separate from core algorithm logic

### Step B6: Add Paper Traceability

Create or update `docs/paper_traceability.md` to map:

- paper equations to MATLAB functions
- paper algorithms to code modules
- paper figures to plotting scripts
- paper tables to experiment scripts
- paper metrics to evaluation functions
- paper assumptions to implementation choices
- missing paper details to user-confirmed assumptions

### Step B7: Add Reproduction Validation

Add checks for:

- whether the main experiment runs end-to-end
- whether output dimensions match the paper
- whether metrics are computed correctly
- whether reproduced values are close to expected values when available
- whether figures or tables match the qualitative trend of the paper
- whether unresolved assumptions are documented

## 4. Shared MATLAB Coding Standards

Apply these standards to both workflows.

### Code Organization

Prefer small, composable MATLAB functions.

Separate:

- data loading
- preprocessing
- model construction
- solver logic
- metric calculation
- visualization
- experiment orchestration

### Naming

Use meaningful names based on mathematical or paper terminology. Avoid vague names such as `func1`, `temp`, `main2`, or `test_old`.

Prefer names such as:

```matlab
computeStateTransition.m
solveOptimizationProblem.m
evaluateReconstructionError.m
plotConvergenceCurve.m
```

### Comments

Use comments to explain mathematical intent, not obvious MATLAB syntax.

Good comment:

```matlab
% Implements Eq. (7): regularized objective with L2 penalty.
```

Bad comment:

```matlab
% Add x and y.
```

### Parameters

Keep parameters visible and easy to modify.

For reproduction tasks, prefer experiment config files or config sections. For reusable methods, prefer named parameter structs.

### Tests

Every generated project should include at least:

- one smoke test
- one dimensional consistency test
- one known-case or limiting-case test
- one example script that runs end-to-end

## 5. Clarification Rules

Ask follow-up questions only when the missing information blocks correct implementation.

Ask about:

- which method or paper to use, if ambiguous
- dataset location, if required
- target figure, table, or experiment, if reproducing a paper
- unclear parameters
- missing boundary conditions
- missing input/output definitions
- preferred MATLAB version or toolbox dependencies, if relevant

Do not ask unnecessary questions before doing useful work.

If information is missing but non-blocking, proceed with a documented assumption and record it in `docs/assumptions.md`.

## 6. Final Output Requirements

When completing a task with this skill, provide:

1. A concise summary of what was built.
2. The source notes used:
   - from `方法库` for method implementation, or
   - from `文献笔记` for paper reproduction.
3. The generated MATLAB project structure.
4. Key MATLAB entry points.
5. Any assumptions or unresolved issues.
6. How to run the main example or experiment.
7. How to run the tests.

For paper reproduction, also include:

- target paper or literature note
- reproduction scope
- reproduced figures, tables, or experiments
- gaps between the note and the implementation
