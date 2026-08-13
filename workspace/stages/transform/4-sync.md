# Stage 4 — Sync the shared registers, then conflict-check

**Runs in the orchestrator, sequentially, after every Stage 3 subagent has reported.** Never inside a
per-feature subagent: the four registers below are vault-wide, so two concurrent features would `Grep`
the same highest id and both mint `EN-007`, or one append would overwrite the other.

Variables resolve against `_bigin/conventions/paths.md`. Stage 3's subagents *reported* candidates; this
stage is where they land.

Most runs sync nothing. **Never promote an entity or manufacture a scenario speculatively** — both stay
`proposed`/absent until a signal genuinely needs them.

## Part 1 — Write the registers, one at a time

In this order, each write completing before the next starts:

| # | Candidate from Stage 3 | Write | Detail |
| :--- | :--- | :--- | :--- |
| 1 | `entity_candidates` | `{entities_file}` row → promote to `{entity_dir}` | `3-lane-entity.md` § Entity |
| 2 | `scenario_candidates` | `{scenarios_file}` `SCN-###` row, created or extended | `3-lane-entity.md` § Business Scenario |
| 3 | `design_principle_candidates` | `{design_principles_file}` row | `3-lane-design.md` § Destination 1 |
| 4 | — | the matching one-line pointer on **each participating hub** (`## Entities`, `## Business Scenarios`) | `3-lane-entity.md` § Ordering |

Step 4 belongs in this same sequential pass, not back in Stage 3: a cross-feature scenario touches hubs
whose own subagent has already finished, and a pointer written from two places at once loses a row.

**Mint every id here, never in a subagent.** `Grep` the register for the highest existing id and
increment. Create a register from its template (`{template_entities}`, `{template_scenarios}`,
`{template_design_principles}`) if it doesn't exist yet.

## Part 2 — Conflict-check each touched feature

Scoped **to that feature**, not the vault. After a new or updated FR/BR lands, re-read that feature's FR
together with its BRs and look for a genuine contradiction — two statements that cannot both hold.

A vault-wide sweep costs quadratically more and belongs to `/enrich-feature`. A wording difference, a
narrower restatement, or two rules about different conditions are not contradictions.

**Never auto-resolve one.** Recency settles a supersession (`2-qualification.md` § 4c); it never settles
a disagreement between two people's stated requirements. On finding one:

1. Raise **one** `- [ ] Q:` on the FR, naming both sides and where each came from
   (`conventions.md` § Open Questions wording — it must read cold, to someone with no context).
2. Flip the triggering Signal Log row to `conflict`, citing the earlier row's `#` in `Notes`.
3. Stop there. Stage 5 (`5-status.md`) sets the status from the live question count.

## Hand-off to Stage 5

Report: `<N> entity promotion(s), <N> scenario(s), <N> design-principle row(s), <N> in-feature
conflict(s)` — or `none this run`. Stage 5 re-counts questions on every artifact this stage touched,
including any FR that just gained a conflict question.

## Failure modes

- **Letting a subagent write a register.** Two features mint the same `EN-###`, or one append silently
  overwrites the other. This is why the stage exists.
- **Deciding a conflict.** Raise it, name both sides, stop. Choosing a winner buries a real
  disagreement inside an artifact that then reads as settled.
- **Promoting an entity nothing asked for.** A `proposed` row is cheap and reversible; an `EN-###`
  document is a permanent id and a maintenance obligation.
- **Writing a hub pointer from Stage 3.** It races the cross-feature write that Part 1 step 4 does
  safely.
- **Skipping the conflict check because the run "only updated" an FR.** An update is exactly how a new
  statement lands next to an older one that contradicts it.
