# Stage 4 — Apply, adjudicate, conflict- and coverage-check

```text
runs: inside workflows/transform.js per feature (Apply, Adjudicate, Close), or the orchestrator's
      fallback loop; Parts 3–4 in the orchestrator after every feature has applied
in:   each feature's ingested changesets.out.json · conflict/held rows (code-grounded vaults)
out:  every artifact written ONCE by the engine · Signal Log rows flipped · links synced · hubs refreshed
      · statuses re-counted · each touched feature conflict-checked, then coverage-checked as a UC set
never: a hand edit to a UC, BR, or hub's derived tables · an id minted by an agent
```

`BIN="${CLAUDE_PLUGIN_ROOT}/bin/bigin"`. Every write in this stage is an engine command.

## Part 1 — Shared registers, serially

A new durable design principle is an `add_principle` change set (target `{"kind":"DESIGN","id":"principles"}`)
applied by `$BIN apply` like any other — the engine appends the `DESIGN-PRINCIPLES.md` row (creating the
register if absent) and flips the traced Signal Log row. Refining or contradicting an existing principle
stays an orchestrator call (`3-lane-design.md` § Destination 1). Entities are never minted or promoted here
(`/sync-entities`); a new UC id is minted only by `$BIN mint route` (Stage 3) or a `create_uc` set.

## Part 1b — Every participating hub

```text
$BIN hub refresh <slug> [<slug> …]   # uc: pointers, ## Use Cases (owns | participates, no step counts),
                                     # ## Requirement Readiness (one row per artifact), the add-only
                                     # ## Open Questions / Gates mirror, one Changelog line
$BIN links sync                      # brs:/uc:/features:/sources: and the FEATURES.md UC column
```

`bigin apply` already refreshes every hub it touched and syncs links; run these again after Part 1 and
after any hand-made hub flip. Both are idempotent. Signal Log and Coverage Gaps are never touched by a
refresh — the engine refuses the write if either changed.

## Part 2 — Apply the change sets

```text
$BIN apply _runs/$RUN/tasks/<slug>.changesets.out.json --run $RUN
```

Per artifact, one write: sets applied in a fixed order (steps → flows → § 1/§ 6 → rule → § 4 mirrors →
questions), version bump, one Changelog line citing the trace and every applied change-set id, `§ 2
changed — flagged for review` when a step changed (the reason `/approve-uc` re-reviews it), status left to
Stage 5. Gated sets go to the ledger with their question on the artifact. Afterwards the engine flips each
traced Signal Log row — `applied` when all its sets landed, `staged` while one is gated or drifted —
syncs links, refreshes the touched hubs, re-counts touched statuses, and re-renders `## Pending changes`.

**The human may have edited the text first** — the engine's drift rule (`1-foldin.md` § The human may
have edited the section first): sha mismatch → not applied, one question naming both wordings; text
already identical → counts as applied. Never "fix" a drift by editing the file.

Read the apply result, not a report: `applied · already · gated · drift · invalid · rejected`. An
`invalid` set (a missing target, an enforcement point naming a dropped step, a BR with no settled
statement) is re-dispatched to the router with the engine's reason, or its row parked `held`.

## Part 2b — Coverage, not claims

For each feature, diff what was **dispatched** against what **landed** (`$BIN run summary $RUN`):

```text
1  every qualified row is applied, staged (gated/drift), conflict, question, or listed as `unrouted`
   with a reason — a row still `new` after apply is UNACCOUNTED: re-route it (`worklist route --rows <n>`)
   or park it: $BIN hub flip <slug> <n>=held@<why>
2  a themed row whose Type is `<a> + <b>` shows a destination per clause in its Destination cell
```

A mismatch is **blocking**: fix or park with a written reason, then re-check. Report the counts either
way — "3 dispatched, 3 accounted for" is what makes a future silent drop visible.

## Part 3 — Adjudicate (code-grounded) and conflict-check

**Adjudicate** when `project.md` `grounding:` is `codebase` or `both` and the feature has `conflict`/`held`
rows: `workflows/adjudicate.js` (or the fallback in `references/agent-dispatch.md` step 8) — one
`code-adjudicator` per row, a second independent judge for P0/security rows, verdicts applied by
`$BIN apply`. `conflict_policy: code-first` lets code settle a factual disagreement; `ask` settles the facts
and gates the decision. Intent questions are never settled by code. Flip a superseded loser with
`$BIN hub flip <slug> <n>=superseded@superseded by the decision on #<m>`.

**Conflict-check** each touched feature, scoped to that feature — never the vault:

```text
1  step vs. rule     — a ## 4 rule whose condition contradicts what a step does
2  rule vs. rule     — two BRs on the same feature that cannot both hold
3  dangling citation — a ## 3 branch point or ## 4 enforcement point naming a missing or dropped step
                       (`bigin mirror br <UC>` and `bigin lint --full` report these mechanically)
```

A wording difference, a narrower restatement, or two rules about different conditions are not
contradictions. **Never auto-resolve one.** On finding one: a `flag_conflict` set on the hub (target `{"kind":"HUB","id":"<slug>"}`,
`trace.hub_rows` = the triggering row, `text` = one question naming both sides and where each came from) —
`$BIN apply` raises the question and flips the row to `conflict`. Stop there — Stage 5 sets the status.

## Part 4 — Coverage-check each touched feature

Whether the feature's requirements **add up** — procedure, six lenses, and the `## Coverage Gaps` row
format in `4b-coverage.md`. Run it per in-scope feature, after Part 3:

```text
run it when: a UC on this feature was created this run or its § 2 changed
             · the hub has no `## Coverage Gaps` section yet (backfill once)
             · $ARGUMENTS named this slug (an EMPTY Stage 2 worklist does not skip it)
skip it when: the feature has no UC at all
writes:      `## Coverage Gaps` rows on that feature's hub (then `$BIN hub refresh <slug>` mirrors the
             open/answered ones into ## Open Questions / Gates)
never:       a UC, a step, a Signal Log row, a question on any UC, or another feature's hub
```

A coverage gap **never parks a UC** — it is a feature-level finding.

## Hand-off

Report: `<N> change sets applied / <N> already / <N> gated / <N> drift / <N> invalid, <N> UC(s) minted,
<N> flagged for review (§ 2 changed), <N> adjudicated (<N> settled, <N> left for a human), <N>
dispatched / <N> accounted for, <N> in-feature conflict(s), <N> coverage gap(s) raised / <N> closed` — or
`none this run`. Name the features whose coverage came back clean: "clean" and "nobody looked" differ.

## Failure modes

- **Editing a file to "help" the engine** — bypasses drift detection and the Changelog trace; the engine
  then refuses its next write to that file ("changed on disk since it was read").
- **Re-applying by hand what the engine reported as drift** — the reviewer's wording vanishes.
- **Deciding a conflict** — choosing a winner buries a real disagreement in text that reads as settled.
- **Skipping the conflict or coverage check because the run "only updated" a UC** — an update is
  exactly how a step lands next to a rule that forbids it, or a pre-condition nothing satisfies appears.
- **Turning a coverage gap into a UC, a step, or a question on a UC.**
- **Trusting the router's reply instead of the apply result** — Part 2b exists because a partial pass
  and a complete one produce the same shape of reply.
