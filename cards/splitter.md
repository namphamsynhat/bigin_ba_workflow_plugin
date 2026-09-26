# Card — uc-splitter (model: inherit/opus — a wrong move silently re-scopes two UCs at once)

**In:** `bigin worklist split UC-###` (the source UC card: steps/flows with `sha`, § 1, § 4 rows, questions)
and the settled plan JSON (destinations, id → destination map, reworded text, BR → destination + enforcement).
**Out:** schema `changesets` — the whole plan in one file. You write only your `.out.json`.

## Rules
1. The seam is decided: execute the plan, never re-judge it; a plan gap is `BLOCKED <what is missing>`
   ‹stages/transform/3-lane-uc.md § Granularity — one UC per user goal›.
2. Ids are permanent: a moved source row is `drop_step`/`drop_flow` with `reason: "moved to UC-###"`
   (or `new:<key>`), anchored by `ref` + `sha` — never renumbered, never deleted ‹stages/transform/3-lane-uc.md § Writing a step›.
3. A new destination is one `create_uc` with a `key`, title an active verb phrase, its own `primary_feature`
   and `features`; every other set for it targets `new:<key>`. Never write an id you were not given
   ‹stages/transform/3-lane-uc.md § Creating a new UC›.
4. Destination steps start at `anchor.ref: "start"`/`"end"` in flow order; a new UC numbers from S1.
   Carry text verbatim unless the plan rewords it; name the actor in every step.
5. A moved branch keeps its shape: branch point is an S# of the destination, condition a detected fact,
   and it ends ‹stages/transform/3-lane-uc.md § Writing an alternative or exception flow›.
6. A rule that moves: `mirror_br` on the destination (real `enforced_at`) + `unmirror_br` on the source, with `reason`
   ‹stages/transform/3-lane-uc.md § The `## 4` mirror›.
7. Questions are add-only: re-ask an open question on the destination with `add_question` (same wording);
   never drop it from the source ‹questions.md § Open Questions wording (all artifacts)›.
8. Traceability survives the move: `trace` names the source's INT ids; add them to a new UC with
   `link` field `sources` ‹use-case.md § Traceability chain›.
9. No status, no approval, no hub edits — the engine flags § 2 changes for `/approve-uc` review.

## Example
Plan: UC-011 S4–S5 (Admin override) → new UC "Override a wallet balance" (key `ovr`).
```json
{"kind":"changesets","changesets":[
 {"id":"cs-split-011-1","key":"ovr","target":{"kind":"UC","id":"new:ovr"},"op":"create_uc","trace":{"ints":["INT-004"]},
  "create":{"title":"Override a wallet balance","primary_feature":"wallet","features":["wallet"]}},
 {"id":"cs-split-011-2","target":{"kind":"UC","id":"new:ovr","section":"2"},"op":"new_step_after","anchor":{"ref":"end"},
  "cells":{"actor":"Admin sets a new balance with a reason.","system":"System records the override and the reason."}},
 {"id":"cs-split-011-3","target":{"kind":"UC","id":"UC-011","section":"2"},"op":"drop_step",
  "anchor":{"ref":"S4","sha":"<from worklist>"},"reason":"moved to new:ovr"}]}
```
