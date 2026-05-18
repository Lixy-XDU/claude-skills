---
name: skill-updater
description: 从 claude-skills GitHub 仓库检查并拉取最新技能更新。触发场景：用户说"更新skills""检查更新""同步skills""/skill-updater"；或间隔一段时间未使用后准备开始新工作。
argument-hint: ""
disable-model-invocation: true
---

# 技能更新器

从 claude-skills GitHub 仓库拉取最新更新。

## 适用场景

- 用户说"更新 skills""检查更新""同步 skills"
- 用户运行 `/skill-updater`
- 间隔一段时间后准备开始新工作前

## 不适用场景

- 用户要修改或创建技能 → 用 `/skill-creator`
- 用户要找新技能 → 用 `/find-skills`
- 初次安装 → 按 README 说明操作

## 核心规则

- 只 `git fetch` + `git pull`，绝不 force-push、不 reset、不删除
- 拉取后更新 `~/.claude/CLAUDE.md`（从仓库模板）
- 技能变更后重建 `SKILL_GRAPH.html`
- **绝不覆盖 `config.local.yaml`**
- 更新后报告变更范围（commit range）

## 工作流

### 1. 检查技能仓库

```bash
SKILLS_DIR="$HOME/.claude/skills"
if [ -d "$SKILLS_DIR/.git" ]; then
  cd "$SKILLS_DIR"
  REMOTE=$(git remote get-url origin 2>/dev/null)
  echo "Skills remote: $REMOTE"
  git fetch origin
  BEHIND=$(git rev-list HEAD..origin/master --count)
  if [ "$BEHIND" -gt 0 ]; then
    echo "发现 $BEHIND 个新提交。正在拉取..."
    git log HEAD..origin/master --oneline
    git pull origin master
    HAS_SKILL_UPDATES=true
  else
    echo "技能：已是最新。"
  fi
else
  echo "技能目录不是 git 仓库，跳过。"
fi
```

### 2. 更新 CLAUDE.md

```bash
if [ "$HAS_SKILL_UPDATES" = true ]; then
  if [ -f "$SKILLS_DIR/CLAUDE.md" ]; then
    cp "$HOME/.claude/CLAUDE.md" "$HOME/.claude/CLAUDE.md.bak-$(date +%Y%m%d%H%M%S)"
    cp "$SKILLS_DIR/CLAUDE.md" "$HOME/.claude/CLAUDE.md"
    echo "CLAUDE.md 已更新（旧版本已备份）。"
  fi
fi
```

### 3. 重建技能图

```bash
GRAPH_SCRIPT="$SKILLS_DIR/skill-graph/scripts/generate_skill_graph_html.py"
if [ -f "$GRAPH_SCRIPT" ]; then
  python "$GRAPH_SCRIPT" --graph-only 2>/dev/null || py "$GRAPH_SCRIPT" --graph-only 2>/dev/null
  echo "SKILL_GRAPH.html 已重建。"
fi
```

### 4. 报告结果

汇总：技能是否更新、CLAUDE.md 是否变更。

## 安全规则

- 绝不 `git push`，此技能只读
- 绝不删除或覆盖 `config.local.yaml`
- 覆盖 CLAUDE.md 前先备份
- `git pull` 失败（合并冲突）时报错并停止，不尝试解决
