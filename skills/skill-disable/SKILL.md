---
name: skill-disable
description: Disable or re-enable a local Claude Code skill or a category of skills. Use when the user wants to temporarily turn off a skill, disable a group of skills by prefix/pattern, stop a skill from triggering, or re-enable a previously disabled skill. Phrases: "禁用skill", "停用技能", "暂时关闭", "disable skill X", "关掉所有matlab相关的skill", "启用skill", "重新打开", "enable skill".
argument-hint: "<skill-name-or-pattern> [--enable]"
disable-model-invocation: false
---

# Skill Disable / Enable

Temporarily disable one or more skills without deleting them. The skill files stay on disk but Claude Code stops loading them. Re-enabling is a single command.

## Mechanism

Disabling works by renaming the skill's entry point:

```text
SKILL.md  →  SKILL.md.disabled
```

Claude Code looks for `SKILL.md` to load a skill. Renaming it to `SKILL.md.disabled` makes the skill invisible to the harness while keeping all files intact. The `skill.meta.yaml` status is also updated to `disabled`.

Re-enabling renames it back:

```text
SKILL.md.disabled  →  SKILL.md
```

## Use when

- User wants to temporarily stop a skill from triggering
- User says "disable skill X", "turn off X", "停用 X"
- User wants to disable all skills matching a prefix ("disable all matlab-*")
- User wants to disable all skills in a category
- User wants to re-enable a previously disabled skill
- Testing whether a skill is causing interference

## Do not use when

- User wants to permanently delete a skill — use `/skill-rm`
- User wants to modify a skill's behavior — edit SKILL.md directly
- User wants to fix a broken skill — use `/skill-creator`

## Workflow

### 1. Resolve the target

The target can be:

| Form | Example | Meaning |
|------|---------|---------|
| Exact name | `ml-traditional-gui` | That specific skill |
| Prefix with `*` | `matlab-*` | All skills whose directory name starts with `matlab-` |
| Prefix with `*` | `nature-*` | All skills starting with `nature-` |
| Category word | `matlab` | All skills containing "matlab" in name or category |
| `--all` | `--all` | All local skills (dangerous, require confirmation) |

If re-enabling, use `--enable`:

```text
/skill-disable ml-traditional-gui --enable
/skill-disable matlab-* --enable
```

### 2. Find matching skills

Search `~/.claude/skills/` for matching directories:

```bash
# List all local skill directories
ls -d ~/.claude/skills/*/SKILL.md ~/.claude/skills/*/SKILL.md.disabled 2>/dev/null
```

Filter by the target pattern. Show the user which skills match and their current status (active / disabled).

### 3. Confirm

Show what will happen:

```text
Skills to DISABLE (3):
  - matlab-core:matlab-create-live-script  (currently active)
  - matlab-core:matlab-testing             (currently active)
  - matlab-app-building:matlab-build-app   (currently active)

These skills will stop appearing in Claude Code. Files stay on disk.
Re-enable with: /skill-disable matlab-* --enable

Proceed? (yes/no)
```

For re-enable:

```text
Skills to ENABLE (2):
  - ml-traditional-gui     (currently disabled)
  - desktop-computer-automation (currently disabled)

Proceed? (yes/no)
```

### 4. Execute

For each matching skill:

**Disable:**
```bash
cd ~/.claude/skills/<name>/
mv SKILL.md SKILL.md.disabled
```

Then update `skill.meta.yaml`:
```yaml
status: disabled
```

**Enable:**
```bash
cd ~/.claude/skills/<name>/
mv SKILL.md.disabled SKILL.md
```

Then update `skill.meta.yaml`:
```yaml
status: active
```

### 5. Update index and graph

After any disable/enable operation:

1. Regenerate `SKILL_GRAPH.html`:
   ```bash
   python ~/.claude/skills/skill-graph/scripts/generate_skill_graph_html.py --graph-only
   ```

2. Update `SKILLS_INDEX.md`: add `(已禁用)` or `(disabled)` annotation to disabled skills' entries, remove annotation for re-enabled skills.

3. If the skill exists in git repo (`D:\git仓库\claude-skills\`), mirror the disable/enable there too and commit.

### 6. Update CHANGELOG

```markdown
- **disable**: `skill-name` — <brief reason or "batch: matlab-*">
- **enable**: `skill-name`
```

### 7. Report

```text
Disabled (3): matlab-core:matlab-create-live-script, matlab-core:matlab-testing, matlab-app-building:matlab-build-app
Graph: SKILL_GRAPH.html rebuilt
Index: SKILLS_INDEX.md updated
```

## Edge cases

- **Skill already in target state**: skip and note
- **No skills match the pattern**: list all available skill names and suggest alternatives
- **Plugin namespaced skills** (e.g., `matlab-core:matlab-create-live-script`): these are managed by plugin systems. Check if the skill directory actually exists under `~/.claude/skills/` — if not, tell user to disable via plugin config
- **Disabling a meta-skill** (skill-index, skill-graph, skill-rm, skill-disable): warn the user that this may break skill management
- **Disabling all skills with `--all`**: require double confirmation

## Safety rules

- Never delete files — only rename
- Always confirm before batch operations
- Warn when disabling meta-skills
- Keep disabled skills in git (they're part of the repo history)
- Back up SKILLS_INDEX.md before editing
