---
name: skill-index
description: 协调、分类、路由、审计和维护本地 Claude Code 技能系统。触发场景：用户想决定用哪个技能、按功能组织技能、更新技能索引、协调多个技能、防止技能冗余；或新增/修改技能后需要更新索引和分类。
argument-hint: "[task-or-skill-topic]"
disable-model-invocation: false
---

# 技能索引

本地技能系统的协调层。不替代领域技能，而是路由任务到正确技能、维护分类、协调元技能、防止技能库混乱。

核心逻辑：

```text
任务 → 分类 → 最佳技能 → 行动 → 索引更新
```

## 适用场景

- 决定哪个技能处理某项任务
- 按功能组织技能
- 构建或更新技能索引
- 协调多个技能
- 分类新技能
- 判断技能应为个人级还是项目级
- 检测技能重叠
- 规划本地技能库结构
- 清理技能冗余
- 定义 `/find-local-skills`、`/find-skills`、`/skill-creator` 的协作方式
- 创建路由映射
- 生成或修订 `SKILLS_INDEX.md`

## 不适用场景

- 用户已明确知道该用哪个领域技能
- 只需执行具体的编码/调试/审查任务
- 任务明显属于某专项技能
- 想安装外部技能 → `/find-skills`
- 想查看本地技能文件 → `/find-local-skills`
- 想把经验变成技能 → `/skill-creator`

## 核心模型

技能系统分四层：

```text
外部发现层：/find-skills
本地管理层：/find-local-skills、/skill-index
经验蒸馏层：/skill-creator
领域执行层：各领域技能
```

本技能拥有层间协调逻辑。

## 存放位置

个人技能：

```bash
~/.claude/skills/<skill-name>/SKILL.md
```

项目技能：

```bash
<project>/.claude/skills/<skill-name>/SKILL.md
```

**禁止**嵌套分类目录（如 `skills/meta/skill-distiller/SKILL.md`）。

分类通过本技能、命名约定或 `SKILLS_INDEX.md` 实现。

## 同伴技能

| 技能 | 职责 |
|------|------|
| `/skill-index` | 路由、分类、治理 |
| `/find-local-skills` | 本地清单、审计 |
| `/find-skills` | 外部发现 |
| `/skill-creator` | 创建/蒸馏/改进 |
| `/skill-graph` | 关系可视化、元数据健康 |

## 默认路由逻辑

1. 任务涉及技能管理 → `/skill-index` 或 `/find-local-skills`
2. 查看已安装技能 → `/find-local-skills`
3. 找新外部技能 → `/find-skills`
4. 把经验变成技能 → `/skill-creator`
5. 匹配已知领域技能 → 推荐该技能
6. 无匹配 → 建议 `/skill-creator` 新建或 `/find-skills` 外部搜索

## 技能分类

| 分类 | 说明 | 示例 |
|------|------|------|
| 元技能 | 管理其他技能的技能 | skill-index, skill-graph, skill-creator |
| 规划与审查 | 计划、架构、风险、决策质量 | plan-review, risk-audit |
| 编码与调试 | 实现、重构、代码分析、bug 诊断 | codebase-recon |
| 测试与QA | 验证、回归安全、测试计划、覆盖率 | test-strategy-review |
| 文档与写作 | 文档、变更日志、规范、结构化写作 | docs-structure-review |
| 运维与发布 | 发布就绪、部署、回滚、监控 | release-checklist |
| 研究与发现 | 外部资源搜索、对比、信息收集 | find-skills |
| 设计与UI | UI/UX、布局、交互设计 | ui-review |
| 数据与分析 | 数据工作流、分析、报告 | data-analysis-review |
| 项目特定 | 绑定单一仓库/团队的技能 | — |

分类依据是技能的主要职责，非实现细节。

## 命名规则

- 小写、连字符、短、任务导向
- 足够具体以可靠路由

**好名字**：`skill-index`、`find-local-skills`、`skill-creator`、`plan-review`、`release-checklist`

**坏名字**：`my-skill`、`helper`、`general-tool`、`things-i-learned`

如果视觉分组需要，用前缀而非嵌套目录（如 `coding-matlab-gui`），但调用体验优先时用短名，分组留在索引里。

## 个人级 vs 项目级

**个人级**：跨项目通用、可复用工程判断、不绑定特定仓库

**项目级**：依赖项目架构/命令/API/路径、编码团队约定、在外部项目中使用有害或混乱

不确定时：可复用判断放个人级，仓库事实放 `CLAUDE.md` 或项目级技能，临时笔记放文档。

## 技能生命周期

```text
发现 → 蒸馏 → 创建 → 注册 → 审计 → 精炼
```

1. **发现**：创建前查 `/find-local-skills`，无本地技能时可选 `/find-skills`
2. **蒸馏**：从经验中提取可复用规则 → `/skill-creator distill`
3. **创建**：放到 `~/.claude/skills/<name>/SKILL.md` 或 `<project>/.claude/skills/<name>/SKILL.md`
4. **注册**：在 `SKILLS_INDEX.md` 中添加 `| \`skill-name\` | personal/project | 一句话用途 | \`/skill-name\` |`
5. **审计**：`/find-local-skills audit` 检查重复/模糊描述/过度触发/危险权限
6. **精炼**：根据实际使用补充边界情况、失效模式、验证检查

## 索引条目格式

```markdown
| `skill-name` | personal/project/external | 一句话用途 | `/skill-name` |
```

Scope 值：`personal`、`project`、`external`、`bundled`、`unknown`。

## 输出格式

### 决定用哪个技能时

```markdown
## 推荐技能
`/<skill-name>`
理由：...
## 替代方案
| Skill | 何时选用 |
```

### 分类决策时

```markdown
## 分类决策
分类：<category>
理由：...
索引条目：
| `skill-name` | personal/project | 一句话用途 | `/skill-name` |
```

### 审计时

```markdown
## 技能系统审计
| 问题 | 严重度 | 受影响技能 | 建议操作 |
```

严重度：`high`（危险权限、重复高影响技能、全局技能含项目特定内容）> `medium`（模糊描述、缺少输出期望、重叠）> `low`（命名清理、格式）。

### 索引更新时

返回完整 `SKILLS_INDEX.md` 或可粘贴的补丁区：

```markdown
## 索引更新
操作：新增/更新/移动/删除/合并
分类：<category>
条目：
| `skill-name` | personal/project | 一句话用途 | `/skill-name` |
```

## 冲突解决

两个技能重叠时：
1. 同名 → 保留窄的、安全的、项目级的
2. 合并重复检查清单
3. 重命名模糊技能
4. 归档或删除废弃技能
5. 处理后更新索引

## 安全规则

- 不推荐盲目安装外部技能
- 不推荐宽泛 `allowed-tools`（除非用户明确要求）
- 标记含 shell/write/delete/install/deploy/credential/network 权限的技能
- 高影响工作流推荐 `disable-model-invocation: true`
- 不将项目特定操作命令放入全局技能
- 不把一次性笔记变成技能
- 不在 `skills/` 下创建嵌套分类目录

## 与同伴技能的协作

- **skill-creator** 产出新技能 → 本技能决定名称、分类、scope、路径、索引条目
- **find-local-skills** 做实际本地检查 → 本技能设计分类和路由策略
- **find-skills** 安装外部技能 → 本技能检查、分类、加入索引、标记安全问题
- **skill-graph** 可视化 → 本技能提供分类和路由依据

## 运行节奏

```
新增技能后：/find-local-skills audit → /skill-index 更新索引
完成大量工作后：/skill-creator distill → /skill-index 分类
进入新项目时：/find-local-skills → /skill-index 项目技能映射
需要新能力时：/find-skills → /skill-index 分类已安装外部技能
```

## 最终规则

技能系统行为：

```text
发现 → 路由 → 执行 → 蒸馏 → 索引 → 审计 → 精炼
```

如果一个文件不能帮助路由、判断、工作流、验证或复用，就不该成为技能。
