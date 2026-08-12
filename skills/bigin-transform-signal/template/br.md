---
id: BR-
type: business-rule
title:
status: draft   # draft | needs-clarification | enriched | approved | consolidated | removed
                # (references/conventions.md § Status vocabularies — in-review and superseded are
                # retired for FR/BR) — same discipline as an FR; /bigin-transform-signal only ever
                # writes draft/needs-clarification.
version: 1.0
feature:         # the FEATURES.md slug this BR belongs to
fr: []           # FR-### id(s) this rule constrains — [] if it's a feature-level rule not yet
                 # tied to one FR (conventions.md § Signal → artifact mapping)
sources: []      # INT-### id(s) this BR traces to
links: []
owner: team
updated:
---

# BR-<NNN> <Title>

<the rule itself, stated as a testable constraint — "If <condition>, then <system must/must
not>..." Not a restatement of the FR it constrains; a rule narrows or governs how the FR behaves.>

## Discussion
<!-- Staged, not-yet-applied change proposals, cleared into the rule statement above once the
human gate (SKILL.md Stage 3 raises it / Stage 1 folds it in) confirms it. Same format as
template/fr.md's ## Discussion. -->

## Open Questions
<!-- Same format and invariant as an FR's Open Questions (conventions.md § Open Questions
wording, § Open Questions ↔ status consistency). -->

## Changelog
- 1.0 (YYYY-MM-DD) — created from <INT-###>
