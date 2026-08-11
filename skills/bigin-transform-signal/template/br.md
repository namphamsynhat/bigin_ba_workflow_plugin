---
id: BR-
type: business-rule
title:
status: draft   # raw | draft | in-review | needs-clarification | approved | superseded | removed
                # (references/conventions.md § Frontmatter schema) — same discipline as an FR;
                # this skill only ever writes draft/in-review/needs-clarification.
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
human gate (SKILL.md Pass 1 raises it / Pass 2 folds it in) confirms it. Same format as
template/fr.md's ## Discussion. -->

## Open Questions
<!-- Same format and invariant as an FR's Open Questions (conventions.md § Open Questions
wording, § Open Questions ↔ status consistency). -->

## Changelog
- 1.0 (YYYY-MM-DD) — created from <INT-###>
