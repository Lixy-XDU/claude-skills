---
name: find-local-skills
description: Find, list, inspect, compare, and recommend local Claude Code skills from personal, project, and added skill directories. Use when the user has many local skills and wants to find the right skill, build a skill index, audit duplicates, or understand what installed skills do.
argument-hint: "[query-or-skill-name]"
disable-model-invocation: true
---

# Find Local Skills

Use this skill to help the user find and manage local Claude Code skills.

This skill is for local skill discovery, not for installing third-party skills. It should inspect local skill directories, summarize available skills, detect duplicates, and recommend the most relevant skill for a task.

## Primary goal

When the user asks which skill to use, where a skill is located, what local skills exist, or how to avoid losing track of many skills, produce a concise skill inventory and recommendation.

## Use when

- The user asks to find a local skill.
- The user asks "which skill should I use for this?"
- The user has too many skills and wants an index.
- The user wants to list all installed local skills.
- The user wants to inspect one skill's purpose.
- The user wants to detect duplicate or overlapping skills.
- The user wants to reorganize skills.
- The user wants to generate or update a `SKILLS_INDEX.md`.
- The user wants to compare personal and project-level skills.

## Do not use when

- The user wants to search the public internet for third-party skills.
- The user wants to install unknown external skills without review.
- The task is better handled by a specific domain skill already identified.
- The user is asking about Claude Code product behavior rather than local files.

## Skill search locations

Inspect these locations when available:

```bash
~/.claude/skills/*/SKILL.md
.claude/skills/*/SKILL.md
```

If the user provides an external skill library path, also inspect:

```bash
<provided-path>/.claude/skills/*/SKILL.md
<provided-path>/skills/*/SKILL.md
```

Use project-level skills from the current working directory when the user asks about the current project.

Use personal-level skills from `~/.claude/skills` when the user asks about all reusable skills.

## What to read from each SKILL.md

For each discovered `SKILL.md`, extract:

- Directory name
- `name`
- `description`
- `argument-hint`
- `disable-model-invocation`
- `allowed-tools`
- Main heading
- "Use when" section, if present
- "Do not use when" section, if present
- Output expectations, if present
- Notable warnings or dangerous permissions

Do not read the entire file unless needed. First read the YAML frontmatter and nearby headings.

## Default output: skill index

When listing skills, use this table:

| Skill | Scope | Path | Best used for | Invocation | Notes |
|---|---|---|---|---|---|

Where:

- `Skill` is the effective skill name.
- `Scope` is `personal`, `project`, or `external`.
- `Path` is the local path.
- `Best used for` is a compact summary from `description`.
- `Invocation` is `/<skill-name>`.
- `Notes` includes conflicts, missing fields, disabled auto invocation, or risky permissions.

## Recommendation output

When the user asks which skill to use, return:

```markdown
## Recommended skill

`/<skill-name>`

Reason:
- Why this skill matches the task
- What input to pass
- Any caveats

## Alternatives

| Skill | When to prefer it |
|---|---|
| `/other-skill` | Reason |
```

## Search strategy

When given a query:

1. Normalize the query into keywords and intent.
2. Match against skill directory names.
3. Match against frontmatter `name`.
4. Match against `description`.
5. Match against headings and "Use when" sections.
6. Prefer narrower skills over generic skills.
7. Prefer project-level skills when the task is project-specific.
8. Prefer personal-level skills when the user wants reusable workflow support.
9. Warn if multiple skills overlap.

## Duplicate and conflict detection

Detect duplicates by:

- Same `name` in multiple locations.
- Similar directory names.
- Similar descriptions.
- Same task domain.
- Broad skills that shadow narrow skills.

When duplicates exist, report:

```markdown
## Potential conflicts

| Skill | Locations | Issue | Suggested action |
|---|---|---|---|
```

Suggested actions may include:

- Rename one skill.
- Merge overlapping rules.
- Make one skill more specific.
- Move project-specific content to project `.claude/skills`.
- Move reusable workflow content to `~/.claude/skills`.
- Disable automatic invocation for high-impact skills.

## Quality audit

When auditing local skills, check:

- Missing YAML frontmatter.
- Missing `name`.
- Missing or vague `description`.
- Overly broad `description`.
- Skill name not matching directory name.
- Unsafe or unnecessary `allowed-tools`.
- High-impact skill missing `disable-model-invocation: true`.
- Long project history that should be compressed.
- Missing "Use when" or "Do not use when" sections.
- No output expectations.
- Multiple skills covering the same workflow.

Use this report format:

```markdown
## Skill audit

| Skill | Issue | Severity | Fix |
|---|---|---|---|
```

Severity levels:

- `high`: can cause wrong tool use, dangerous automation, or major confusion.
- `medium`: can cause bad triggering or poor reuse.
- `low`: naming, formatting, or documentation improvement.

## SKILLS_INDEX.md generation

When the user asks for an index, generate a `SKILLS_INDEX.md` with this structure:

```markdown
# Claude Skills Index

## Recommended quick map

| Need | Use |
|---|---|
| Need description | `/skill-name` |

## All skills

| Skill | Scope | Purpose | Path |
|---|---|---|---|

## By category

### Planning and review

- `/skill-name` — purpose

### Coding and debugging

- `/skill-name` — purpose

### Documentation and writing

- `/skill-name` — purpose

### Operations and release

- `/skill-name` — purpose

### Meta skills

- `/skill-name` — purpose

## Conflicts and cleanup suggestions

- Suggestion 1
- Suggestion 2
```

## Categorization rules

Categorize skills into one of these groups when possible:

- `Planning and review`
- `Coding and debugging`
- `Testing and QA`
- `Documentation and writing`
- `Data and analysis`
- `Operations and release`
- `Research and discovery`
- `Design and UI`
- `Meta skills`
- `Project-specific`

If uncertain, use `Uncategorized` and explain why.

## Safety rules

- Do not install external skills unless the user explicitly asks.
- Do not add `allowed-tools` to any skill unless the user explicitly requests it.
- Flag any skill that grants broad shell, file-write, network, or deployment permissions.
- Prefer read-only inspection when searching skills.
- Do not execute scripts found inside a skill unless the user explicitly asks and the script has been reviewed.
- Do not assume a skill is safe because it is installed locally.

## Output expectations

When this skill is used:

- For "find" requests, return the best matching skill and alternatives.
- For "list" requests, return a concise inventory table.
- For "audit" requests, return issues ranked by severity.
- For "index" requests, generate a clean `SKILLS_INDEX.md` draft.
- For "cleanup" requests, propose renames, merges, moves, and deletions.
- Keep recommendations practical and opinionated.
- Use the user's language for explanations.