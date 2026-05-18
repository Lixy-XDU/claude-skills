---
name: find-skills
description: 帮助用户从开放技能生态中发现和安装技能。触发场景：用户问"怎么找到X的skill""有没有X技能""帮我找一个skill"；或本地技能库缺少所需能力，需要外部搜索。
---

# 查找外部技能

从开放的 agent skills 生态中发现并安装技能。

## 适用场景

- 用户问"怎么做 X"，X 可能是已有技能覆盖的常见任务
- 用户说"帮我找一个 X 技能""有没有 X 技能"
- 用户希望扩展能力但没有本地对应技能
- 用户提到某个领域有需求（设计、测试、部署等）

## Skills CLI 简介

Skills CLI（`npx skills`）是开放技能生态的包管理器。

**核心命令：**
- `npx skills find [query]` — 交互式或关键词搜索
- `npx skills add <package>` — 从 GitHub 等源安装技能
- `npx skills check` — 检查更新
- `npx skills update` — 更新全部已安装技能

**浏览技能：** https://skills.sh/

## 查找流程

### 1. 理解需求

识别用户需求的领域、具体任务，以及是否足够常见以至于大概率已有现成技能。

### 2. 先看排行榜

在运行 CLI 搜索前，先查看 [skills.sh 排行榜](https://skills.sh/)，排行榜按总安装量排序。

例如 Web 开发的热门技能：
- `vercel-labs/agent-skills` — React、Next.js、Web 设计（各 100K+ 安装）
- `anthropics/skills` — 前端设计、文档处理（100K+ 安装）

### 3. 搜索

排行榜不覆盖时运行：

```bash
npx skills find [query]
```

例子：
- "帮我优化 React 性能" → `npx skills find react performance`
- "帮我做 PR review" → `npx skills find pr review`

### 4. 质量验证

推荐前验证：
1. **安装量** — 优先 1K+ 安装的技能；100 以下须谨慎
2. **来源声誉** — 官方来源（`vercel-labs`、`anthropics`、`microsoft`）比未知作者可靠
3. **GitHub stars** — 源仓库 <100 stars 应持怀疑态度

### 5. 展示选项

找到后展示：技能名及功能、安装量及来源、安装命令、skills.sh 链接。

```
我找到了一个可能帮到你的技能！"react-best-practices" 来自 Vercel Engineering，
提供 React/Next.js 性能优化指南（185K 安装）。

安装命令：
npx skills add vercel-labs/agent-skills@react-best-practices

详情：https://skills.sh/vercel-labs/agent-skills/react-best-practices
```

### 6. 提供安装

用户同意后安装：

```bash
npx skills add <owner/repo@skill> -g -y
```

`-g` 全局安装，`-y` 跳过确认。

## 常见分类

| 分类 | 关键词示例 |
|------|----------|
| Web 开发 | react, nextjs, typescript, css, tailwind |
| 测试 | testing, jest, playwright, e2e |
| DevOps | deploy, docker, kubernetes, ci-cd |
| 文档 | docs, readme, changelog, api-docs |
| 代码质量 | review, lint, refactor, best-practices |
| 设计 | ui, ux, design-system, accessibility |
| 效率 | workflow, automation, git |

## 搜索技巧

1. 用具体关键词："react testing" 比 "testing" 好
2. 尝试同义词："deploy" 不行就试 "deployment" 或 "ci-cd"
3. 关注热门源：`vercel-labs/agent-skills`、`ComposioHQ/awesome-claude-skills`

## 找不到时

1. 告知未找到现成技能
2. 提出用通用能力直接帮助
3. 建议用户可自行创建：`npx skills init <name>`
