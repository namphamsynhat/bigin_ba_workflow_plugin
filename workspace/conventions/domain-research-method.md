# Domain research — shared dispatch mechanics

Read by both the project-level research step (`skills/bigin-new-project/references/domain-research.md`
§ 5.3) and the feature-level research step (`_bigin/stages/extract/3-filing.md` § Step 2a, and
`/enrich-feature`'s manual refresh). This file owns only *how a research pass runs* — what it's
scoped to, and where its output lands, are each caller's own job (see their own "Writing the
findings" section).

A caller invokes this with two things already in hand:

- **scope** — a one-line statement of what's being researched: "the whole project" (project-level) or
  "the `<feature-name>` feature" (feature-level).
- **input text** — what's actually known so far: a proposal excerpt / project brief (project-level),
  or a feature name + its one-line scope (feature-level).

## Choosing how this runs

Check `.claude/bigin-ba-workflow-plugin.local.md` § Domain research method before doing anything
else (template: `skills/bigin-new-project/template/settings.local.md`).

| Configured as | What to do |
|---|---|
| `skill: <skill-name>` | Dispatch that skill via the `Skill` tool, passing it the input text and the scope as `args`. Treat its return value as the research and skip to the caller's "Writing the findings" step — no further back-and-forth with the user. |
| `agent: <subagent-type>` | Dispatch one `Agent` call with that `subagent_type` (prompt shape in § Delegating to an agent below). Treat its final report as the research and skip to the caller's "Writing the findings" step. |
| `built-in`, or the section is absent/blank | Run § Built-in method below. |

**Default resolution, absent an explicit setting:** `skill: bmad-domain-research` if that skill is
installed in this project (`bmad-code-org/bmad-method`'s domain-research skill —
`skills/bigin-new-project/SKILL.md` § 2.5 installs it at project init unless opted out), else
§ Built-in method. A skill dispatch that fails outright, times out, or returns nothing usable falls
back to § Built-in method for this run rather than blocking the caller — same "providers never
block" pattern `bigin-new-project` § 7 already uses for a missing MCP server. Never retry the failed
skill more than once in the same run.

This table is the extension point. Two ways to change what runs here, and they're different edits:

- **Point at an existing skill or agent instead** — add or edit the `## Domain research method`
  section in `.claude/bigin-ba-workflow-plugin.local.md`. Per-project setting, applies to both the
  project-level and feature-level call sites, since they share this file.
- **Change the built-in method itself** — edit § Built-in method below. The plugin's own shipped
  default, not project data — this changes it for every project that falls back to `built-in`.

## Built-in method

Use `WebSearch` (and `WebFetch` for a specific promising result) against the input text. Research, in
this order, stopping once a question has a clear answer rather than exhausting every source:

1. **Industry/domain context** — what field this operates in, and what "normal" looks like there.
2. **Comparable products** — 2–4 existing products doing something similar; how they approach the
   same problem, and any documented shortcomings or user complaints.
3. **Compliance/regulatory concerns** — anything the domain itself imposes (data residency, financial
   regulation, healthcare privacy, accessibility law) independent of what the client has mentioned.
4. **Common failure modes** — mistakes or edge cases similar products/features are known to have hit,
   especially ones a first-time build in this domain would miss.
5. **Entities and integrations typically involved** — the actors, data objects, and third-party
   systems something like this usually has to model, as a heads-up for later entity work, not as a
   substitute for it.

Keep findings specific to *this* scope's stated content, not generic advice restating it back. A
finding earns its place by being something nobody already said.

## Delegating to an agent

When `.claude/bigin-ba-workflow-plugin.local.md` names an `agent: <subagent-type>`, dispatch one
foreground `Agent` call:

```text
Research the domain for <scope> before building against it. Cover industry context, comparable
products and their known shortcomings, compliance/regulatory concerns, common failure modes, and the
entities/integrations something like this typically involves. Be specific to what's described below,
not generic advice.

Scope: <scope>
What's known: <the input text, verbatim>

Report findings grouped by the five topics above, each with a one-line "why it matters here."
```

Its final response is the research — treat it the same as the built-in method's output.
