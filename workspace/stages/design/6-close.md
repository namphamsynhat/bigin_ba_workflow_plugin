# Stage 6 — Close: stamp, mirror, verify, report

```text
runs: orchestrator, LAST
in:   every UX spec, nav map file, and hub this run touched
out:  absorbed: stamped · statuses set from a live count · hubs refreshed · seventeen checks · the report
never: a status decided in Stages 1-5 · an absorbed: entry for a UC with no screen
```

## Part 1 — Stamp `absorbed:`, and only for real work

```text
per UX spec:
    designed = the UCs that got a screen row in ## 2 THIS RUN (check the file, not the report)
    absorbed: = [UC-###@<version>, …]   for every UC in `designed`, re-stamped WHOLE
    a UC in the hub's uc: but not in `designed` → stays OFF absorbed:
                                                 → named in ## 6 as not yet designed
    nav_map:       = {nav_map_file}'s version, as it stands now
    engine:        = the METHOD layer Stage 1 detected (wds | figma | <plugin> | built-in).
                     NOT a renderer — nothing in this skill renders. What actually rendered this
                     spec, if anything ever does, is `/bigin-render-design`'s to write into ## 8
    platform:      = the project config's platform, as Stage 1 announced it (web | mobile | both;
                     absent in the config → web) — UNLESS a UC, a hub ## Design Directives row, or an
                     active DESIGN-PRINCIPLES row EXPLICITLY stated a platform for THIS feature, in
                     which case that value, and the citation goes on ## 1's Platform line. Never
                     re-read the config to decide it, never infer it from a step's wording (check 12)
    relationship_model: = modelled ONLY IF ## 7 exists AND carries rows. Read the section on disk;
                          a worker that reported `modelled` and wrote an empty ## 7 gets `none`
                          and its ## 7 deleted (checks 9-11)
    flow_review:   = pfd | <critique skill> | skipped — what Stage 4 actually did, read from whether
                     a ### Flow Review table is really in ## 5. A `pfd` flag over no table is the
                     same lie as a `modelled` flag over an empty ## 7 (check 17)
    sources:       = every UC/BR/EN/PP id, DESIGN-PRINCIPLES row #, and hub directive # used
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

The navigation map gets no status — bump `version`, append `## Changelog`, done.

## Part 3 — Refresh each hub

Per feature that owns a UX spec, **and** every other slug named in that spec's `features:`:

```text
## UX Spec              → [[UX-### <Feature>]] — <status> — <N> screens — updated <date>
uiux:                   → UX-###
## Design Directives    → rows a screen really implements: Status open → reflected
                          Notes: "reflected in UX-### <screen>"
                          a row NO screen implements STAYS open. Never flip it to look complete.
## Open Questions / Gates → one line per design question, the SAME sentence as ## 6
## Notes / History      → one dated bullet: what was designed, from which UCs, and which PP-###
                          a flow now resolves — named, never marked
## Changelog            → one line

NEVER TOUCH             Signal Log · ## Pain Points · ## Requirement Readiness · status: · uc: ·
                        br: · FEATURES.md · PAIN-POINTS.md
```

**A pain-point row is named, never closed.** A flow resolving `PP-004` says so in the hub's
`## Notes / History` line and in the UX spec's `## 4` `Resolves` cell. It never fills that row's
`Resolved by` cell, never changes its status, and never touches `PAIN-POINTS.md` — the register is
the requirement side's, and `/bigin-transform-signal` is what closes a row
(`{design_conventions}` § Write map).

## Part 4 — The one line back to the requirement

```text
per UC designed this run:
    UC status is NOT approved  → append ONE line to its ## Discussion:
        - **UX-###** (<date>): screens for this flow are drafted — <N> screens, see
          04-UIUX/UX-### <Feature>.md. Supporting evidence, no requirement change proposed.
    UC status IS approved      → write NOTHING on the UC. The hub pointer is the flow-back.
```

Nothing else on the UC, ever (D4). Not a step, not a rule, not a question, not a version bump.

## Part 5 — Seventeen checks, every run

Each is a real failure that otherwise reports as success. **A mismatch is blocking:** repair,
re-check, then report.

| # | Check | Why |
|---|---|---|
| 1 | every `absorbed:` entry names a UC with ≥1 screen row in `## 2` | a stamped-but-undesigned UC makes the feature read as finished forever |
| 2 | every screen's `serves` cites an `S#` that exists in that UC and is not removed | a screen serving a deleted step serves nothing |
| 3 | every element's `Role` cell holds a role from the closed list in `{design_conventions}` § Semantic style roles, or is blank; and no screen carries two `primary action` elements | an invented eleventh role is a one-screen vocabulary nothing downstream can map, and two primary actions means the screen is really two screens, or one of them was never primary |
| 4 | no raw colour, size, or font value — and **no `--token` id** — in any screen spec | D2. A hex pins a value nobody stated; a token id cites a design system this vault does not have, so it resolves to nothing and a render engine quietly picks its own |
| 5 | every question in `## 6` is mirrored on the hub, same sentence, and is not already open on the UC's `## 5` | one question, two places — never two questions |
| 6 | each UX spec's `status` matches its live unchecked-question count | the invariant Part 2 exists to hold |
| 7 | **no `## Prototype Prompt` heading remains** in any spec this run touched | those blocks were a second, hand-written copy of the screens beside them, inlining token values that no longer exist anywhere. `/bigin-render-design` builds its own prompt from `## 1`–`## 5` plus the UCs, BRs, and entity register — a leftover block is a stale spec a human may paste in good faith (`3-screens.md` § Adopting an existing UX spec deletes them) |
| 8 | `{nav_map_file}` lost nothing: no entry deleted, and no `id` changed **in place** — a Stage 4 re-nest adds the new row and retires the old one in § Removing an entry. Every entry's `Points to` (when not "—") names a screen that really exists in an actual UX spec; every entry whose `id` has a dot has a parent `id` that also exists **in the same `## Structure` section** (on `both`, the two shells are two trees — an `id` is unique within its own section, not across both) | D1, and either an orphaned menu entry (dead link) or an orphaned branch (a child with no parent row) reaches a client looking like real IA. An `id` edited in place silently un-points every screen spec citing the old path |
| 9 | `relationship_model:` matches `## 7` **on disk**: `modelled` ⟺ `## 7` exists with ≥1 row in any of its four tables; `none` ⟺ `## 7` is absent or was deleted | an empty `## 7` reads as "the relationship was considered and there is none" when nobody looked — and a `modelled` flag over no rows makes the next run skip the work |
| 10 | every **Memory Architecture** row names an `EN-###` field that really exists in that entity's field list, and every filled **stage 3 — autonomous** cell cites a `BR-###` that really exists | D7. A memory over no stored field is a relationship the system cannot have; an ungranted autonomous cell reaches a prototype as the agent acting alone, with nobody having decided it may |
| 11 | every gap `## 7` produced (an unstated autonomy ceiling, retention rule, memory owner, wrong-answer path, or learning disclosure) is an unchecked `- [ ] Q:` in `## 6` marked as a requirement gap | the gaps are the section's main output. Found and not written down, they are worse than never looked for — the run reports a relationship model that quietly assumed all five |
| 12 | the spec's `platform:` **and** its `## 1` **Platform** line hold the same value, and that value is the project config's — or both name the same per-feature override and cite the UC, directive, or principle that **explicitly stated** it | a spec silently on the wrong platform produces a prototype in the wrong shell: right screens, right copy, wrong product. Nothing else in the run catches it — every check above passes on a phone spec built for a web project — and it reaches the client as a decision somebody appears to have made |
| 13 | every screen spec's `Regions` (or its `Layout — …` lines) uses **that platform's** vocabulary — web `header / nav / main / aside / footer`, mobile `header / content / tab-bar / sheet / fab` — and on `both`, every `Layout — Web` / `Layout — Mobile` split is a real difference, not the same block written twice | the wrong vocabulary asks a tool to build a shell the platform does not have (a `tab-bar` on a web screen, a `nav` on a phone one), and a duplicated split reads as a considered difference — so the next run maintains two copies of one layout and they drift |
| 14 | the frontmatter `actors:` list and the `## 1` **Actor & Scope** table hold the same roles, in the same bands; every row names an actor that really appears in an in-scope UC's `## 1`; and every one of its three cells carries a ground that really exists (a `BR-###`, a UC step, or an `EN-###` cardinality) — no row for an actor no UC names | an invented actor is an invented persona, and every screen designed for them is scope nobody asked for wearing an owner nobody appointed. A guessed `all` in a scope cell is worse: it hands an actor reach no rule granted, and the client approves it by looking at a prototype |
| 15 | every screen spec carries an `Actor` and a `Scope` line whose actor appears in the Actor & Scope table; every screen at volume `many` carries **at least one find mechanism** (search, filter, or sort) and all five volume states — `empty`, `few`, `many at real scale` (with the real number named, not "several"), `loading`, `error`; and no screen at volume `one` carries find machinery | a `many` screen without find machinery reviews as finished and collapses on the client's real table — and no other check catches it, because every element on it is properly grounded. A `many` state that never names a number gets prototyped at three rows, which tests nothing the client is worried about |
| 16 | no screen spec carries a bulk action, an export, a "select all matching", a saved view, or a subscription unless a `UC-### S<n>` or a `BR-###` **really grants it** — and every one that was left out because nothing granted it is an unchecked `- [ ] Q:` in `## 6` marked as a requirement gap | D8, the data-side counterpart of check 10. An ungranted bulk affordance reaches the client in a working prototype, they agree it looks right, and it becomes a requirement nobody wrote or costed — except this one deletes five hundred records at a time |
| 17 | **`## 4`'s `### Coverage` table and `## 5`'s `### Flow Review` table, together.** Coverage exists and is **whole** (`5-verify.md` wrote it): one row per non-removed `S#`/`A#`/`E#` of every in-scope UC, per screen-constraining `BR-###` they cite, per `EN-###` field their steps read or write, **per unresolved hub `PP-###`**, per open hub directive, and per active principle — every row carrying `covered` (with a real screen **and** state in `Covered by`; for a `PP-###`, a real **flow** and where in it), `gap → ## 6 Q<n>` pointing at a question that really exists and is unchecked, or `out of scope — <reason>` citing something that really says so. And Flow Review matches `flow_review:` on disk: one row per `## 4` flow ⟺ the flag names a skill; **no table at all** ⟺ `skipped`. An **empty** Flow Review table fails either way | Stage 5's whole output, and the only check that can catch an **omission**. Every other check on this list runs backward — element to ground — and backward passes cleanly on a spec with an entire exception flow missing: nothing on it was invented, because nothing on it was drawn. A `covered` verdict over an empty `Covered by`, or a `gap` pointing at no question, is the table claiming a coverage nobody checked. The Flow Review half catches the same lie one level up: an empty table, or one written on a run where no review skill was installed, records that every journey was walked and found sound when nobody walked one |

**A `PP-###` row is the one to check hardest.** Every other item on the Coverage table is a step, a
rule, or a field somebody eventually notices missing. A pain point is the thing everybody assumes
somebody else handled — and a `covered` verdict naming a screen instead of a flow, or naming a flow
whose `Resolves` cell never mentions that id, is the table recording that the client's complaint was
addressed when nobody decided it was.

Also confirm **every feature Stage 1 put on the work-list was reached**: designed, or skipped with a
stated reason. A feature the run never got to prints as **pending**, never disappears — otherwise the
next run's scan and the human both assume it was covered.

## Part 6 — Report

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
           method: <pfd (mode 1) | <critique skill> | SKIPPED — not installed>
           (on a skip, ONE install line, once for the run — never per feature)
Stage 5:   <slug> UX-### — <N> item(s) checked: <N> covered, <N> gap(s), <N> out of scope;
           pain points: <N> of <N> resolved by a flow;
           <N> row(s) repaired; render-ready: yes | <N> input gap(s) raised
           (one line per feature; "0 gaps" is a real result and gets printed)
pain points: <slug> — PP-### resolved by flow <goal> (one line each);
           <N> still unresolved — question raised | none open on this feature
design system: NONE PRODUCED, by design. Colour, type, spacing, and components come from the design
           team or are bound at render time. Never reported as a gap
render:    not this skill's job — /bigin-render-design, whenever a human wants it, on the engine
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
             /bigin-render-design [<slug>]   — their choice of design system, project, and timing
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
- **Passing check 10 by eye.** "Grounded by: the customer entity" is not a field. Open the `EN-###`
  and find the field name, or the row is a requirement gap.
- **Letting `## 7`'s gaps stay in `## 7`.** A gap named only in the relationship model is invisible
  to the human review, to the hub, and to `/bigin-transform-signal`. It has to be a `## 6` question.
- **Stamping a `platform:` the spec's screens do not actually reflect.** The same class of failure as
  stamping `absorbed:` from a report: the frontmatter says `mobile`, the regions say
  `nav / main / aside`, and the prompt block builds a sidebar. Read the screens, then stamp
  (checks 12-13), or the wrong actor's screen (checks 14-16).
- **Leaving a `## Prototype Prompt` block in a spec this run touched.** It inlines token values that
  no longer exist anywhere and describes screens that may since have changed. A BA who pastes it in
  good faith gets a prototype of a design nobody is maintaining (check 7).
- **Stamping `flow_review: pfd` on a run where the stage was skipped.** Same failure as stamping
  `relationship_model: modelled` over an empty `## 7`: the flag says every journey was walked, no
  future run re-opens it, and nobody ever did. Read `## 5` for the table, then stamp (check 17).
- **Filling a pain point's `Resolved by` cell on the hub or the register.** Both are the requirement
  side's. A flow that fixes `PP-004` names it; `/bigin-transform-signal` closes the row. Closing it
  here means a pain point reads as settled on the strength of a design nobody has accepted yet.
- **Reporting the absent design system as a gap.** There is none by design, and a `design system:
  missing` line teaches every reader that something went wrong in a run that did exactly what it
  should.
- **Reporting a render.** Nothing in this skill renders any more. A `render:` line saying "done",
  "skipped", or "waived" describes a step that was never part of this run, and a reader takes it as
  evidence a prototype exists.
- **Passing check 17 by counting rows.** A `### Coverage` table with the right number of rows and a
  `covered` verdict over an empty `Covered by` cell is exactly the claim the check exists to refuse.
  Open the screen it names and find the state — and for a `PP-###`, open the FLOW and find the moment
  the actor stops experiencing that pain. A screen name in a pain point's `Covered by` is the subject
  coming up somewhere, not a journey fixing anything.
- **Leaving a stale check count after adding one.** The header, Part 5's heading, and every other
  place this file says how many checks there are must agree with the table's last row. A header
  claiming one number over a table holding another teaches the next run to stop early, and nothing
  fails — it just quietly never runs the checks that were appended. Grep the count before closing.
- **Passing checks 14-16 by eye.** "Actor: Admin" in a spec proves nothing on its own — open the UC
  and confirm that actor is really in its `## 1`, and open the `EN-###` and confirm the cardinality
  that put the screen in the `many` band. A scope table is exactly as trustworthy as the grounds in
  its last column, and a guessed `all` looks identical to a read one.
- **Counting a `many` screen as compliant because it has a filter.** Check 15 wants the find
  mechanism *and* all five volume states, with the real number named in the `many` one. A filter
  over a list whose only rendered state is three sample rows is machinery over nothing.
