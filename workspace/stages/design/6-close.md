# Stage 6 — Close: stamp, mirror, verify, report

```text
runs: orchestrator, LAST
in:   every UX spec, nav map file, and hub this run touched
out:  absorbed: stamped · statuses set from a live count · hubs refreshed · nineteen checks · the report
never: a status decided in Stages 1-5 · an absorbed: entry for a UC with no screen
```

Extend the navigation map first (`2-navigation.md` § Part B) — the close below stamps its version.

## Part 1 — Before the engine closes: what only you can write

```text
per UX spec this run touched:
  ## 6 Open Questions   finished — every gap Stages 3-5 raised is an unchecked "- [ ] Q<n>:" line
  sources:              every UC/BR/EN/PP id, DESIGN-PRINCIPLES row #, and hub directive # used
  features:             the owning slug first, then every other slug these screens touch
                        (the close writes a pointer on EVERY hub named here — a participant hub with
                         no pointer reads as undesigned and comes back on the next work-list)
  engine:               the METHOD layer Stage 1 detected (wds | figma | <plugin> | built-in) — NOT
                        a renderer; what rendered a spec is /bigin-render-design-od's to write in ## 8
  platform:             the dispatched value; an override only where ## 1's Platform line cites the
                        directive or principle that EXPLICITLY stated it

per hub ## Design Directives row a screen REALLY implements:
  Status open → reflected · Notes: "reflected in UX-### <screen>"
  a row no screen implements STAYS open. Never flip it to look complete: reflected means a screen
  implements it, not that it was in the worklist.
```

## Part 2 — Close each feature

```text
bigin design close <slug> --run <run>        per feature that owns a UX spec this run touched
```

From the file on disk — never from a worker's report — it:

```text
absorbed:      re-stamped WHOLE: every use case this feature owns that has ≥1 ## 2 screen row, at its
               live version. A use case with no screen row stays OFF, is listed as `not designed`,
               and keeps the spec at needs-clarification — a 60%-designed feature never reads as done
status:        needs-clarification if any "- [ ] Q" is open in ## 6 (or a use case is not designed),
               else draft. Never accepted (human-only, D5) and never superseded
nav_map:       the navigation map's version as it stands
relationship_model: `modelled` over an empty or absent ## 7 becomes `none`
each hub in features:   ## UX Spec pointer line + uiux:
the owning hub          every open ## 6 question mirrored into ## Open Questions / Gates, tagged
                        (ref: UX-### § 6 Q<n>) — one question, two places, never two questions —
                        and one dated ## Notes / History bullet
each designed UC that is NOT approved   ONE ## Discussion line: "screens for this flow are drafted".
                        An approved UC gets nothing (D4): the hub pointer is the flow-back
stale:         cleared, by `bigin cascade`
the run        `designed:<slug>` recorded, so a resumed run skips this feature
```

It is idempotent — run it again after a repair. It never touches the Signal Log, `## Pain Points`,
`## Requirement Readiness`, a hub's `status:` / `uc:` / `br:`, `FEATURES.md`, or `PAIN-POINTS.md`.

**A pain-point row is named, never closed.** A flow resolving `PP-004` says so in its `Resolves` cell;
`/bigin-transform-signal` is what closes the row (`design-core.md` § Write map). The navigation map
gets no status — bump `version`, append `## Changelog`, done.

## Part 3 — Nineteen checks, every run

`bigin design close` ends by running the lookups and prints them. **A `BLOCK` line is blocking:**
repair (a scoped worker for anything inside a screen block), re-run the close, then report. A
`confirm` line is a heuristic — open only the block it names and decide.

**The engine runs these** — do not repeat them by eye:

| # | Check |
|---|---|
| 1 | every `absorbed:` entry names a UC with ≥1 screen row in `## 2` |
| 2 | every `Serves` cites a step or flow that exists and is not removed; every inventory row has a `## 3` block and the reverse |
| 3 | every `Role` is on the closed list or blank; one `primary action` per screen |
| 4 | no hex, px, font name or `--token` id in a screen spec (D2) |
| 5 | every open `## 6` question is on the hub |
| 6 | `status` matches the live open-question count |
| 7 | no `## Prototype Prompt` heading remains |
| 9 | `relationship_model:` matches `## 7` on disk |
| 12 | frontmatter `platform:` equals `## 1`'s Platform line |
| 13 | every Regions / Layout line uses its platform's vocabulary |
| 14 (half) | `actors:` and the Actor & Scope table hold the same roles; every row carries a ground |
| 15 | every screen has an Actor and a Volume; a `many` screen has a find mechanism, its five volume states and a real number |
| 16 (flag) | each bulk / export / select-all / saved-view / subscription mention with no UC or BR on its line |
| 17 | `### Coverage` exists, every row's verdict is well-formed, `covered` has a `Covered by`, a `gap` points at an open question, every step, flow, rule and pain point has a row, no pain point is `covered` without a flow naming it; `### Flow Review` has its rows |
| 18 | every `View ID` is present, `<slug>-<screen-kebab>`, and unique across every spec |
| 19 | every `Screen Type` is one of the four and agrees with the nav map's `(Landing)` / `(Drill-down)` tags |

**These need a reader** — they are yours, every run:

| # | Check | Why |
|---|---|---|
| 8 | the navigation map lost nothing: `git diff` it — no entry deleted, no `id` changed in place (a re-nest adds the new row and retires the old one); every `Points to` names a real screen; every dotted `id` has its parent in the same `## Structure` section | D1. An `id` edited in place silently un-points every screen spec citing the old path |
| 10 | every `## 7` Memory Architecture row names an `EN-###` field that really exists, and every filled stage 3 cell cites a real `BR-###` | D7. A memory over no stored field is a relationship the system cannot have |
| 11 | every gap `## 7` produced is an unchecked `## 6` question marked as a requirement gap | the gaps are that section's main output |
| 14 (half) | every Actor & Scope actor really appears in an in-scope UC's `## 1`, and each cell's ground really says what the cell claims | an invented actor is an invented persona; a guessed `all` hands an actor reach no rule granted |
| 16 | each flagged capability is really granted by the UC step or BR it cites — or it comes off the screen and becomes a requirement gap | D8. An ungranted bulk affordance becomes a requirement nobody wrote or costed |
| 17 (half) | a `covered` row's `Covered by` names something that is really there — and for a `PP-###`, a **flow** and the moment in it the actor stops experiencing that pain, never a screen name | the engine checks the table's shape, not its truth |
| 13 (half) | on `both`, each `Layout — Web` / `Layout — Mobile` split is a real difference, not one block written twice | a duplicated split is maintained as two copies and they drift |

Also confirm **every feature Stage 1 put on the work-list was reached**: designed, or skipped with a
stated reason. A feature the run never got to prints as **pending**, never disappears.

## Part 4 — Report

```text
mode:      bootstrap | extend — navigation map v<x> (<N> entries)
platform:  <web | mobile | both> (project config) [ · override: <slug> → <web|mobile|both>, grounded
           by <UC-### / directive #n / DESIGN-PRINCIPLES #n> (one per overriding feature) ]
method:    <wds | figma | <plugin> | built-in> — <install command, if none was found>
           (the METHOD layer only. Nothing rendered this run; nothing in this skill can)
pattern skills: <the designer-skills used | none> — <one line: where each applied, or "none — did not apply this run">
Stage 1:   <N> feature(s) in scope — <slug>: <N> NEW, <N> CHANGED, <N> CURRENT (skipped)
Stage 3:   <slug> UX-### created|updated — <N> screens (<N> new), <N> states, <N> flows
                  serving UC-### S<n>… (one line per feature)
Stage 2B:  <N> nav entr(y/ies) added — total <N> entries; 0 deleted, 0 renamed in place
Stage 4:   <slug> UX-### — <N> flow(s) reviewed: <N> sound, <N> improved, <N> gap(s);
           <N> nav entr(y/ies) re-nested | none
Stage 5:   <slug> UX-### — <N> item(s) checked: <N> covered, <N> gap(s), <N> out of scope;
           pain points: <N> of <N> resolved by a flow;
           <N> row(s) repaired; render-ready: yes | <N> input gap(s) raised
           (one line per feature; "0 gaps" is a real result and gets printed)
pain points: <slug> — PP-### resolved by flow <goal> (one line each);
           <N> still unresolved — question raised | none open on this feature
design system: NONE PRODUCED, by design. Colour, type, spacing, and components come from the design
           team or are bound at render time. Never reported as a gap
render:    not this skill's job — /bigin-render-design-od, whenever a human wants it, on the engine
           they choose. Never reported as done, skipped, or waived here: there was nothing to do
actors:    <slug> UX-### — <N> actor(s): <role> (sees <own|assigned|unit|all>, <one|few|many>);
           … (one line per feature)
           splits: <place> → <screen A> (<actor>) + <screen B> (<actor>), on <volume|capability>
                   | none — no place served two actors with differing scope
           capability gaps: <N> raised (bulk/export/saved view nothing granted) | none
relationship: <slug> UX-### modelled — context <N> / memory <N> / trust <N> / measures <N>,
              <N> requirement gap(s); or "<slug>: none — failed <judges|persists|repeats>"
              (one line per feature in scope; "none" everywhere is the normal result)
directives: <slug> #<n> → reflected (one line each); <N> still open
skipped:   <slug>/UC-### — <no main flow | already current | owned by <slug> | removed>
pending:   <slug> — on the work-list, not reached this run
questions: UX-### — <the question>, owner client|team [design | REQUIREMENT GAP]
next:      human review of UX-### → then, when they want a prototype in front of a client:
             /bigin-render-design-od [<slug>]   — their choice of design system, project, and timing
           requirement gaps → /bigin-transform-signal
```

**Report what the vault says after Part 3, not what the run intended.**

## Failure modes

- **Stamping by hand.** `absorbed:`, the status, the hub pointer and the mirrored questions are the
  engine's. A hand stamp is the one taken from a worker's report, and a worker that reported success
  without landing its write leaves a feature reading as designed forever.
- **Closing before `## 6` is finished.** The status is counted from disk at the moment of the close.
- **Flipping a directive to `reflected` because it was in the worklist.**
- **Leaving a participant slug out of `features:`.** That hub gets no pointer and reads as undesigned.
- **Editing a UC beyond the one `## Discussion` line the close writes.** That is
  `/bigin-transform-signal`'s job and the human gate exists for a reason.
- **Treating the engine's OK as the whole of Part 3.** It ran the lookups. Checks 8, 10, 11 and the
  truth behind 14, 16 and 17 are still unread.
- **Passing check 17 by its shape.** Open the screen a `covered` row names and find the state; for a
  `PP-###`, open the flow. A screen name in a pain point's `Covered by` is the subject coming up
  somewhere, not a journey fixing anything.
- **Filling a pain point's `Resolved by` cell on the hub or the register.** Both are the requirement
  side's.
- **Reporting the absent design system as a gap, or reporting a render.** There is none by design,
  and nothing in this skill renders.
- **Dropping a feature out of the report because the run ran out of room.** Pending is a result.
