---
name: skill-rm
description: Delete a local Claude Code skill entirely. Use when the user wants to remove, uninstall, clean up, or get rid of a skill, or says "删除skill", "移除技能", "卸载skill", "rm skill". Also use when /skill-index detects an obsolete or duplicate skill that should be removed.
argument-hint: "<skill-name>"
disable-model-invocation: false
---

# Skill Remove

Delete a local skill — its directory, metadata, index entry, and graph node — in one pass.

## Use when

- User says "删除 skill X", "remove skill X", "卸载 X"
- A skill is confirmed obsolete, duplicate, or superseded
- `/skill-index` audit recommends deletion
- Cleanup after merging two skills

## Do not use when

- User only wants to temporarily hide a skill — use `/skill-disable`
- User wants to rename or reorganize — use `/skill-index`
- User wants to uninstall an external/plugin skill — those live outside `~/.claude/skills/`

## Workflow

### 1. Identify the target

The user must provide the skill name (the directory name under `~/.claude/skills/`, e.g., `ml-traditional-gui`).

If the name is ambiguous, list candidates and ask the user to pick one.

### 2. Safety check

Before deleting, check and report:

```text
- Skill path: ~/.claude/skills/<name>/
- Scope (from skill.meta.yaml): personal / project / external
- Referenced by other skills (who lists this skill in their relations):
    - upstream of: ...
    - downstream of: ...
    - cooperates_with: ...
```

If other skills reference this skill in their `skill.meta.yaml` relations, warn the user and list which skills and which relation fields would break. **Do not delete until the user confirms** they understand the broken references.

### 3. Confirm

Show the user exactly what will happen and ask for explicit confirmation:

```text
The following will be deleted:
  - Directory: ~/.claude/skills/<name>/
  - All files within it (SKILL.md, skill.meta.yaml, scripts/, references/, ...)

This action CANNOT be undone (unless the skill is still in the git repo).

Proceed? (yes/no)
```

### 4. Delete

If confirmed:

```bash
rm -rf ~/.claude/skills/<name>/
```

### 5. Update the skill index

Remove the skill's row from `~/.claude/skills/SKILLS_INDEX.md`.

If the skill is the last one in its category section, remove the empty section.

### 6. Rebuild skill graph

```bash
python ~/.claude/skills/skill-graph/scripts/generate_skill_graph_html.py --graph-only
```

### 7. Handle git repo (if applicable)

If the skill exists in `D:\git仓库\claude-skills\skills\`, also delete it there:

```bash
rm -rf <git-repo>/skills/<name>/
cd <git-repo> && git add -A && git commit -m "chore(skills): remove <name>"
```

Do NOT auto-push. Tell the user the commit was made locally and they can push when ready.

### 8. Update CHANGELOG

Append to both `~/.claude/skills/CHANGELOG.md` and `<git-repo>/skills/CHANGELOG.md`:

```markdown
- **remove**: `skill-name` — <brief reason>
```

### 9. Report

Summarize what was done:

```text
Deleted: ~/.claude/skills/<name>/
Index: removed from SKILLS_INDEX.md
Graph: SKILL_GRAPH.html rebuilt
Git: committed to claude-skills (not pushed)
```

## Edge cases

- **Skill not found**: search with `find ~/.claude/skills -maxdepth 1 -type d -name "*<query>*"` and show candidates
- **Skill is a plugin namespace** (e.g., `matlab-core:matlab-create-live-script`): these live in managed plugin directories, not under `~/.claude/skills/`. Tell the user to uninstall via the plugin manager
- **Multiple matches**: show all and ask which one
- **Git repo not found**: skip git steps, note as warning

## Safety rules

- ALWAYS confirm before deleting
- ALWAYS check for cross-references before deleting
- Never delete skills outside `~/.claude/skills/` without explicit user instruction
- Never force-push
- Back up the SKILLS_INDEX.md before editing (copy to SKILLS_INDEX.md.bak)
