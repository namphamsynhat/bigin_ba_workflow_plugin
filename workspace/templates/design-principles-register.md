---
type: design-principles
version: 1.0
updated:
---

# Design Principles

Durable, cross-cutting design/brand/tone/accessibility/interaction/content preferences — the kind of constraint that outlives any one feature. `extract-signal` appends a row here when a signal reads as this durable, **in addition to** filing it normally on its anchored feature's Signal Log — never instead of that filing. A preference scoped to a single feature goes to that feature hub's `## Design Directives` section instead (`registers.md` § Design Principles Register); a signal stated about one feature that clearly generalizes lands in both.

Append-only: `#` is permanent, never renumbered or deleted. A later statement that contradicts an earlier one is a **new** row, with the old row's `Status` set to `superseded` (or `rejected` if it was explicitly walked back) and `Notes` pointing at the row that replaced it. `Status` is `active | superseded | rejected | conflict`. Every write bumps `version` and appends a `## Changelog` line.

`/bigin-generate-design` reads this file directly, not only via the PRD — so a feature that reaches prototyping before its PRD is finished still produces a prototype consistent with what the client has said.

| # | Principle | Why | Category | Source | Status | Notes |
|---|-----------|-----|----------|--------|--------|-------|

## Changelog
- 1.0 (YYYY-MM-DD) — register created
