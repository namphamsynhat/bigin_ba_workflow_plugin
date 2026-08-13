# Stage 5 — Status, verification, and report

**Runs in the orchestrator, last.** Every `status` in the run is set here and nowhere else — Stages 1–4
write content and leave status alone. A status decided mid-stage and left stale by a later edit to the
same artifact is this vault's most common drift (`conventions.md` § Open Questions ↔ status consistency).

Variables resolve against `_bigin/conventions/paths.md`.

## Part 1 — Set every status from a live re-count

Per artifact this run touched, in this order. **Derive the status from the count, not from memory of what
the run intended to resolve:**

1. Apply every accepted change to `## Open Questions` first — tick genuinely resolved boxes, append
   genuinely new ones.
2. **Re-count** the remaining unchecked `- [ ] Q:` lines by reading the section on disk.
3. Set the status:
   - count `> 0` → `needs-clarification`
   - count `0` → `draft`, or the stage the artifact had already reached if this run only resolved a
     question without editing content.

Two hard limits:

- **Never write `in-review` or `superseded` on an FR/BR.** Both are retired
  (`conventions.md` § Status vocabularies). Never write `removed` either — that is human-gated only.
- **Editing content on an `enriched`/`approved`/`consolidated` artifact sets it back** to
  `draft`/`needs-clarification`. Approval does not freeze an FR.

## Part 2 — Refresh the hub, don't restate it

Per touched hub:

- Refresh `## Requirement Readiness` — a snapshot for orientation, re-derived from each FR's own status.
  It is not the gate; each FR's own `status` is.
- Append one `## Notes / History` bullet.
- **Do not change the hub's `status:`.** It mirrors the `{requirements_file}` row — a scope state, not a
  workflow state. There is no "ready for PRD" feature status.

## Part 3 — Verify before reporting

Each of these five is a real failure that otherwise reports as success. Check all five, every run.
**A mismatch is blocking:** repair it and re-check rather than report a count the vault doesn't support.

| # | Check | Why it matters |
| :--- | :--- | :--- |
| 1 | Every `staged` row has a matching `## Discussion` entry citing its `INT-###` | A `staged` row with nothing staged is stranded — it no longer reads as pending, so no future run collects it |
| 2 | Every `applied` row shows its content in the artifact, or carries a `Notes` pointer explaining why no change was needed | `2-qualification.md` § Gate 4 |
| 3 | No Signal Log row was renumbered, deleted, un-merged into one row per signal, or had its `Signal`/`Source` text rewritten — except a Gate 3 clause refresh, which carries `Notes: refreshed from <INT-###>` | Row `#`s are permanent; other artifacts cite them, and a themed row's `Source` cite is the only trail back to the note rows it covers |
| 4 | Every question raised exists as an unchecked `- [ ] Q:` on the artifact named, and duplicates no question already open on the source `INT` note | One question, two places — never two questions |
| 5 | Each touched artifact's `status` matches its live unchecked-question count | The invariant Part 1 exists to hold |

## Part 4 — Report

```text
Stage 1 (fold-in): <N> FR/BR resolved — <slug>: FR-### now draft, ready for /enrich-feature
Stage 2 (qualify): <N> qualified, <N> held (<reason>), <N> applied as duplicate/already-covered
Stage 3 (draft):   <N> FR created, <N> updated, <N> BR created, <N> BR updated — <slug>: FR-### (staged, needs-clarification | staged, draft)
                   design: <N> directive(s) — <slug> ## UX Spec, <N> DESIGN-PRINCIPLES row(s)
Stage 4 (sync):    <N> entity promotion(s), <N> scenario(s), <N> in-feature conflict(s) — or "none this run"
remaining unanswered: <slug>: FR-###/BR-### — N open question(s), owner client|team
next: <slug> ready for /enrich-feature | <slug> ready for /prototype-design (design-only)
```

Report what the vault says after Part 3, not what the run intended. A held signal names its remedy; a
blocked row names why.

## Failure modes

- **Setting status from intent.** "I resolved that question" is not the same as "the box is ticked on
  disk." Re-read and count.
- **Reporting before verifying.** All five checks pass silently when they pass — that's the point. The
  run that skips them is indistinguishable from the run that passes them, until a signal goes missing.
- **Changing a hub's `status:`.** It mirrors scope from `{requirements_file}`; overwriting it desyncs the
  registry from the hub with nothing to reconcile them.
- **Flipping an artifact off `needs-clarification` with a question still unchecked** — including one
  raised earlier in the same run and forgotten.
