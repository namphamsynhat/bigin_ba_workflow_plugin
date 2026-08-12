# Bigin BA Workflow Plugin

A Claude Code plugin that guides a Business Analyst through turning raw communication (meetings, emails, chat notes) into structured requirement documentation — from first capture to Epics and User Stories.

## Workflow

Structured as ETL: `extract-signal` **extracts** raw intake into per-feature signals,
`bigin-transform-signal` **transforms** those signals into FRs and BRs (each its own file, with
Entities/Business Scenarios kept in sync across features), and the remaining stages **load**
approved requirements into the PRD, prototype, and epics. See `references/conventions.md` for the
full ID scheme and artifact conventions.

```
/bigin-new-project        initiate the project in this repo: scaffold the workspace, capture the
                           engagement config, map the codebase if it's an existing product
        |
/bigin-intake             capture raw intake, unmodified (auto: email/meeting, or direct: freeform note)
        |
/extract-signal           [Extract] drain the intake queue: extract signals, anchor each to a
                           feature, file it onto that feature's Signal Log
        |
/bigin-transform-signal   [Transform] qualify each filed signal, route it to a lane, turn it into
                           drafted/updated FRs and BRs, keep cross-feature Entities and Business
                           Scenarios in sync, human-gate every FR/BR change before it's folded in
        |
        |------------------------------------------.
        |                                          |
/enrich-feature           [Load] domain research    |  presentation-only signals take the Design
        |                  + entity mapping         |  chain — a directive on the feature hub or
        |                                           |  in DESIGN-PRINCIPLES.md, no FR, no PRD
/approve-fr               [Load] approve the FRs,   |
        |                  generate/update the PRD  |
        |                                           |
/prototype-design         [Load] produce a text-level prototype design (flows, screens, states)
        |
/consolidate-prd          [Load] merge design decisions into the PRD, generate Epics & User Stories
```

`/bigin-transform-signal` runs five stages per invocation: **fold-in** (apply staged changes a human
has since answered — first, so a rerun is always useful), **qualify** (four gates: blocked on an
answer, source materialized, fidelity, dedup), **route and draft** (one subagent per feature, never
per lane — a feature's hub and FR/BR files are one ownership domain), **sync** (shared registers,
written sequentially, plus an in-feature conflict check), and **status and report**. Signals it
can't safely act on are parked `held` with the remedy named, never repaired by re-reading raw
material — extraction owns that, and its own fidelity pass is where a signal is checked
quote-by-quote against the source it claims to come from.

All state is written into the current repo — `_bigin/` for engagement config, `00-Inbox`/`01-Requirements` for the requirements vault:

```
_bigin/system/project.md         engagement config: client, approver, contacts,
                                  new vs. ongoing product, codebase map
00-Inbox/
└── INT-<NNN>.md                 raw captures, one file per intake, verbatim
01-Requirements/
├── FEATURES.md                  the feature slug registry — everything anchors to a row here
├── PAIN-POINTS.md               canonical PP-### register
├── ENTITIES.md                  candidate EN-### rows a signal reveals (proposed only)
├── DESIGN-PRINCIPLES.md         durable, cross-cutting design constraints
├── SCENARIOS.md                  single SCN-### register — one row per cross-feature flow
├── _features/<slug>.md          one Feature Hub per slug — Signal Log, Entities, Business
│                                 Scenarios, Requirement Readiness, Pain Points
├── _frs/FR-<NNN> <Title>.md      one Functional Requirement doc per FR
├── _brs/BR-<NNN> <Title>.md      one Business Rule doc per BR — always its own file, fr: []
│                                 citing the FR(s) it constrains (or [] if feature-level)
└── _entities/EN-<NNN> <Title>.md one entity doc per promoted EN-### (domain-modeled, not just
                                  proposed) — a field-level BR is still its own _brs/ file
PRD.md                            consolidated PRD, one section per approved feature
prototypes/FR-<NNN>-prototype.md flows/screens for an approved feature
epics.md                          generated Epics & User Stories
```

`/bigin-new-project` runs once per repo and is re-runnable: it shows the existing config and only rewrites what you confirm, never touching captured intake, features, or the PRD. For `project_mode: ongoing` it also records a **codebase map** — stack, entry points, and code-area slugs — so later stages can anchor requirements to real directories. Code areas name places in the code, not features; feature names still come from client signals via `/extract-signal`.

Every FR's own frontmatter `status` (`draft` → `in-review` ⇄ `needs-clarification` → `approved`, human-only per `/approve-fr`) is the authoritative gate — a feature can have more than one FR at different stages at once, though normally a feature carries just one FR across its life (an update edits it in place rather than forking). Each Feature Hub's `## Requirement Readiness` table is a refreshed snapshot for orientation, not the gate itself. Features are matched by slug across stages, so `/extract-signal` and `/bigin-transform-signal` update an existing hub/FR rather than duplicating one when new signals map to the same feature.

> **Migration note:** `/enrich-feature`, `/approve-fr`, `/prototype-design`, and `/consolidate-prd` still read the older `.bigin/features/FR-<id>-*.md` single-file model. They haven't been moved onto the `01-Requirements/` layout yet — that's the next stage of this migration, not yet done. See `references/conventions.md` § Reconciliation notes for the full list of gaps.

## Configuration

`/extract-signal` and `/bigin-intake` read `.claude/bigin-ba-workflow-plugin.local.md` if present — a plugin settings file (not project data, so it belongs in `.claude/`, not `_bigin/`) for project-specific overrides such as a house style for `Why` phrasing or a standing list of features that always map to one obvious slug without raising a question. It's optional; omit it to use the built-in defaults. Add `.claude/*.local.md` to the project's `.gitignore` since it's user/local config.

## Install (local development)

```bash
claude --plugin-dir /path/to/bigin_ba_workflow_plugin
```

Then run `/bigin-new-project` to initiate the project, and `/bigin-intake` to capture the first input. Use `/reload-plugins` after editing any `SKILL.md` to pick up changes without restarting.

## Install (from a marketplace)

Once published to a marketplace:

```
/plugin install bigin-ba-workflow-plugin@<marketplace-name>
```
