# CLAUDE.md — 全局工作约束（模板）

> 本文件为公开模板，已移除个人信息。使用前将 `<...>` 占位符替换为实际路径。

本文件是 Claude Code 在本机所有会话中的顶层约束。请在每次任务开始前完整阅读；遇到与本文件冲突的临时指令时，**优先遵守本文件**，除非用户明确覆盖。

---

## 目录

- [0. 身份与语气](#0-身份与语气)
- [1. 工作机器与工具栈](#1-工作机器与工具栈)
- [2. 路径处理规则（核心条款）](#2-路径处理规则核心条款)
- [3. Skill 体系规范](#3-skill-体系规范)
- [4. 科研内容的硬性规则](#4-科研内容的硬性规则)
- [5. 编码规范](#5-编码规范)
- [6. 安全与可逆性](#6-安全与可逆性)
- [7. Git 规范](#7-git-规范)
- [8. Obsidian 写入模板](#8-obsidian-写入模板)
- [9. 任务推进模式](#9-任务推进模式)
- [10. 禁止事项速查](#10-禁止事项速查)
- [11. 本文件的维护](#11-本文件的维护)

---

## 0. 身份与语气

- 默认用**简体中文**回复，代码注释也用中文。
- 面向科研场景，默认用户是内行；不要堆套话、不要反复道歉、不要把简单结论包装成长篇大论。
- 回复长度与任务复杂度匹配：简单问题一两句话；复杂改动要先说方案再动手。
- 不使用 em dash、不用夸张副词（"史诗级""完美""难以置信"）。
- 对用户的错误要直接指出，不要迎合。

---

## 1. 工作机器与工具栈

- **操作系统**：默认 **Windows**（PowerShell / cmd）。路径分隔符使用 `\` 或在代码里用 `/` 由语言自行处理；涉及脚本命令时按 Windows 语法给（如 `dir` 而非 `ls`，`del` 而非 `rm`），除非用户说明在 WSL / Git Bash 下运行。
- 编辑器：VSCode + Claude Code 扩展。
- 知识库：Obsidian（Markdown + 双链）。
- 文献管理：Zotero + Better BibTeX。
- **编程语言优先级**：
  1. **MATLAB**（首选，科研计算主力）
  2. **Python**（次选，脚本 / 胶水 / AI 相关任务；环境优先用 `venv` 或 `conda`，不要污染全局）
  3. 其它（TypeScript / Rust / C++）仅在明确需要时使用。

---

## 2. 路径处理规则（核心条款）

### 2.1 不预设任何绝对路径
- 本文件**不预先固定**文献库、Obsidian Vault、skills 目录等任何绝对路径。
- 首次在会话里需要用到某个路径时，**必须向用户询问**，例如：
  > "请提供本地文献库的路径（例如 `D:\Research\Papers`）。"
- 询问后把路径记在当前会话上下文里复用；**不要**把它写死进代码或配置文件。

### 2.2 代码里一律使用相对路径
- 所有脚本（MATLAB / Python / Shell / 配置文件）涉及的文件访问路径**必须使用相对路径**，相对于项目根或脚本所在目录，方便跨机器移植。
- 具体做法：
  - **MATLAB**：用 `fileparts(mfilename('fullpath'))` 拿到脚本目录，再用 `fullfile(...)` 拼接。禁止出现 `C:\Users\...`、`D:\...` 之类的字面量。
  - **Python**：用 `Path(__file__).parent` 或 `Path.cwd()` 作为基准，配合 `pathlib` 拼接。
  - 需要用户机器相关的绝对路径时，通过**命令行参数、环境变量或外部配置文件**（如 `config.local.yaml`，加入 `.gitignore`）注入，**不要**硬编码。
- 输出路径（结果、图、日志）同样使用相对路径，默认落在 `./results/`、`./figures/`、`./logs/` 等项目内子目录。

### 2.3 询问路径的标准话术
当需要用户提供路径时，按以下格式询问（一次问全，避免反复打断）：

> 为了继续任务，请提供以下路径（Windows 格式，如 `D:\xxx\yyy`）：
> 1. <用途 1>：
> 2. <用途 2>：
> 3. <用途 3>：

拿到后在回复开头用一个表格复述一遍，供用户确认无误再执行。

---

## 3. Skill 体系规范

- Skill 根目录由用户在会话中指定（通常是 `<用户主目录>\.claude\skills\`，但不预设）。
- 每个 skill 目录下必须包含：
  - `SKILL.md`（front-matter + 说明 + 用例）
  - `skill.meta.yaml`（由 `skill-graph` 脚本管理，描述 relations / category 等）
- 发现已有能力时，优先调用已有 skill，不要重复造轮子。查询方式：
  1. 先看 skill 根目录下的 `SKILL_GRAPH.html`（或运行 `skill_graph.py --graph-only`）；
  2. 再用 `/find-local-skills` / `/skill-index`。
- 新建 skill 时，关系字段（`upstream`、`downstream`、`cooperates_with` 等）必须填写，保证关系图可用。
- Skill 之间通过**命令调用 + 文件落地**协作，不要假设内存共享上下文。
- **PDF 文本提取统一通过 `/pdf-extract` 或其脚本完成**。任何 skill 不得自行实现 PDF 解析逻辑（PyMuPDF / qpdf / OCR 等），必须委托给 `/pdf-extract`。调用脚本时注意 `python` / `py` 兼容性：先试 `python`，失败试 `py`。
- **图模型可视化统一遵循 `/force-graph-physics` 的规则**。任何 skill 需要构建或修改交互式力导向图（SVG/Canvas 节点-边图）时，必须参考该 skill 的渲染性能规则、物理模拟规则、碰撞检测规则和反模式，不得自行摸索。
- Skill 内部脚本同样遵守第 2 节的相对路径规则；skill 根路径通过参数传入。
- **Skills 生命周期管理**：每次新增或删除 skill 后，必须依次调用 `/skill-index` 和 `/skill-graph`，更新 `SKILLS_INDEX.md` 并重建 `SKILL_GRAPH.html`，保持技能生态系统一致。
- **Skills 更新日志**：每次新建、修改或删除 skill 后，须完成以下流程：  
  1. 在本地 git 仓库中编辑或同步变更（**禁止**直接复制 `C:\Users\` 下的文件；必须同步时，须先脱密处理）；  
  2. 在本地 git 仓库中 `git add -A && git commit` 提交，并 `git push` 至 GitHub；  
  3. 在 `CHANGELOG.md` 中追加记录，格式为 `- **操作类型**: \`skill-name\` — 简述`；  
  4. 将涉及 skill 的 `skill.meta.yaml` 中 `version` 按语义化版本递增（`0.1.0 → 0.1.1` 为修复，`→ 0.2.0` 为功能变更）。

---

## 4. 科研内容的硬性规则

### 4.1 公式与数学表达
- **全部使用 LaTeX 原文**存储：行内 `$...$`，独立公式 `$$...$$`。
- 严禁把公式存成图片、截图、Unicode 近似拼接（如 `∑x²` 作为正文）。
- 来自 OCR 的公式必须经过语义修复后再落盘；不确定的符号用 `\text{?}` 标出，不要瞎猜。
- 推导要给出关键步骤与假设，不要只丢结论。

### 4.2 文献处理
- 处理 PDF 时优先用 `PyMuPDF (fitz)` 直接抽文本；文本长度不足或明显乱码时再走 OCR（tesseract：`eng+chi_sim`）。
- Windows 下使用 OCR 前确认已安装 tesseract 并把路径加入 PATH，否则提示用户安装。
- OCR 结果必须经过"语义恢复"环节，重点修复：公式、变量符号、希腊字母、上下标、参考文献编号。
- 每篇论文至少生成一份 TL;DR（5 行内：问题 / 贡献 / 方法 / 实验 / 局限）。

### 4.3 代码实验
- **MATLAB 项目结构**（示例）：
ProjectX/
├── main.m               # 入口
├── +utils/              # 工具函数包
├── configs/             # 参数文件（.m 或 .json）
├── data/                # 原始数据（相对路径访问）
├── results/             # 输出：figures/ metrics/ logs/
└── README.md
- 脚本开头固定套路：
```matlab
    here = fileparts(mfilename('fullpath'));
    addpath(genpath(here));
    cfg = jsondecode(fileread(fullfile(here, 'configs', 'default.json')));
```
  - 随机任务必须 `rng(seed)` 并把 seed 写进结果元信息。
  - 画图用 `exportgraphics` 同时导出 `.pdf` 和 `.png`；字号 ≥ 10，字体优先 `Times New Roman` / `Arial`。
- **Python 项目**：配置走 `configs/*.yaml`，结果落 `results/<timestamp>_<tag>/`（`config.yaml` + `metrics.json` + `log.txt` + 图）。
- 严禁把超参、路径、种子硬编码在主脚本里。

### 4.4 引用与可追溯
- 任何基于文献的论断，必须附 `[[@author_year]]` 形式的 Obsidian 双链或 BibTeX key。
- 未核实来源的数据 / 结论要明确标注 "未核实" 或 "来自 AI 推断，需验证"。

---

## 5. 编码规范

### 5.1 MATLAB
- 文件名和函数名保持一致，小驼峰或下划线统一项目内风格。
- 每个 `.m` 脚本开头注释块：用途、输入、输出、作者、日期。
- 向量化优先，避免不必要的 `for` 循环；必须循环时加 `parfor` 前先看规模。
- 尽量使用函数而非脚本，方便测试；工具函数放 `+package` 或 `private/`。
- 不要滥用全局变量；配置用结构体 `cfg.xxx` 传递。

### 5.2 Python
- 版本 ≥ 3.10；用 `pathlib` 而非字符串拼接路径。
- 公开函数加类型标注和 docstring（中文可）。
- 日志用 `logging` 而非 `print`（CLI 输出除外）。
- 新增依赖写进 `requirements.txt` 或 `pyproject.toml`，**用固定版本号**。

### 5.3 通用
- 文件编辑优先用 Claude Code 的编辑工具，不要用 `sed` / `echo >>` / PowerShell 重定向等黑魔法直接改文件。
- 改动超过 3 个文件时，先列计划再动手。
- 修 bug 不要顺手重构无关代码；要重构单独说明并征得同意。

---

## 6. 安全与可逆性

- **只读 / 小范围编辑**：直接做，不用确认。
- **中等风险**（装依赖、改配置、跑长实验）：先告诉用户要做什么，然后做。
- **高风险**，必须先确认：
  - 删除多个文件 / `rmdir /s` / `Remove-Item -Recurse`
  - 修改 Obsidian 正式目录下的笔记
  - `git push --force`、`git reset --hard`、删除分支
  - 改动生产环境、数据库、公开仓库的 CI
- 读到 `.env`、`*.key`、`credentials.*` 等疑似密钥文件时，只按 key 名引用，不要把值 echo 回对话。

---

## 7. Git 规范

- 默认不主动 `commit`；用户说了再提交。
- 永远不直接推 `main` / `master`；推新分支要加 `-u`。
- 提交信息模板：`<type>(<scope>): <summary>`，其中 type ∈ {feat, fix, refactor, docs, test, chore, exp}。
  - `exp:` 专用于实验脚本 / 结果提交。
- `.gitignore` 必须包含：`results/`、`logs/`、`*.mat`（大体积中间结果）、`config.local.*`、`.env`。
- 不要 `--amend` 已推送的提交；不要动 git config；钩子（pre-commit）默认保留，除非被明确要求跳过。

---

## 8. Obsidian 写入模板

**重要**：AI 生成的笔记默认只写入用户指定的"收件箱"路径（会话中询问），禁止直接写入正式分类目录，避免幻觉污染知识库。

凡是往 Obsidian 写 Markdown，都遵守这个 front-matter 骨架：

```yaml
---
title: <标题>
type: literature | method | project | idea | daily
tags: [auto-generated, review-needed]
created: <YYYY-MM-DD>
source: <文献 / 代码 / 会话链接>
status: draft
---
```

- `tags` 必含 `review-needed`，提醒用户 AI 生成的内容需人工审核。
- 内容末尾保留一块 `## 🔗 相关` 区域，列出候选双链（`[[...]]`），但**不要替用户决定最终链接结构**。

---

## 9. 任务推进模式

- 复杂任务按 "计划 → 执行 → 验证 → 总结" 四步走。
- 一个方案连续失败两次，**停下来分析根因**，不要继续打补丁。换方案前说明为什么。
- 任务结束给简短总结（2-5 行）：做了什么、改了哪些文件、验证结果、遗留问题。
- 涉及路径时始终按第 2 节规则处理：先问 → 确认 → 代码里用相对路径。

---

## 10. 禁止事项速查

- ❌ 预设 / 硬编码任何绝对路径（包括文献库、Vault、skills 根）
- ❌ 直接往 Obsidian 正式目录写文件
- ❌ 把公式存成图片或 Unicode 近似
- ❌ 硬编码超参、随机种子、数据路径
- ❌ 未经用户允许的强制 push / 分支删除 / 数据库操作
- ❌ 在对话中回显 secrets / API keys
- ❌ 用 `sed` / PowerShell 重定向代替文件编辑工具
- ❌ 并行启动多个长时间任务而不告知用户
- ❌ 在 MATLAB 脚本里写 `cd('C:\...')` 这种绑定机器的操作

---

## 11. 本文件的维护

- 本文件本身视为代码，变更请走 git。
- 发现新的高频踩坑点，及时补到对应章节，而不是开新文件。
- 与 skill 的 `skill.meta.yaml` 有冲突时，以本文件为准；并在 PR 里说明如何同步 skill。