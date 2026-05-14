---
name: skill-updater
description: Update installed Claude Code skills from the claude-skills GitHub repository. Use when the user wants to check for updates, pull the latest skills, sync with upstream, or run `/skill-updater`.
argument-hint: ""
disable-model-invocation: true
---

# Skill Updater

Check for and apply updates from the claude-skills GitHub repository.

## Use when

- User asks "update skills", "check for updates", "sync skills"
- User runs `/skill-updater`
- User wants the latest version of installed skills
- After a gap in usage, before starting new work

## Do not use when

- User wants to modify or create skills (use `/skill-creator` or `/skill-distiller`)
- User wants to find new skills (use `/find-skills`)
- Initial installation (use README instructions)

## Core rules

- Only `git fetch` + `git pull` — never force-push, never reset, never delete
- Update `~/.claude/CLAUDE.md` from repo template after pull
- Rebuild `SKILL_GRAPH.html` after skill changes
- Do NOT overwrite `config.local.yaml` under any circumstances
- Report what changed (commit range) after update

## Workflow

### 1. Check skills repo

```bash
SKILLS_DIR="$HOME/.claude/skills"
if [ -d "$SKILLS_DIR/.git" ]; then
  cd "$SKILLS_DIR"
  REMOTE=$(git remote get-url origin 2>/dev/null)
  echo "Skills remote: $REMOTE"
  git fetch origin
  BEHIND=$(git rev-list HEAD..origin/master --count)
  if [ "$BEHIND" -gt 0 ]; then
    echo "Found $BEHIND new commit(s). Pulling..."
    git log HEAD..origin/master --oneline
    git pull origin master
    HAS_SKILL_UPDATES=true
  else
    echo "Skills: already up to date."
  fi
else
  echo "Skills directory is not a git repo — skipping."
fi
```

### 2. Update CLAUDE.md

If skills were updated, copy the latest template:

```bash
if [ "$HAS_SKILL_UPDATES" = true ]; then
  if [ -f "$SKILLS_DIR/CLAUDE.md" ]; then
    cp "$HOME/.claude/CLAUDE.md" "$HOME/.claude/CLAUDE.md.bak-$(date +%Y%m%d%H%M%S)"
    cp "$SKILLS_DIR/CLAUDE.md" "$HOME/.claude/CLAUDE.md"
    echo "CLAUDE.md updated (old version backed up)."
  fi
fi
```

### 3. Rebuild skill graph

```bash
GRAPH_SCRIPT="$SKILLS_DIR/skill-graph/scripts/generate_skill_graph_html.py"
if [ -f "$GRAPH_SCRIPT" ]; then
  python "$GRAPH_SCRIPT" --graph-only 2>/dev/null || py "$GRAPH_SCRIPT" --graph-only 2>/dev/null
  echo "SKILL_GRAPH.html rebuilt."
fi
```

### 4. Report results

After all steps, summarize:
- Skills: up to date / updated from `<old>` to `<new>`
- CLAUDE.md: unchanged / updated

## Safety rules

- Never run `git push` — this skill is read-only from GitHub's perspective
- Never delete or overwrite `config.local.yaml`
- Back up CLAUDE.md before overwriting
- If `git pull` fails (merge conflict), report the error and stop — do not attempt resolution
