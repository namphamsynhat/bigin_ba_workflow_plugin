# Role cards

What an agent actually reads (restructure plan Phase 4): **one card, ≤ 3 KB**, instead of whole
convention files. Each card = inputs · output (a schema in `lib/bigin/schema/`) · the 5–10 rules
that role can actually break · one worked example · the model tier and why.

Conventions in `workspace/conventions/` stay the human reference and the source cards are derived
from. Every rule on a card cites its source as `‹file § heading›` — `file` resolves under
`workspace/conventions/`, or under `workspace/` for a stage file (`‹stages/transform/3-lane-uc.md §
Writing a step›`). `tests/test_phase4_lean.py::test_card_citations_resolve` fails when a cited heading
no longer exists, so a card cannot drift from its convention silently.

A project override in `.claude/bigin-ba-workflow-plugin.local.md` still wins over a card; the
orchestrating skill passes any relevant override text inside the task input, never the whole file.

| Card | Agent | Output schema |
|---|---|---|
| `router.md` | uc-router | `route` (Phase A), `changesets` (Phase B) |
| `adjudicator.md` | code-adjudicator | `adjudication` |
| `extractor.md` | signal-extractor | `signals` |
| `auditor.md` | signal-auditor | `audit` |
| `filer.md` | signal-filer | `filing` |
| `splitter.md` | uc-splitter | `changesets` |
| `design-screens.md` | bigin-generate-design screens worker | (writes the UX spec — design stage) |
| `prd-writer.md` | bigin-generate-prd writer | (writes the PRD — PRD stage) |
| `ba-review.md`, `ba-triage.md` | bigin-ba (interactive) | loaded on demand |
