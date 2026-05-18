---
name: skill-lifecycle
description: 管理本地技能的生命周期——删除、禁用、启用、中文化。触发场景：用户说"删除skill""移除skill""卸载skill""禁用skill""停用技能""启用skill""重新打开skill""中文化""翻译成中文""汉化""skill是英文的"；或 /skill-index 审计建议删除/禁用某个技能。
argument-hint: "<rm|disable|enable|localize> <skill-name-or-pattern>"
disable-model-invocation: false
---

# 技能生命周期管理

统一管理本地技能的删除、禁用、启用和中文化。四个子命令共享定位→确认→执行→更新索引→重建图的流程。

## 子命令

| 命令 | 用途 | 示例 |
|------|------|------|
| `rm <name>` | 永久删除技能目录及所有文件 | `/skill-lifecycle rm ml-traditional-gui` |
| `disable <pattern>` | 临时禁用（重命名 SKILL.md） | `/skill-lifecycle disable nature-*` |
| `enable <pattern>` | 重新启用已禁用的技能 | `/skill-lifecycle enable nature-*` |
| `localize <pattern>` | 检测并中文化英文技能 | `/skill-lifecycle localize pptx-toolkit` |

## 通用规则

以下规则适用于全部子命令：

- **确认**：执行前必须向用户展示影响范围并获取确认
- **plugin 技能**：`matlab-core:*`、`toolkit:*` 等命名空间技能由插件系统管理，不得直接删除或禁用，须提示用户通过插件管理器操作
- **元技能保护**：禁用元技能（skill-index、skill-graph、skill-lifecycle、skill-creator、skill-updater）时警告用户可能导致技能管理功能异常
- **备份**：编辑 `SKILLS_INDEX.md` 前先复制为 `.bak`
- **同步**：修改后统一调 `/skill-graph` 重建 `SKILL_GRAPH.html`
- **git**：同步到 `D:\git仓库\claude-skills\` 后 `git commit`，推送须用户授权

---

## 一、删除（rm）

### 流程

1. **定位**：用户提供技能名。歧义时列出候选项
2. **交叉引用检查**：扫描其他技能的 `skill.meta.yaml`，找出将此技能列为 upstream/downstream/cooperates_with 的引用方，展示给用户
3. **确认**：展示将删除的目录及全部内容，提示不可逆
4. **执行**：`rm -rf ~/.claude/skills/<name>/`
5. **索引**：从 `SKILLS_INDEX.md` 移除该行；若为分类最后一项，删除空分类
6. **重建图**：`python ~/.claude/skills/skill-graph/scripts/generate_skill_graph_html.py --graph-only`
7. **git 同步**：若 `D:\git仓库\claude-skills\skills\<name>\` 存在，同步删除并 `git commit`
8. **CHANGELOG**：`- **remove**: \`skill-name\` — <简述原因>`
9. **报告**：汇总删除内容、索引变更、图重建、git 提交状态

### 边界情况

- 技能不存在 → `find ~/.claude/skills -maxdepth 1 -type d -name "*<query>*"` 列出候选项
- 匹配到多个 → 全部列出，让用户选择
- git 仓库不存在 → 跳过 git 步骤，记录警告

---

## 二、禁用（disable）

### 机制

将 `SKILL.md` 重命名为 `SKILL.md.disabled`，同时将 `skill.meta.yaml` 的 `status` 改为 `disabled`。Claude Code 只加载 `SKILL.md`，重命名后技能不可见。所有文件保留在磁盘上，可随时启用。

### 目标匹配

| 形式 | 示例 | 含义 |
|------|------|------|
| 精确名称 | `ml-traditional-gui` | 精确匹配该技能 |
| 前缀通配 | `matlab-*` | 目录名以 `matlab-` 开头的所有技能 |
| 前缀通配 | `nature-*` | 所有 `nature-` 前缀技能 |
| `--all` | `--all` | 全部本地技能（须双重确认） |

### 流程

1. **匹配**：按目标模式搜索 `~/.claude/skills/` 下匹配的目录
2. **展示**：列出将禁用的技能及当前状态（active/disabled）
3. **确认**：展示影响范围，获取确认。`--all` 须双重确认
4. **执行**：逐个 `mv SKILL.md SKILL.md.disabled`，更新 `skill.meta.yaml` 中 `status: disabled`
5. **索引**：在 `SKILLS_INDEX.md` 中对应行标注 `（已禁用）`
6. **重建图 + CHANGELOG**：同上

### 边界情况

- 技能已禁用 → 跳过并注明
- 无匹配技能 → 列出全部可用技能名，建议替代拼写
- 禁用元技能 → 警告可能影响技能管理功能

---

## 三、启用（enable）

### 机制

`SKILL.md.disabled` → `SKILL.md`，`status` 改回 `active`。

### 流程

1. **匹配**：搜索 `~/.claude/skills/*/SKILL.md.disabled`
2. **展示**：列出将被启用的技能
3. **确认**：获取确认
4. **执行**：`mv SKILL.md.disabled SKILL.md`，`status: active`
5. **索引**：移除 `（已禁用）` 标注
6. **重建图 + CHANGELOG**：同上

---

## 四、中文化（localize）

### 背景

CLAUDE.md 规定：所有加入本机技能生态的 skill，其 `SKILL.md` 正文（含标题、说明、工作流、示例）必须翻译为简体中文。外部引入的英文 skill 须在首次安装后完成中文化，后续迭代保持中文。`skill.meta.yaml` 的 `title` 和 `purpose` 字段同样使用中文。

### 机制

检测 SKILL.md 正文的中文覆盖率，对英文为主的技能调用 Claude Code 自身翻译能力完成中文化，同时保留代码、路径、技术术语不变。

### 目标匹配

| 形式 | 示例 | 含义 |
|------|------|------|
| 精确名称 | `pptx-toolkit` | 精确匹配该技能 |
| 前缀通配 | `matlab-*` | 目录名以 `matlab-` 开头的所有技能 |
| 前缀通配 | `nature-*` | 所有 `nature-` 前缀技能 |
| `--all` | `--all` | 全部本地技能（逐一检测） |
| `--check` | `--check` | 仅检测并报告，不执行翻译 |

### 流程

1. **匹配**：按目标模式搜索 `~/.claude/skills/` 下匹配的目录
2. **检测**：对每个匹配的技能，读取 `SKILL.md` 正文（排除 frontmatter、代码块、行内代码、URL、文件路径），统计中文字符占比
   - 中文占比 ≥ 60% → 已是中文，跳过
   - 中文占比 30-60% → 标记为"部分中文"，待确认
   - 中文占比 < 30% → 标记为"需中文化"
3. **展示**：列出每个技能的检测结果

   ```
   | 技能 | 中文占比 | 状态 |
   |------|---------|------|
   | pptx-toolkit | 5% | 需中文化 |
   | content-to-slides | 55% | 部分中文 |
   | nature-figure | 95% | 已是中文 |

4. **确认**：展示将中文化的技能清单，获取确认
5. **执行**：对每个待中文化的技能：

   a. **翻译 SKILL.md**：
      - 保留 frontmatter 结构（`name` 字段通常保留英文，`description` 翻译为中文）
      - 保留所有代码块内容（bash、python、javascript、json 等）完全不变
      - 保留行内代码 `` `like_this` `` 不变
      - 保留 URL、文件路径不变
      - 保留 YAML frontmatter 格式不变
      - 保留专有名词原文（pptxgenjs、python-pptx、Gemini、Claude Code 等）
      - 翻译正文段落、标题、表格文字、列表项为简体中文
      - 使用自然的中文技术写作风格（参考现有中文化 skill 的措辞习惯）

   b. **更新 skill.meta.yaml**：将 `title` 和 `purpose` 字段翻译为中文

   c. **更新 frontmatter description**：若 SKILL.md 的 `description` 为英文，翻译为中文触发描述

6. **索引**：在 `SKILLS_INDEX.md` 中更新对应条目的描述（如有变化）
7. **重建图 + CHANGELOG**：同上
8. **报告**：汇总每个技能的中文化结果

### 翻译质量规则

- **标题优先级**：先保证各级标题翻译准确，再处理正文段落
- **术语一致性**：同一英文术语在 skill 体系内保持统一中文译名（参考已中文化的 nature-* 系列措辞）
- **不翻译的内容**：
  - 代码块（\`\`\` 包围的内容）
  - 行内代码（\` 包围的内容）
  - URL 和文件路径
  - CLI 命令和参数
  - JavaScript/Python/Bash 等代码片段
  - YAML/JSON 配置示例
  - 品牌名、产品名、GitHub 仓库名
- **可翻译的内容**：
  - 段落文字、说明文字
  - 表格中的文字描述
  - 列表项、注释
  - 章节标题（## 之后的部分）
  - 设计哲学、风格描述等概念性内容
  - frontmatter 的 `description` 字段

### 边界情况

- 技能无 SKILL.md → 跳过并报告
- 技能已是中文 → 跳过并注明
- plugin 技能（`matlab-core:*` 等）→ 提示用户中文化可能被插件更新覆盖，仍可执行
- `--check` 模式 → 只检测和报告，不翻译
- 翻译后技能功能 → 仅改变文档语言，不影响 skill 执行逻辑

### 示例

```bash
# 检测全部技能的中文覆盖情况
/skill-lifecycle localize --check --all

# 中文化单个英文技能
/skill-lifecycle localize pptx-toolkit

# 中文化所有 nature- 前缀技能
/skill-lifecycle localize nature-*
```

- 删除前始终做交叉引用检查
- 禁用不删除任何文件，只做重命名
- 批量操作始终先展示清单再确认
- 不操作 `~/.claude/skills/` 以外的技能
- 编辑索引前备份
