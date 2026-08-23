# Domain research — project-level

Runs only from `/bigin-new-project` § 5.3: `project_mode: new`, and only once a proposal (§ 5.1) or a
project brief (§ 5.2) is on record to research from. Its job is to turn "what this product does" into
domain grounding — known edge cases, industry-standard approaches, compliance/regulatory concerns, and
comparable products' failure modes — before the first client signal arrives, so later stages inherit
context instead of each rediscovering it cold.

**This is not** the feature-level domain research that now runs automatically the moment a feature is
registered (`_bigin/stages/extract/3-filing.md` § Step 2a, refreshable on demand via
`/enrich-feature`). That one runs later, repeats per feature, is scoped to one feature's stated
purpose, and writes to `01-Requirements/_research/<slug>/`. This one runs once, project-wide, before
any feature exists to scope it to. Don't conflate the two, and don't have this step write into a
feature hub — there isn't one yet.

## How this runs

Read `_bigin/conventions/domain-research-method.md` for the dispatch mechanics (choosing a method,
the built-in WebSearch topics, delegating to a skill or agent) — this file only supplies what's
specific to the project-level case:

- **scope**: "the whole project"
- **input text**: the proposal excerpt or project brief, verbatim, plus the client name

Follow that file through, then come back here for § Writing the findings below.

## Writing the findings

Write the full report to `_bigin/system/domain-research.md` (new file — no template; it's freeform
prose, not a parsed schema):

```markdown
# Domain Research — <Client Name>

_<date> · /bigin-new-project § 5.3 · method: <built-in | skill:<name> | agent:<type>>_

## Input
<the proposal excerpt or project brief this ran against>

## Findings

### Industry/domain context
- <finding> — <why it matters for this project>

### Comparable products
- <product> — <approach, and any known shortcoming>

### Compliance/regulatory concerns
- <concern> — <what it implies for scope or design>

### Common failure modes
- <failure mode> — <how it'd show up here>

### Entities and integrations to expect
- <entity/integration> — <why it's likely relevant>

## Open questions this raises
- <something worth confirming with the client before it becomes an assumption baked into a use case>
```

Then append a dated pointer under `_bigin/system/project.md`'s `## Domain Research` section (add the
section if the project was initiated before this existed):

```markdown
## Domain Research
<!-- project_mode: new only — written by /bigin-new-project § 5.3, method-agnostic. -->
- 2026-08-14 — <one-line summary of the single most decision-relevant finding> → full report:
  `_bigin/system/domain-research.md`
```

The pointer is what a human skims; the file is what `/enrich-feature` or a later research pass actually
reads. Don't duplicate the full findings into `project.md` — same "pointer, not inline prose" rule the
Feature Hub's `Notes` cell already follows.
