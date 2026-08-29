---
type: scenario-register
status_of_template: retired
updated:
---

# Business Scenario Register (retired)

<!-- RETIRED TEMPLATE — do not instantiate, never add a row. Kept only so that a SCENARIOS.md written
before the UC migration still parses and its SCN-### ids still resolve. Existing rows stay in place with
Status: superseded and Notes naming the UC that absorbed them.
See `registers.md` § Business Scenarios (retired). -->

One row per cross-feature business scenario — a flow whose steps span more than one feature. Replaced
by `UC-###`: a use case spanning features records the same flow with its actors, alternative and
exception paths, governing rules, and open questions, and it passes the human review gate that this
register never did.

`Notes` on a superseded row names the UC that absorbed it (`absorbed by UC-012`), and that UC lists the
`SCN-###` in its own `absorbs:` frontmatter.

| SCN-### | Name | Steps (feature: what happens) | Status | Notes |
|---------|------|-------------------------------|--------|-------|

## Changelog
- (YYYY-MM-DD) — register created
