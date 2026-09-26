# Card — uc-router (model: inherit/opus — the costliest call)

**In:** `bigin worklist route <slug>` JSON — `rows`, `candidates` (UC cards: summary, steps/flows with `sha`,
§ 4 BR ids, open questions), `brs`, `uc_index` (all UC titles). The worklist is your read: never open a UC/hub file.
**Phase A out:** `route` — one entry per row (per clause for a `a + b` Type), `new[]` for genuinely new goals.
**Phase B out:** `changesets` — final text, one change set per intended edit. Write only your `.out.json`.

## Rules
1. Same goal = same actor sitting down to accomplish the same thing → update that UC, at any status; a new
   step, branch, validation or rule is an update ‹stages/transform/3-routing.md § Which UC — new or update›.
2. A new goal is a `new` entry with a `key`; the engine mints ids between phases.
3. Route per clause: every `+`-joined Type clause gets its own destination ‹stages/transform/3-routing.md § The lane table›.
4. Steps: one action by one named actor, intent not gesture, System column filled, nothing unstated invented
   ‹stages/transform/3-lane-uc.md § Writing a step›. Flows: branch point is an S#, condition a detected fact,
   every flow ends ‹stages/transform/3-lane-uc.md § Writing an alternative or exception flow›.
5. A rule is `If <condition>, then the system must|must not <effect>`, one rule per BR, no unstated threshold
   ‹stages/transform/3-lane-br.md § Writing the rule statement›. Link it to the UC with `mirror_br` + `enforced_at`.
6. Copy anchor `ref` + `sha` from the worklist exactly; a mismatch becomes a drift question.
7. Missing fact → `add_question` (self-contained, plain language, one decision) or a `gate` on the change that
   depends on it ‹questions.md § Open Questions wording (all artifacts)›. Never guess.
8. Every change set carries `trace` {int, note_rows, hub, hub_rows, xr?} from the row's Source cell.
9. Presentation-only statements → `add_directive` on the hub (DESIGN target) ‹stages/transform/3-routing.md § The design boundary test›.
10. Never set status, approve or renumber; entities are cited, not promoted ‹stages/transform/3-routing.md § Entity — cite, never promote›.

**Ops:** `new_step_after`/`replace_step`/`drop_step` · `new_flow`/`replace_flow`/`drop_flow` · `set_field`/`append_note`
· `create_br` · `set_rule`/`append_rule_clause` · `mirror_br` · `add_question` · `link` · `add_directive` · `add_principle` · `flag_conflict` · `unmirror_br`.

## Example (Phase B, one row)
Row 4 "The applicant confirms their bank details before payment" (INT-002 #6), UC-003 S1 sha `33649690f016`:
```json
{"id":"cs-payments-4a","trace":{"int":"INT-002","note_rows":[6],"hub":"payments","hub_rows":["4"]},
 "target":{"kind":"UC","id":"UC-003","section":"2"},"op":"new_step_after","anchor":{"ref":"S1","sha":"33649690f016"},
 "cells":{"actor":"Finance officer checks the bank details are confirmed.","system":"System blocks release until they are."}}
```
plus `mirror_br` BR-006 at S3 if BR-006 already states that rule.
