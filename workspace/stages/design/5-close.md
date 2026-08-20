# Stage 5 — Close: stamp, mirror, verify, report

```text
runs: orchestrator, LAST
in:   every UX spec, design-system file, nav map file, and hub this run touched
out:  absorbed: stamped · statuses set from a live count · hubs refreshed · twelve checks · the report
never: a status decided in Stages 1-4 · an absorbed: entry for a UC with no screen
```

## Part 1 — Stamp `absorbed:`, and only for real work

```text
per UX spec:
    designed = the UCs that got a screen row in ## 2 THIS RUN (check the file, not the report)
    absorbed: = [UC-###@<version>, …]   for every UC in `designed`, re-stamped WHOLE
    a UC in the hub's uc: but not in `designed` → stays OFF absorbed:
                                                 → named in ## 6 as not yet designed
    design_system: = {tokens_file}'s version, as it stands now
    nav_map:       = {nav_map_file}'s version, as it stands now
    engine:        = the engine Stage 1 detected (wds | figma | <plugin> | built-in)
    relationship_model: = modelled ONLY IF ## 7 exists AND carries rows. Read the section on disk;
                          a worker that reported `modelled` and wrote an empty ## 7 gets `none`
                          and its ## 7 deleted (checks 10-12)
    sources:       = every UC/BR/EN id, DESIGN-PRINCIPLES row #, and hub directive # used
    features:      = the owning slug first, then every other slug these screens touch
```

Re-stamp the **whole** list every run. A partial stamp is worse than none: the spec then claims to
reflect a version of a UC it never read.

A run that stopped halfway (context, a failed subagent) stamps only what landed and stays
`needs-clarification`. A 60%-designed feature must never read as finished.

## Part 2 — Set every status from a live count

```text
per UX spec, in this order:
1  finish writing ## 6 Open Questions
2  RE-COUNT the unchecked "- [ ] Q:" lines BY READING THE SECTION ON DISK
3  count > 0 → status: needs-clarification
   count = 0 → status: draft
   never     → accepted (human-only, D5) · superseded (only when another UX replaced this one)
```

The design system files get no status — bump `version`, append `## Changelog`, done.

## Part 3 — Refresh each hub

Per feature that owns a UX spec, **and** every other slug named in that spec's `features:`:

```text
## UX Spec              → [[UX-### <Feature>]] — <status> — <N> screens — updated <date>
uiux:                   → UX-###
## Design Directives    → rows a screen really implements: Status open → reflected
                          Notes: "reflected in UX-### <screen>"
                          a row NO screen implements STAYS open. Never flip it to look complete.
## Open Questions / Gates → one line per design question, the SAME sentence as ## 6
## Notes / History      → one dated bullet: what was designed, from which UCs
## Changelog            → one line

NEVER TOUCH             Signal Log · ## Requirement Readiness · status: · uc: · br: · FEATURES.md
```

## Part 4 — The one line back to the requirement

```text
per UC designed this run:
    UC status is NOT approved  → append ONE line to its ## Discussion:
        - **UX-###** (<date>): screens for this flow are drafted — <N> screens, see
          04-UIUX/UX-### <Feature>.md. Supporting evidence, no requirement change proposed.
    UC status IS approved      → write NOTHING on the UC. The hub pointer is the flow-back.
```

Nothing else on the UC, ever (D4). Not a step, not a rule, not a question, not a version bump.

## Part 5 — Twelve checks, every run

Each is a real failure that otherwise reports as success. **A mismatch is blocking:** repair,
re-check, then report.

| # | Check | Why |
|---|---|---|
| 1 | every `absorbed:` entry names a UC with ≥1 screen row in `## 2` | a stamped-but-undesigned UC makes the feature read as finished forever |
| 2 | every screen's `serves` cites an `S#` that exists in that UC and is not removed | a screen serving a deleted step serves nothing |
| 3 | the design system lost nothing: no token or component removed or renamed this run | D1 — every earlier screen cites those names |
| 4 | every token named in a screen spec exists in `{tokens_file}` | a screen citing a token that was never added is unbuildable |
| 5 | no raw colour/size/font value in any screen spec | D2 — one hex in a spec and the system stops being the source |
| 6 | every question in `## 6` is mirrored on the hub, same sentence, and is not already open on the UC's `## 5` | one question, two places — never two questions |
| 7 | each UX spec's `status` matches its live unchecked-question count | the invariant Part 2 exists to hold |
| 8 | both prompt blocks exist and contain no `UC-`/`BR-`/`EN-`/`UX-`/`INT-`/`PRD-` id | D6 — an id in a prompt renders as a heading in the prototype |
| 9 | `{nav_map_file}` lost nothing (no entry removed/renamed); every entry's `Points to` (when not "—") names a screen that really exists in an actual UX spec; every entry whose `id` has a dot has a parent `id` that also exists in the table | D1, and either an orphaned menu entry (dead link) or an orphaned branch (a child with no parent row) reaches a client looking like real IA |
| 10 | `relationship_model:` matches `## 7` **on disk**: `modelled` ⟺ `## 7` exists with ≥1 row in any of its four tables; `none` ⟺ `## 7` is absent or was deleted | an empty `## 7` reads as "the relationship was considered and there is none" when nobody looked — and a `modelled` flag over no rows makes the next run skip the work |
| 11 | every **Memory Architecture** row names an `EN-###` field that really exists in that entity's field list, and every filled **stage 3 — autonomous** cell cites a `BR-###` that really exists | D7. A memory over no stored field is a relationship the system cannot have; an ungranted autonomous cell reaches a prototype as the agent acting alone, with nobody having decided it may |
| 12 | every gap `## 7` produced (an unstated autonomy ceiling, retention rule, memory owner, wrong-answer path, or learning disclosure) is an unchecked `- [ ] Q:` in `## 6` marked as a requirement gap | the gaps are the section's main output. Found and not written down, they are worse than never looked for — the run reports a relationship model that quietly assumed all five |

Also confirm **every feature Stage 1 put on the work-list was reached**: designed, or skipped with a
stated reason. A feature the run never got to prints as **pending**, never disappears — otherwise the
next run's scan and the human both assume it was covered.

## Part 6 — Report

```text
mode:      bootstrap | extend — design system v<x> (<N> tokens, <N> components), nav map v<x> (<N> entries)
engine:    <engine> | built-in — <install command, if none was found>
boosters:  <agentic-ux-design | design-library | none> — <one line: where it applied and why, or "none — did not apply this run">
Stage 1:   <N> feature(s) in scope — <slug>: <N> NEW, <N> CHANGED, <N> CURRENT (skipped)
Stage 3:   <slug> UX-### created|updated — <N> screens (<N> new), <N> states
                  serving UC-### S<n>… (one line per feature)
Stage 2B:  <N> token(s) added, <N> component(s) added — total <N> tokens / <N> components
           <N> nav entr(y/ies) added — total <N> entries; 0 removed, 0 renamed (tokens or nav)
Stage 4:   <slug> UX-### — Claude design ✓  Figma Make ✓ (+ relationship block, when modelled)
relationship: <slug> UX-### modelled — context <N> / memory <N> / trust <N> / measures <N>,
              <N> requirement gap(s); or "<slug>: none — failed <judges|persists|repeats>"
              (one line per feature in scope; "none" everywhere is the normal result)
directives: <slug> #<n> → reflected (one line each); <N> still open
skipped:   <slug>/UC-### — <no main flow | already current | owned by <slug> | removed>
pending:   <slug> — on the work-list, not reached this run
questions: UX-### — <the question>, owner client|team [design | REQUIREMENT GAP]
next:      human review of UX-### → paste a Prototype Prompt into Claude design or Figma Make
           requirement gaps → /bigin-transform-signal
```

**Report what the vault says after Part 5, not what the run intended.**

## Failure modes

- **Stamping `absorbed:` from the report instead of the file.** A subagent that reported success
  without landing its write leaves a feature permanently reading as designed.
- **Setting status early.** The most common drift in this vault. Count last, from disk.
- **Flipping a directive to `reflected` because it was in the brief.** It is reflected when a screen
  implements it, not when it was read.
- **Refreshing only the owning feature's hub.** The other features in `features:` read as undesigned.
- **Editing the UC beyond the one `## Discussion` line.** That is `/bigin-transform-signal`'s job and
  the human gate exists for a reason.
- **Dropping a feature out of the report because the run ran out of room.** Pending is a result.
- **Leaving a nav entry pointing at a screen check 9 never confirmed.** It reaches a client as a
  menu item with nothing real behind it.
- **Stamping `relationship_model: modelled` from the worker's report.** Same failure as stamping
  `absorbed:` from a report: the flag says the relationship was modelled, no future run re-opens it,
  and `## 7` is empty. Read the section, count the rows.
- **Passing check 11 by eye.** "Grounded by: the customer entity" is not a field. Open the `EN-###`
  and find the field name, or the row is a requirement gap.
- **Letting `## 7`'s gaps stay in `## 7`.** A gap named only in the relationship model is invisible
  to the human review, to the hub, and to `/bigin-transform-signal`. It has to be a `## 6` question.
