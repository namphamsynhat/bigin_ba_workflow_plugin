---
id: FR-
type: requirement
status_of_template: retired
absorbed_by:    # UC-### that took this FR's content over, once one has
title:
status: draft   # draft | needs-clarification | enriched | approved | consolidated | removed
                # (_bigin/conventions/conventions.md § Status vocabularies — in-review and superseded are
                # retired for FR/BR). /bigin-transform-signal only ever writes
                # draft/needs-clarification; enriched is permanently unreachable (enrichment is
                # feature-scoped now, never FR/UC-level), consolidated to /consolidate-prd, and
                # approved/removed are human-only (hard rule 4).
version: 1.0
feature:         # the FEATURES.md slug this FR belongs to
sources: []      # INT-### id(s) this FR traces to
links: []        # downstream PRD-###/EP-###/US-###/UX-### ids, once they exist
attachments: []  # vault-relative paths, copied over from every sources: INT note's own attachments
amends:          # another FR-### id this one splits off from — rare, human-confirmed only
owner: team
updated:
---

# `FR-<NNN> <Title>`

<!-- RETIRED TEMPLATE — do not instantiate. FR-### was replaced by UC-### (_bigin/templates/use-case.md):
a use case carries the same testable content as positioned flow steps, plus the actors, branches, rules
mirror, and open questions that made a bare requirement list unreviewable. This file is kept only so
that an FR written before the migration still parses and its id still resolves.

An FR a use case has taken over carries `absorbed_by: UC-###` and is frozen: never edited, never set
`removed` (human-gated, hard rule 4). See _bigin/stages/transform/3-lane-uc.md § Adopting an existing
FR. -->

> [!summary]- Summary (retired — nothing writes this)
> `<enrichment is feature-scoped now and never touches an FR; leave blank.>`

## Business goal
<!-- Why this is being built, in the client's own terms — drawn from the signal(s) that created
this FR, not invented. -->

## Problem & Pain Points
<!-- Mirror of this FR's rows from 01-Requirements/PAIN-POINTS.md (conventions.md § Pain Point
Register): PP-### | Statement | Status | Proposed solution | Resolved by. Empty until a
[pain-point] signal anchors here. -->

| PP-### | Statement | Status | Proposed solution | Resolved by |
|--------|-----------|--------|--------------------|--------------|

## Functional requirements
<!-- Numbered FR-<NNN>.1, FR-<NNN>.2, ... one testable, actionable statement per line
(conventions.md § Signal → artifact mapping). Never written straight here — draft into
## Discussion first, fold in only after the human gate (§ SKILL.md Stage 3 stages it, Stage 1
folds it in on a later run). A
policy/conditional constraint on this FR is its own BR-### file (01-Requirements/_brs/), not a
line here — see _bigin/templates/br.md. -->

## Discussion
<!-- Staged, not-yet-applied change proposals, one per pending signal, cleared into
## Functional requirements above only once the human gate (SKILL.md Stage 3 raises it / Stage 1
folds it in) confirms it. Format:

- **<INT-###>** (staged <YYYY-MM-DD>): <quoted/tightly paraphrased signal> → proposed: <the FR
  line this becomes>

Never fold an entry into Functional requirements without the gate having resolved it first. -->

## Open Questions
<!-- Same format and invariant as an intake note's Open Questions (conventions.md § Open
Questions wording, § Open Questions ↔ status consistency): zero unchecked boxes here ⟺ status is
not needs-clarification.

- [ ] Q: ... (owner: client|team) (ref: <INT-###>)
      A: -->

## Changelog
- 1.0 (YYYY-MM-DD) — created from `<INT-###>`
