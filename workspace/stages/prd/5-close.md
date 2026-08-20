# Stage 5 — Close: stamp, status, hub refresh, verify, report

```text
runs: orchestrator, LAST, sequentially per feature (never in a worker — hubs are shared state)
in:   every PRD written this run · every participating hub
out:  absorbed: · design_absorbed: · status · the Traceability table · hub ## PRD + prd: ·
      hub ## Open Questions / Gates · changelogs · the run report
never: setting status: approved (P5) · touching a UC, BR, entity, or UX spec (P4) ·
       stamping a UC that got no capability row
```

## Part 1 — Traceability table

One row per § 5 capability. Every cell filled or `—`; never blank.

```text
Capability     C# + name from § 5
UC             UC-<NNN>@<version> — the version folded, not the current one on disk if they differ
                                    (they should not; Stage 1 read it this run)
Rules          the BR-### ids in § 7 that apply at this capability's steps, or —
Information    the EN-### ids in § 8 this capability's steps touch, or —
Screens        the § 9 screen names serving this capability, or —
Raised in      the INT-### ids from the UC's sources:
```

A capability with `—` in `Raised in` is scope nobody asked for. That is a blocking finding, not a
formatting gap: report it and name the capability.

## Part 2 — Stamp the staleness records

```text
absorbed:         UC-<NNN>@<version> for EVERY approved UC that really got a § 5 capability row
                  this run — the FOLD list plus the CURRENT ones already covered.
                  RE-STAMPED WHOLE, never appended to.
design_absorbed:  UX-<NNN>@<version> for each design reported in § 9. Whole, same discipline.
uc:               the same ids as absorbed:, without versions
pending_uc:       the § 10 Pending Scope ids
brs: entities: uiux: features: sources:   from what §§ 5-9 actually cite
```

`absorbed:` is the entire mechanism that makes "this PRD has drifted from its use cases" detectable
(`{conventions_reference}` § Absorbed) — `sources:` cannot answer it, because a CR edits a UC in place
and the id keeps looking covered. Two rules make it self-healing:

- **re-stamp the whole list every run.** No counter, no append — a re-run cannot leave a false
  "current" claim behind.
- **never stamp a UC that got no capability row.** A UC stamped without being folded reads as covered
  forever, and no future run picks it up. This is the most expensive mistake available in this stage.

Bump `version:` (existing PRD) and append a `## Changelog` line naming what changed and which UCs
drove it. Set `updated:` to today.

## Part 3 — Status, from a live count on disk

```text
count the unchecked "- [ ] Q:" lines in § 11 of the file as it now exists

  any unchecked line   → status: draft
  zero unchecked lines → status: draft
```

Both branches are `draft`. **This stage never writes `approved`** (P5) — a human approves a PRD, the
same way a human approves a UC (hard rule 4). The count still matters: report it, because zero open
decisions is what tells a human this PRD is ready to take to the sponsor, and the report is the only
place that shows.

## Part 4 — Refresh every participating hub, one at a time

Per slug in the PRD's `features:` (owner first):

| Hub location | Write |
|---|---|
| `prd:` frontmatter | the `PRD-###` id |
| `## PRD` | the link + status: `[[PRD-<NNN> <Feature>]] — draft, N capabilities, M pending` |
| `## Open Questions / Gates` | mirror § 11's lines, **same sentence** as the UC/UX they came from — never a reworded second copy |
| `## Notes / History` · `## Changelog` | one line each: what this run folded |

**Nothing else on the hub.** Not the Signal Log, not `## Requirement Readiness`, not `## Use Cases`,
not `status:`, not `uc:`/`br:`/`uiux:`. There is no "ready for PRD" feature status and this stage does
not invent one (`{conventions_reference}` § Feature Hub, maintenance contract).

Sequential, one hub per write pass — a hub is shared state and two concurrent writers lose a section.

## Part 5 — Eight verification checks. A mismatch is blocking.

Run these against the files **on disk**, not against what the run intended.

| # | Check | Fails when |
|---|---|---|
| 1 | one PRD per feature | two files in `{prd_dir}` carry the same `feature:` slug |
| 2 | id matches filename | `id:` and the `PRD-###` in the filename disagree |
| 3 | `absorbed:` ⇔ capabilities | an id in `absorbed:` has no § 5 row, or a § 5 row's UC is missing from `absorbed:` |
| 4 | approved-only body | any id in `uc:` is not `approved` on disk, or any `pending_uc:` id appears in §§ 5-9 |
| 5 | status invariant | `status:` is anything but `draft`, or § 11's live count was not the one reported |
| 6 | traceability complete | a § Traceability row has a blank cell, or `—` in `Raised in` |
| 7 | no technical leakage | §§ 1-12 contain an endpoint, a schema/field type, a framework, a hex value, a px value, or a token name (P1) |
| 8 | hub agrees | the hub's `prd:` or `## PRD` link disagrees with the file that exists |

Report every failure with its file and section. A failing check is never "close enough" — checks 3
and 4 are the two that make a PRD lie about its own coverage.

## Part 6 — The run report

```text
engine · per feature: PRD-### (new|updated v1.0→v1.1) · capabilities · flows · rules · entities
screens folded (UX-###@version | no design) · pending scope (ids) · CURRENT skipped · features
skipped (chain: cr | nothing approved) · open decisions (count, and how many are requirement gaps)
verification: 8/8 or the failures · next
```

`next` is one of: `/approve-uc` on the pending ids · `/bigin-transform-signal` to clear an open
decision · `/bigin-generate-design` when a design is missing or stale · a human takes the PRD to the
sponsor · epics/stories, by hand until that stage is built
(`{conventions_reference}` § Reconciliation notes).

Report what the vault says, not what the run meant to do. A count recomputed from intent instead of
from the file is how a clean-looking report hides a half-written section.
