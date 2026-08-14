# Domain research — built-in method, and how to swap it

Runs only from `/bigin-new-project` § 5.3: `project_mode: new`, and only once a proposal (§ 5.1) or a
project brief (§ 5.2) is on record to research from. Its job is to turn "what this product does" into
domain grounding — known edge cases, industry-standard approaches, compliance/regulatory concerns, and
comparable products' failure modes — before the first client signal arrives, so later stages inherit
context instead of each rediscovering it cold.

**This is not** `/enrich-feature`'s per-feature `## Domain Research` (`_bigin/conventions/
conventions.md` § Feature Hub, marked Planned there). That one runs later, repeats per feature, is
scoped to a single use case's requirements, and is planned to live under `01-Requirements/_research/<slug>/`.
This one runs once, project-wide, before any feature exists to scope it to. Don't conflate the two, and
don't have this step write into a feature hub — there isn't one yet.

## Choosing how this runs

Check `.claude/bigin-ba-workflow-plugin.local.md` § Domain research method before doing anything else
(template: `skills/bigin-new-project/template/settings.local.md`). Absent file, absent section, or
`built-in` all mean the same thing: run § Built-in method below.

| Configured as | What to do |
|---|---|
| absent, or `built-in` | Run § Built-in method below. |
| `skill: <skill-name>` | Dispatch that skill via the `Skill` tool, passing it the proposal text or project brief and the client name as `args`. Treat its return value as the research and skip to § Writing the findings — no further back-and-forth with the user. |
| `agent: <subagent-type>` | Dispatch one `Agent` call with that `subagent_type` (prompt shape in § Delegating to an agent below). Treat its final report as the research and skip to § Writing the findings. |

This table is the extension point. Two ways to change what runs here, and they're different edits:

- **Point at an existing skill or agent instead** (e.g. one already installed for market/competitive
  research, or one better at a regulated domain than a generic web search) — add or edit the
  `## Domain research method` section in `.claude/bigin-ba-workflow-plugin.local.md`. That's a
  per-project setting, not a plugin change.
- **Change the built-in method itself** — edit § Built-in method in this file directly. It's the
  plugin's own shipped default, not project data, so this changes it for every project that falls back
  to `built-in`.

Either edit leaves everything else in this skill untouched: SKILL.md § 5.3 only ever says "read this
file," never which method to run.

## Built-in method

Use `WebSearch` (and `WebFetch` for a specific promising result) against the proposal text or project
brief. Research, in this order, stopping once a question has a clear answer rather than exhausting every
source:

1. **Industry/domain context** — what field this product operates in, and what "normal" looks like there.
2. **Comparable products** — 2–4 existing products doing something similar; how they approach the same
   problem, and any documented shortcomings or user complaints.
3. **Compliance/regulatory concerns** — anything the domain itself imposes (data residency, financial
   regulation, healthcare privacy, accessibility law) independent of what the client has mentioned.
4. **Common failure modes** — mistakes or edge cases similar products are known to have hit, especially
   ones a first-time build in this domain would miss.
5. **Entities and integrations typically involved** — the actors, data objects, and third-party systems a
   product like this usually has to model, as a heads-up for later `## Entity Map` work, not as a
   substitute for it.

Keep findings specific to *this* project's stated scope, not generic advice restating the brief back.
A finding earns its place by being something the client didn't already say.

## Delegating to an agent

When `.claude/bigin-ba-workflow-plugin.local.md` names an `agent: <subagent-type>`, dispatch one
foreground `Agent` call:

```text
Research the domain for a new project before any requirements exist for it. This grounds the
engagement, not one feature — cover industry context, comparable products and their known
shortcomings, compliance/regulatory concerns, common failure modes, and the entities/integrations
products like this typically involve. Be specific to what's described below, not generic advice.

Client: <client name>
What's being built: <the proposal excerpt or project brief, verbatim>

Report findings grouped by the five topics above, each with a one-line "why it matters here."
```

Its final response is the research — treat it the same as the built-in method's output.

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
