---
id: BR-
type: business-rule
title:
status: draft   # draft | needs-clarification | enriched | approved | consolidated | removed
                # (_bigin/conventions/conventions.md § Status vocabularies — in-review and superseded are
                # retired for FR/BR) — same discipline as an FR; /bigin-transform-signal only ever
                # writes draft/needs-clarification.
version: 1.0
feature:         # the FEATURES.md slug this BR belongs to
uc: []           # UC-### id(s) this rule governs — [] if it's a feature-level rule not yet tied to
                 # one workflow (conventions.md § Signal → artifact mapping). This file is the SOURCE
                 # of the rule; each listed UC's § 4 is a read-only mirror of it (BABOK § 10.47 —
                 # rules are captured separately so a rule change doesn't force a use-case change).
fr: []           # RETIRED. Pre-UC FR-### id(s) this rule constrained, kept as traceability so old
                 # ids still resolve. Nothing writes here any more.
sources: []      # INT-### id(s) this BR traces to
links: []
owner: team
updated:
---

# `BR-<NNN> <Title>`

`<the rule itself, stated as a testable constraint: "If CONDITION, then the system must / must not ...">`

Not a restatement of the step it constrains — a rule narrows or governs how the workflow behaves.
A rule about an entity field also names it: "Governs EN-004 Vendor → tax_code."

## Discussion
<!-- Staged, not-yet-applied change proposals, cleared into the rule statement above once the
human gate (SKILL.md Stage 3 raises it / Stage 1 folds it in) confirms it. Same format as
_bigin/templates/use-case.md's ## Discussion. -->

## Open Questions
<!-- Same format and invariant as a use case's § 5 Still open list (conventions.md § Open Questions
wording, § Open Questions ↔ status consistency). -->

## Changelog
- 1.0 (YYYY-MM-DD) — created from `<INT-###>`
