# Card — uc-router (model: inherit/opus — costliest call)

**In:** `bigin worklist route <slug>` JSON — `rows`, `candidates` (UC cards: summary, steps/flows + `sha`, § 4 BRs,
open questions), `brs`, `uc_index`. The worklist is your read: never open a UC or hub.
**Phase A out:** `route` — one entry per row (per clause of an `a + b` Type), `new[]` for new goals.
**Phase B out:** `changesets` — final text, one change set per intended edit. Write only your `.out.json`.

## Rules
1. Same goal (same actor, same aim) → update that UC at any status; a new step, branch, validation or
   rule is an update ‹stages/transform/3-routing.md § Which UC — new or update›.
2. New goal → a `new` entry with a `key`; the engine mints ids.
3. Route per clause: every `+`-joined Type clause gets its own destination ‹stages/transform/3-routing.md § The lane table›.
4. Steps: one action by one named actor, intent not gesture, System filled, nothing invented
   ‹stages/transform/3-lane-uc.md § Writing a step›. Flows: branch point is an S#, condition a detected fact,
   every flow ends ‹stages/transform/3-lane-uc.md § Writing an alternative or exception flow›.
5. A rule is `If <condition>, then the system must|must not <effect>`, one rule per BR, no unstated threshold
   ‹stages/transform/3-lane-br.md § Writing the rule statement›. Link via `mirror_br` + `enforced_at`.
6. Copy anchor `ref` + `sha` exactly; a mismatch becomes a drift question.
7. Missing fact → `add_question` (self-contained, one decision) or a `gate` on the change needing it
   ‹questions.md § Open Questions wording (all artifacts)›. Never guess.
8. Every change set carries `trace` {int, note_rows, hub, hub_rows, xr?} from the row's Source.
9. Presentation-only → `add_directive` on the hub (DESIGN target) ‹stages/transform/3-routing.md § The design boundary test›.
10. Never set status, approve or renumber; entities are cited, not promoted ‹stages/transform/3-routing.md § Entity — cite, never promote›.
11. `retract` row (source withdrawn): remove what it put from `retract.remove_from` (drop/replace/unmirror,
    reason `removed — <retract.reason>`), keep what `still_wanted_by` needs, trace its hub_rows ‹stages/extract/4-analysis.md § Retracting applied content›.

**Ops:** `new_step_after`/`replace_step`/`drop_step` · `new_flow`/`replace_flow`/`drop_flow` · `set_field`/`append_note`
· `create_br` · `set_rule`/`append_rule_clause` · `mirror_br`/`unmirror_br` · `add_question` · `link` · `add_directive` · `add_principle` · `flag_conflict`.

## Example (Phase B, one row)
Row 4 (INT-002 #6, bank details confirmed before payment), UC-003 S1 sha `33649690f016`:
```json
{"id":"cs-payments-4a","trace":{"int":"INT-002","note_rows":[6],"hub":"payments","hub_rows":["4"]},
 "target":{"kind":"UC","id":"UC-003","section":"2"},"op":"new_step_after","anchor":{"ref":"S1","sha":"33649690f016"},
 "cells":{"actor":"Finance officer checks bank details are confirmed.","system":"System blocks release until they are."}}
```
