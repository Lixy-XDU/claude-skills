---
name: skill-distiller
description: Convert practical work experience, project notes, debugging records, implementation lessons, plans, reviews, or repeated workflows into a focused Claude Code SKILL.md. Use when the user wants to create, refactor, or evaluate a skill from real work experience. This skill produces the skill content and a compact index handoff, but does not manage the full skill library.
argument-hint: "[experience-notes-or-skill-topic]"
disable-model-invocation: true
---

# Skill Distiller

Use this skill to turn raw work experience into a focused, reusable Claude Code `SKILL.md`.

This skill's job is narrow:

```text
experience → reusable judgment → focused SKILL.md → compact index handoff
```

It does not manage the full skill ecosystem. Skill routing, taxonomy, index maintenance, and conflict governance belong to `/skills-index`. Local inspection belongs to `/find-local-skills`. External skill discovery belongs to `/find-skills`.

## Core responsibility

This skill should produce high-quality `SKILL.md` files from messy practical experience.

A good skill is not a diary, not a project report, not a generic tutorial, and not a memory dump.

A good skill encodes:

- When Claude should use it
- When Claude should not use it
- What Claude should do differently because of the experience
- What rules must be followed
- What mistakes must be avoided
- What workflow should be executed
- What checks must be applied
- What output should be produced

## Use when

Use this skill when the user asks to:

- Turn work experience into a `SKILL.md`
- Convert debugging notes into a reusable debugging workflow
- Convert project lessons into repeatable Claude Code behavior
- Convert an implementation pattern into a coding skill
- Convert a review checklist into a review skill
- Convert a migration, release, testing, or planning workflow into a skill
- Refactor an existing `SKILL.md`
- Evaluate whether something deserves to become a skill
- Extract reusable rules from a project, bug, plan, or failed attempt
- Remove noise from a draft skill
- Improve a skill's trigger, structure, rules, checks, or output format

## Do not use when

Do not create a skill when the input is only:

- A one-off fact
- A temporary reminder
- A generic preference
- A single command with no reusable judgment
- A project-specific note better suited for `CLAUDE.md`
- A long reference document that should remain documentation
- A broad policy that should apply to every Claude Code session
- A task already covered by a narrow, high-quality existing skill

When a skill should not be created, recommend the better destination:

- `CLAUDE.md`
- project documentation
- an existing skill
- `/find-local-skills`
- `/find-skills`
- `/skills-index`

## Relationship to companion skills

Use this responsibility split:

| Skill | Responsibility |
|---|---|
| `/skill-distiller` | Produce or refactor individual `SKILL.md` files from experience |
| `/skills-index` | Route, categorize, coordinate, and maintain the skill system |
| `/find-local-skills` | Inspect installed local skills and detect duplicates or overlap |
| `/find-skills` | Search external/community skills when local coverage is insufficient |

This skill may produce a compact index handoff, but it should not generate or maintain the full skill index unless the user explicitly asks.

## Skill creation decision rule

Create or refactor a skill only if at least two of these are true:

- The workflow will be repeated.
- The task has non-obvious constraints.
- The task has known failure modes.
- The user wants Claude to behave consistently.
- The experience contains reusable judgment.
- The task benefits from a checklist.
- The task has a preferred output structure.
- The task is easy to do wrong without domain memory.
- The task will recur across projects or sessions.
- The cost of forgetting the lesson is high.

If fewer than two are true, do not force the content into a skill.

## Input types

The user may provide:

- Raw notes
- Debugging records
- Project summaries
- Failed implementation attempts
- Successful implementation patterns
- Migration notes
- Release notes
- Code review lessons
- Testing workflows
- Deployment checklists
- Conversation transcripts
- Existing `SKILL.md` drafts
- A vague request like “make this into a skill”

If the input is messy, infer structure. Do not require perfect formatting.

## Distillation workflow

When converting experience into a skill:

1. Identify the reusable task type.
2. Identify the domain.
3. Identify when Claude should use the skill.
4. Identify when Claude should not use the skill.
5. Decide whether this should become a skill at all.
6. Separate reusable rules from project-specific facts.
7. Extract hard constraints.
8. Extract preferred patterns.
9. Extract anti-patterns.
10. Extract known failure modes.
11. Extract validation checks.
12. Extract troubleshooting mappings when relevant.
13. Define output expectations.
14. Choose a clear skill name.
15. Produce the final `SKILL.md`.
16. Produce a compact index handoff for `/skills-index`.

## What to preserve

Preserve information that changes future behavior:

- Technical constraints
- Environment constraints
- Version-specific behavior
- Required construction order
- Safe defaults
- Design patterns
- Debugging heuristics
- Review heuristics
- Edge cases
- Known bugs
- Failure symptoms
- Root causes
- Fix patterns
- Validation checks
- Output formats
- Templates
- Commands
- Decision rules
- Safety boundaries
- Tool permission cautions

## What to remove

Remove or compress information that does not belong in a reusable skill:

- Chronological storytelling
- Personal commentary
- Emotional descriptions
- Redundant background
- One-off implementation details
- Long logs
- Full transcripts
- Project names unless essential
- File names unless they define the workflow
- Screenshots descriptions unless they encode reusable rules
- Details that apply only to one repository
- Generic best practices without operational value

## Generalization rules

Convert specific experience into reusable operational rules.

Bad:

> In `modulation_ui.m`, the window kept moving upward.

Good:

> Never assign `fig.Position` inside `SizeChangedFcn`; it can create a resize feedback loop and cause window drift.

Bad:

> I fixed the bug by changing this one line.

Good:

> For this class of bug, first check whether the callback mutates state that retriggers the callback.

Bad:

> This worked in my project.

Good:

> Use this pattern when the GUI uses traditional MATLAB `figure` and `uicontrol` with normalized layout.

Bad:

> I should remember this next time.

Good:

> Add this to the validation checklist so Claude checks it before generating code.

## Naming rules

Choose names that are:

- Short
- Lowercase
- Hyphenated
- Task-oriented
- Specific enough to route reliably
- Not project-specific unless intentionally project-level

Good names:

```text
plan-review
codebase-recon
skill-distiller
find-local-skills
skills-index
matlab-traditional-gui
migration-risk-audit
release-checklist
test-strategy-review
bug-pattern-extractor
```

Bad names:

```text
my-skill
project-notes
general-helper
things-i-learned
claude-helper
work-summary
useful-stuff
```

Avoid nested category directories under `skills/`.

Use this structure:

```bash
~/.claude/skills/<skill-name>/SKILL.md
```

or for project-specific skills:

```bash
<project>/.claude/skills/<skill-name>/SKILL.md
```

## Description rules

The `description` is the most important routing field.

It should include:

- The task type
- The domain
- The trigger condition
- The expected value

Good:

```yaml
description: Review database migration plans for sequencing, rollback safety, data compatibility, observability, and production failure risks. Use when evaluating schema changes, data backfills, or migration rollout plans.
```

Bad:

```yaml
description: Helps with database stuff.
```

Avoid vague words:

```text
help
assist
general
useful
things
project
notes
stuff
```

Prefer concrete verbs:

```text
review
generate
audit
debug
refactor
extract
validate
compare
plan
triage
distill
```

## Frontmatter rules

Use valid YAML frontmatter.

Default template:

```yaml
---
name: skill-name
description: Clear description of when to use this skill and what task it helps with.
argument-hint: "[input-file-or-topic]"
disable-model-invocation: true
---
```

Use `disable-model-invocation: true` by default for:

- Meta skills
- Review workflows
- Release workflows
- Deployment workflows
- Migration workflows
- Shell workflows
- File deletion workflows
- Permission-sensitive workflows
- Any high-impact operation

Do not add `allowed-tools` unless the user explicitly requests tool pre-authorization.

If `allowed-tools` is requested, keep it narrow and explain the risk.

## Standard SKILL.md structure

Use this structure by default:

```markdown
---
name: skill-name
description: Clear description of when to use this skill and what task it helps with.
argument-hint: "[input-file-or-topic]"
disable-model-invocation: true
---

# Skill Title

Briefly define what this skill does.

## Use when

- Scenario 1
- Scenario 2
- Scenario 3

## Do not use when

- Exclusion 1
- Exclusion 2

## Core rules

- Rule 1
- Rule 2
- Rule 3

## Workflow

1. Step 1
2. Step 2
3. Step 3

## Patterns

Describe recommended implementation or reasoning patterns.

## Anti-patterns

Describe mistakes to avoid.

## Validation checklist

- Check 1
- Check 2
- Check 3

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Symptom | Cause | Fix |

## Output expectations

Describe what Claude should produce when this skill is used.
```

For small skills, sections may be shorter, but the skill must still contain concrete rules and output expectations.

## Personal vs project-level placement

Recommend personal-level placement when:

- The skill applies across projects.
- It captures reusable engineering judgment.
- It is a general workflow.
- It is not tied to a repository-specific command or architecture.

Path:

```bash
~/.claude/skills/<skill-name>/SKILL.md
```

Recommend project-level placement when:

- The skill depends on project architecture.
- The skill uses project-specific commands.
- The skill describes team conventions.
- The skill references internal APIs, paths, or deployment details.
- The skill should not affect other projects.

Path:

```bash
<project>/.claude/skills/<skill-name>/SKILL.md
```

If uncertain:

- Put reusable judgment in a personal skill.
- Put repository facts in `CLAUDE.md` or a project-level skill.
- Put temporary notes in documentation.

## Compact index handoff

When creating or refactoring a skill, produce a compact handoff for `/skills-index`.

Do not maintain the full index here.

Use this format:

```markdown
## Index handoff

Recommended category: <category-or-ask-/skills-index>
Recommended scope: personal/project
Recommended path: ~/.claude/skills/<skill-name>/SKILL.md

Index entry:

| `skill-name` | personal/project | One-sentence purpose | `/skill-name` |
```

If category is uncertain, say:

```markdown
Recommended category: ask `/skills-index`
```

If overlap is likely, say:

```markdown
Potential overlap: run `/find-local-skills <topic>` before installing.
```

## Duplicate and overlap caution

Before finalizing a new skill, consider whether it overlaps with existing likely skills.

If overlap is possible, include:

```markdown
Potential overlap:
- `/existing-skill-name` may cover a similar workflow.
- Run `/find-local-skills <topic>` before installing.
```

Do not invent exact local skill contents unless provided by the user.

If the user gives an actual local skill list, use it.

## Skill quality checklist

Before finalizing a skill, verify:

- The purpose is narrow and clear.
- The name is lowercase and hyphenated.
- The `description` is specific enough for routing.
- The skill is not just a summary.
- The skill contains concrete rules.
- The skill includes anti-patterns.
- The skill includes a workflow.
- The skill includes validation checks.
- The skill includes output expectations.
- Troubleshooting exists when failure modes are known.
- Project-specific content is not placed in a global skill.
- Dangerous tool permissions are absent unless explicitly requested.
- High-impact workflows use `disable-model-invocation: true`.
- The skill can be used without reading the original notes.
- A compact index handoff is provided unless the user asks for raw skill text only.

## Refactoring existing skills

When refactoring an existing `SKILL.md`, audit:

1. YAML validity.
2. Name clarity.
3. Description specificity.
4. Trigger scope.
5. Project-specific leakage.
6. Missing sections.
7. Operational usefulness of rules.
8. Reusability of examples.
9. Presence of anti-patterns.
10. Presence of validation checks.
11. Output expectations.
12. Unnecessary or unsafe `allowed-tools`.
13. Whether an index handoff should be updated.

Return:

```markdown
## Verdict

Ready / Needs revision / Should merge / Should not be a skill

## Main issues

- Issue 1
- Issue 2

## Revised SKILL.md

```markdown
...
```

## Index handoff

Recommended category: <category-or-ask-/skills-index>
Recommended scope: personal/project
Recommended path: <path>

Index entry:

| `skill-name` | personal/project | One-sentence purpose | `/skill-name` |
```

## Merging guidance

When two skill drafts overlap:

1. Keep the clearer name.
2. Keep the narrower trigger.
3. Preserve the best rules and checks.
4. Remove duplicated explanation.
5. Move project-specific details out of global skills.
6. Produce one clean `SKILL.md`.
7. Provide a compact index handoff.
8. Recommend `/skills-index` for the final merge decision if needed.

Merge report format:

```markdown
## Merge recommendation

Keep: `/skill-a`
Merge from: `/skill-b`

Reason:
- Reason 1
- Reason 2

Result:
- Produce one revised `SKILL.md`
- Ask `/skills-index` to update the index
```

## Auxiliary files

A skill may use auxiliary files when the material is too long for `SKILL.md`.

Use auxiliary files for:

- Long templates
- Extended examples
- Reference checklists
- Domain-specific conventions
- Large command libraries
- Long troubleshooting tables

Recommended structure:

```bash
<skill-name>/
  SKILL.md
  templates/
    output-template.md
  examples/
    good-example.md
    bad-example.md
  checklists/
    review-checklist.md
```

In `SKILL.md`, explicitly say when Claude should read each auxiliary file.

Do not move essential trigger logic or core rules out of `SKILL.md`.

## Output modes

### When the user asks to create a skill

Return:

1. Proposed skill name
2. Recommended path
3. Final `SKILL.md`
4. Compact index handoff

If the user says "text only", output only the final `SKILL.md`.

### When the user asks to refactor a skill

Return:

1. Brief verdict
2. Key structural changes
3. Revised `SKILL.md`
4. Compact index handoff

If the user says "text only", output only the revised `SKILL.md`.

### When the user asks whether something should become a skill

Return:

```markdown
## Verdict

Create / Do not create / Merge into existing skill / Put in CLAUDE.md / Put in docs

## Reason

- Reason 1
- Reason 2

## Recommended destination

Path or file.
```

### When the user provides raw notes

Return:

1. Extraction summary
2. Proposed skill name
3. Recommended path
4. Final `SKILL.md`
5. Compact index handoff

### When the user asks for index or taxonomy decisions

Do not take over the full index. Return:

```markdown
Use `/skills-index` for taxonomy, routing, and full index maintenance.

Suggested handoff:

| `skill-name` | personal/project | One-sentence purpose | `/skill-name` |
```

## Final generation rules

When generating the final skill:

- Use valid YAML frontmatter.
- Keep frontmatter minimal.
- Use a concrete `description`.
- Prefer `disable-model-invocation: true` for high-impact or meta workflows.
- Do not add `allowed-tools` unless explicitly requested.
- Do not invent environment details.
- Preserve version-specific constraints when provided.
- Convert long experience into compact operational rules.
- Prefer workflows and checklists over prose.
- Remove chronological story unless it encodes a failure pattern.
- Make the skill usable without the original notes.
- Include output expectations.
- Include a compact index handoff unless the user requests raw text only.
- Avoid nested skill category directories.
- Keep the skill narrow enough to route reliably.

## Final rule

A skill should encode:

```text
trigger → judgment → workflow → checks → output
```

The index layer should encode:

```text
skill → category → routing → coordination
```

Do not mix those responsibilities unless the user explicitly asks.