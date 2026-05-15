---
name: skill-index
description: Coordinate, categorize, route, audit, and maintain local Claude Code skills. Use when the user wants to decide which skill to use, organize skills by function, update the skill index, coordinate find-local-skills, find-skills, and skill-distiller, or prevent local skill sprawl.
argument-hint: "[task-or-skill-topic]"
disable-model-invocation: false
---

# Skills Index

Use this skill as the coordination layer for the user's Claude Code skills.

This skill does not replace domain-specific skills. It routes tasks to the right skill, maintains the skill taxonomy, coordinates meta skills, and prevents the local skill library from becoming disorganized.

Core purpose:

```text
task → category → best skill → action → index update
```

## Use when

Use this skill when the user asks to:

- Decide which skill should handle a task.
- Organize skills by function.
- Build or update a skill index.
- Coordinate multiple skills.
- Categorize a new skill.
- Decide whether a skill should be personal or project-level.
- Detect overlap between skills.
- Plan a local skill library structure.
- Clean up skill sprawl.
- Define how `/find-local-skills`, `/find-skills`, and `/skill-distiller` should work together.
- Create a routing map for commonly used skills.
- Generate or revise a `SKILLS_INDEX.md` auxiliary document.
- Convert a loose skill list into a maintainable skill system.

## Do not use when

Do not use this skill when:

- The user already knows the exact domain skill to invoke.
- The user only wants to execute a specific coding/debugging/review task.
- The task belongs clearly to a specialized skill.
- The user wants to install an external skill directly; use `/find-skills`.
- The user wants to inspect local skill files directly; use `/find-local-skills`.
- The user wants to convert raw experience into a new skill; use `/skill-distiller`.

## Core model

The user's skill system has three layers:

```text
External discovery layer:
  /find-skills

Local management layer:
  /find-local-skills
  /skills-index

Experience distillation layer:
  /skill-distiller

Domain execution layer:
  /plan-review
  /risk-audit
  /ml-traditional-gui
  /codebase-recon
  /release-checklist
  ...
```

This skill owns the coordination logic between those layers.

## Recommended locations

Personal skills should usually live here:

```bash
~/.claude/skills/<skill-name>/SKILL.md
```

Project-specific skills should usually live here:

```bash
<project>/.claude/skills/<skill-name>/SKILL.md
```

Do not create nested category folders like this:

```bash
~/.claude/skills/meta/skill-distiller/SKILL.md
~/.claude/skills/coding/ml-traditional-gui/SKILL.md
```

Claude Code expects each skill to live directly under `skills/<skill-name>/SKILL.md`.

Use this skill, naming conventions, or an auxiliary `SKILLS_INDEX.md` file for categorization.

## Companion skills

This skill coordinates these meta skills:

| Skill | Role | Use when |
|---|---|---|
| `/skills-index` | Route, categorize, coordinate, and govern the local skill system | The user needs a skill map or coordination decision |
| `/find-local-skills` | Search, list, inspect, compare, and audit installed local skills | The user needs to know what is already installed |
| `/find-skills` | Search external/community skills | The user needs new capabilities not available locally |
| `/skill-distiller` | Convert raw work experience into reusable `SKILL.md` files | The user has notes, lessons, or workflows to preserve |

## Default routing logic

When the user describes a task, route it as follows:

1. If the task is about managing skills, use `/skills-index` or `/find-local-skills`.
2. If the task is about finding installed skills, use `/find-local-skills`.
3. If the task is about finding new external skills, use `/find-skills`.
4. If the task is about turning experience into a skill, use `/skill-distiller`.
5. If the task matches a known domain-specific skill, recommend that skill.
6. If no matching skill exists, recommend either:
   - create a new skill with `/skill-distiller`, or
   - search externally with `/find-skills`.

## Quick routing map

| User need | Recommended skill | Reason |
|---|---|---|
| “我该用哪个 skill？” | `/skills-index` | Decide the routing category and next skill |
| “我本地有哪些 skill？” | `/find-local-skills` | Inspect installed local skills |
| “帮我找一个外部 skill” | `/find-skills` | Search external/community skill sources |
| “把这次经验沉淀成 skill” | `/skill-distiller` | Convert experience into reusable `SKILL.md` |
| “本地 skill 太多，帮我整理” | `/find-local-skills` then `/skills-index` | First inspect, then reorganize |
| “这个 skill 应该放哪类？” | `/skills-index` | Categorize and update index |
| “这个 skill 有没有必要？” | `/skill-distiller` | Apply skill creation decision rule |
| “这个 skill 和别的重复吗？” | `/find-local-skills` then `/skills-index` | Detect overlap, then decide merge/rename |
| “给我一个技能库结构” | `/skills-index` | Design taxonomy and governance |
| “生成 SKILLS_INDEX.md” | `/skills-index` | Produce auxiliary index document |

## Skill categories

Use these categories by default.

### Meta skills

Skills that create, search, manage, audit, or coordinate other skills.

Examples:

```text
/skills-index
/find-local-skills
/find-skills
/skill-distiller
```

### Planning and review

Skills for plans, architecture, migrations, risk, sequencing, and decision quality.

Examples:

```text
/plan-review
/risk-audit
/migration-risk-audit
```

### Coding and debugging

Skills for implementation, refactoring, codebase analysis, and bug diagnosis.

Examples:

```text
/codebase-recon
/bug-pattern-extractor
/ml-traditional-gui
```

### Testing and QA

Skills for validation, regression safety, test planning, coverage, and QA review.

Examples:

```text
/test-strategy-review
```

### Documentation and writing

Skills for documentation, changelogs, specs, explanations, and structured writing.

Examples:

```text
/docs-structure-review
/changelog-writer
```

### Operations and release

Skills for release readiness, deployment, rollback, monitoring, and production safety.

Examples:

```text
/release-checklist
/deployment-review
/rollback-plan
```

### Research and discovery

Skills for external research, comparison, public information gathering, and tool discovery.

Examples:

```text
/find-skills
/research-brief
```

### Design and UI

Skills for UI, UX, layout, visual structure, interaction design, and frontend behavior.

Examples:

```text
/ml-traditional-gui
/ui-review
/frontend-component-design
```

### Data and analysis

Skills for data workflows, analysis, reporting, metrics, and interpretation.

Examples:

```text
/data-analysis-review
/metrics-audit
```

### Project-specific

Skills tied to one repository, team, architecture, or deployment environment.

These should usually live in:

```bash
<project>/.claude/skills/<skill-name>/SKILL.md
```

## Category selection rules

When categorizing a skill:

1. Choose the category based on the skill's primary job, not its implementation detail.
2. If a skill manages skills, classify it as `Meta skills`.
3. If a skill prevents bad decisions before implementation, classify it as `Planning and review`.
4. If a skill directly guides code writing or debugging, classify it as `Coding and debugging`.
5. If a skill verifies correctness, classify it as `Testing and QA`.
6. If a skill produces written artifacts, classify it as `Documentation and writing`.
7. If a skill affects production, deployment, rollback, or monitoring, classify it as `Operations and release`.
8. If a skill searches external resources, classify it as `Research and discovery`.
9. If a skill depends on one repo's commands or architecture, classify it as `Project-specific`.

If a skill fits multiple categories, choose the one that best predicts when the user would invoke it.

## Naming rules

Skill names should be:

- lowercase
- hyphenated
- short
- task-oriented
- specific enough to route reliably

Good names:

```text
skills-index
find-local-skills
skill-distiller
plan-review
risk-audit
codebase-recon
matlab-traditional-gui
migration-risk-audit
release-checklist
test-strategy-review
```

Bad names:

```text
my-skill
helper
general-tool
things-i-learned
project-notes
work-summary
useful-stuff
```

If visual grouping is needed, prefer prefixes over nested folders:

```text
meta-skills-index
planning-plan-review
coding-matlab-traditional-gui
ops-release-checklist
```

However, when invocation ergonomics matter, prefer shorter names and maintain grouping in the index.

## Personal vs project-level decision

Recommend a personal/global skill when:

- The workflow applies across multiple projects.
- The skill captures general engineering judgment.
- The skill is not tied to one repository's commands.
- The skill is reusable in future unrelated work.

Use:

```bash
~/.claude/skills/<skill-name>/SKILL.md
```

Recommend a project-level skill when:

- The skill depends on project architecture.
- The skill uses project-specific commands.
- The skill encodes team conventions.
- The skill references internal paths, APIs, deployment details, or local scripts.
- The skill would be harmful or confusing outside the project.

Use:

```bash
<project>/.claude/skills/<skill-name>/SKILL.md
```

If uncertain:

- Put reusable judgment in a personal skill.
- Put repository facts in `CLAUDE.md` or a project-level skill.
- Put temporary notes in documentation, not in a skill.

## Skill lifecycle

### 1. Discover

Before creating a new skill, check whether one already exists.

Recommended command:

```text
/find-local-skills <topic>
```

If no local skill fits, optionally search external skills:

```text
/find-skills <topic>
```

### 2. Distill

If the work experience contains reusable judgment, use:

```text
/skill-distiller <notes>
```

The goal is not to summarize everything. The goal is to extract repeatable rules, constraints, workflows, checks, and output expectations.

### 3. Create

Create a skill at:

```bash
~/.claude/skills/<skill-name>/SKILL.md
```

or:

```bash
<project>/.claude/skills/<skill-name>/SKILL.md
```

### 4. Register

Add or update its entry in the index.

Minimum entry format:

```markdown
| `skill-name` | personal/project/external | One-sentence purpose | `/skill-name` |
```

### 5. Audit

After adding or changing skills, run:

```text
/find-local-skills audit
```

Look for:

- duplicate skills
- vague descriptions
- overly broad triggers
- missing output expectations
- project-specific content in global skills
- dangerous tool permissions
- missing manual invocation guard for high-impact workflows

### 6. Refine

Update skills after real use if they miss:

- edge cases
- failure modes
- validation checks
- output constraints
- trigger exclusions
- safety rules
- index category

## Standard index entry

Use this table format for skill index entries:

```markdown
| Skill | Scope | Purpose | Invocation |
|---|---|---|---|
| `skill-name` | personal | One-sentence purpose | `/skill-name` |
```

Scope values:

```text
personal
project
external
bundled
unknown
```

## Standard SKILLS_INDEX.md structure

When generating an auxiliary `SKILLS_INDEX.md`, use this structure:

```markdown
# Claude Skills Index

## Quick routing map

| Need | Use | Purpose |
|---|---|---|

## Meta skills

| Skill | Scope | Purpose | Invocation |
|---|---|---|---|

## Planning and review

| Skill | Scope | Purpose | Invocation |
|---|---|---|---|

## Coding and debugging

| Skill | Scope | Purpose | Invocation |
|---|---|---|---|

## Testing and QA

| Skill | Scope | Purpose | Invocation |
|---|---|---|---|

## Documentation and writing

| Skill | Scope | Purpose | Invocation |
|---|---|---|---|

## Operations and release

| Skill | Scope | Purpose | Invocation |
|---|---|---|---|

## Research and discovery

| Skill | Scope | Purpose | Invocation |
|---|---|---|---|

## Design and UI

| Skill | Scope | Purpose | Invocation |
|---|---|---|---|

## Data and analysis

| Skill | Scope | Purpose | Invocation |
|---|---|---|---|

## Project-specific

| Skill | Scope | Purpose | Invocation |
|---|---|---|---|

## Cleanup recommendations

- Recommendation 1
- Recommendation 2
```

## Required output formats

### When the user asks which skill to use

Return:

```markdown
## Recommended skill

`/<skill-name>`

Reason:
- Why this skill fits
- What input to pass
- Any caveats

## Alternatives

| Skill | When to prefer it |
|---|---|
| `/other-skill` | Reason |
```

### When the user asks to categorize a skill

Return:

```markdown
## Category decision

Category: <category>

Reason:
- Reason 1
- Reason 2

Index entry:

| `skill-name` | personal/project/external | One-sentence purpose | `/skill-name` |
```

### When the user asks to update the index

Return either:

1. the full revised `SKILLS_INDEX.md`, or
2. a patch section that can be pasted into the existing index.

Use this format:

```markdown
## Index update

Action: Add / Update / Move / Remove / Merge

Category: <category>

Entry:

| `skill-name` | personal/project/external | One-sentence purpose | `/skill-name` |
```

### When the user asks to audit the skill system

Return:

```markdown
## Skill system audit

| Issue | Severity | Affected skills | Recommended action |
|---|---|---|---|
```

Severity levels:

```text
high
medium
low
```

Use `high` for:

- dangerous permissions
- duplicate high-impact skills
- unclear deployment/release/migration skills
- project-specific commands in global skills
- broad auto-triggering skill descriptions

Use `medium` for:

- vague descriptions
- missing output expectations
- missing validation checklists
- overlapping non-dangerous skills

Use `low` for:

- naming cleanup
- categorization clarity
- formatting issues

## Conflict resolution rules

When two skills overlap:

1. Keep the narrower skill if it has a clearer trigger.
2. Keep the safer skill if one has unnecessary tool permissions.
3. Keep the project-level skill for project-specific workflows.
4. Keep the personal-level skill for reusable judgment.
5. Merge duplicated checklists.
6. Rename vague skills.
7. Archive or delete obsolete skills.
8. Update the index after the decision.

Conflict output:

```markdown
## Conflict decision

| Skills | Conflict | Decision |
|---|---|---|
| `/skill-a`, `/skill-b` | Both handle the same task | Keep `/skill-a`; merge useful rules from `/skill-b` |
```

## Safety rules

When coordinating skills:

- Do not recommend blind installation of external skills.
- Do not recommend broad `allowed-tools` unless the user explicitly asks.
- Flag skills that include shell, write, delete, install, deploy, credential, or network permissions.
- Prefer `disable-model-invocation: true` for high-impact workflows.
- Prefer explicit invocation for release, migration, deployment, shell, destructive, or permission-sensitive skills.
- Do not move project-specific operational commands into global skills.
- Do not turn one-off notes into skills.
- Do not create nested category folders under `skills/`.

## High-impact skill policy

High-impact skills include:

- deployment
- release
- migration
- shell automation
- file deletion
- git history rewrite
- credential handling
- infrastructure modification
- database changes
- production debugging

For these, recommend:

```yaml
disable-model-invocation: true
```

and avoid `allowed-tools` unless the user explicitly wants pre-authorization.

## Integration with skill-distiller

When `/skill-distiller` produces a new skill, this skill should help decide:

- skill name
- category
- scope
- path
- index entry
- overlap with existing skills
- whether it should be merged instead of created

A new skill from `/skill-distiller` should usually produce:

```markdown
Recommended category: <category>
Recommended path: ~/.claude/skills/<skill-name>/SKILL.md

Index entry:

| `skill-name` | personal | One-sentence purpose | `/skill-name` |
```

## Integration with find-local-skills

Use `/find-local-skills` when the task requires actual local inspection.

This skill can design the taxonomy and routing policy, but `/find-local-skills` should inspect:

```bash
~/.claude/skills/*/SKILL.md
.claude/skills/*/SKILL.md
```

Use `/find-local-skills` before finalizing:

- merges
- deletions
- duplicate reports
- inventory tables
- index updates based on actual installed files

## Integration with find-skills

Use `/find-skills` when the local library lacks a required capability.

After installing an external skill:

1. inspect it
2. classify it
3. add it to the index
4. flag any safety concerns
5. decide whether a local wrapper/customized skill is needed

## Operating rhythm

After adding a skill:

```text
/find-local-skills audit
/skills-index update index
```

After finishing substantial work:

```text
/skill-distiller <notes>
/skills-index categorize new skill
```

When entering a new project:

```text
/find-local-skills current project
/skills-index project skill map
```

When needing unfamiliar capability:

```text
/find-skills <task-or-tool>
/skills-index categorize installed external skill
```

## Output expectations

When this skill is used:

- Route the user to the best skill.
- Explain why that skill fits.
- Recommend whether to use local, external, or newly distilled skills.
- Categorize skills consistently.
- Produce index entries in a paste-ready format.
- Keep the skill library flat under `skills/<skill-name>/SKILL.md`.
- Avoid creating generic or duplicate skills.
- Keep meta skills distinct from domain execution skills.
- Preserve safety boundaries for high-impact workflows.
- Use the user's language unless the user asks otherwise.

## Final rule

A skill system should behave like this:

```text
discover → route → execute → distill → index → audit → refine
```

If a file does not help routing, judgment, workflow, validation, or reuse, it should not become a skill.