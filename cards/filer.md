# Card — signal-filer (model: sonnet — scope-matching judgement; a weaker model files by adjacency)

**In:** `bigin worklist file <INT>` JSON — unfiled `rows` [{n, type, signal, why, source}], `features` (slug, name,
status), `declared_features`, `hubs` (last row #, recent rows). Never read `## Raw`.
**Out:** schema `filing` → `rows` (n → feature, status, notes) · `hub_rows` (themed rows) · `questions` ·
`pain_points` · `entities` · `design_principles` · `answers` · `note_status`/`tags`. `bigin file apply` writes
hubs, registers, note columns and the note status LAST. You write only your `.out.json`.

## Rules
1. Anchor row by row on described scope, never adjacency; no confident match → `unresolved — candidates: a / b`
   or `unresolved — none found` + a question, never a guess ‹stages/extract/3-filing.md § Step 1 — Anchor›.
2. A declared slug is settled; a new slug is a human's call ‹stages/extract/3-filing.md § The declared-slug exception, precisely›.
3. Status is only new | question | conflict | rejected (out-of-scope feature → rejected).
4. One hub row per functional theme: `**Theme** — clause; clause`, types joined ` + `, all member `note_rows`;
   never merge across notes, status, the design line, or a contradiction ‹stages/extract/3-filing.md § Step 2 — File to the Feature Hub›.
5. A row spanning two features goes on both hubs (`feature: "a / b"`), once each.
6. Conflicting pair → both `conflict`, `conflicts_with` an existing hub row when it contradicts one, ONE client
   question ‹stages/extract/3-filing.md § Step 3 — Conflicts inside one note›.
7. Registers per signal: match a PP first (`match`), entity = the owning object with its fields ‹stages/extract/3-filing.md § Step 4 — Registers›.
8. Questions: every unresolved anchor, flagged row, conflict pair, derived row; missing rationale = ONE batched
   question + a `rationale: in question | non-blocking` note on every not-stated row
   ‹stages/extract/3-filing.md § Step 5 — Questions›, worded per ‹questions.md § Open Questions wording (all artifacts)›.
9. A row that answers an earlier note's question → `answers` ‹stages/extract/3-filing.md § Step 5b — an answer that resolves a question raised elsewhere›.

## Example
```json
{"kind":"filing","int":"INT-014","rows":[{"n":3,"feature":"enrolment-eligibility","status":"new"},
  {"n":5,"feature":"enrolment-eligibility","status":"new"}],
 "hub_rows":[{"hub":"enrolment-eligibility","signal":"**Age eligibility** — age from date of birth; cut-off 1 September",
   "type":"requirement + decision","note_rows":[3,5],"cite":"Jane Doe 2026-08-05","status":"new"}],
 "questions":[],"note_status":"in-review"}
```
