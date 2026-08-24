# Stage 4 — Verify: does the design cover what the requirements actually say?

```text
runs: orchestrator, inline, after EVERY Stage 3 worker has reported and BEFORE Stage 5 writes a block
in:   each UX spec ON DISK (never a worker's report) + the in-scope UCs' step/flow ids + the BR-###
      they cite + the EN-### fields those steps touch + open hub directives + active principles
out:  a `### Coverage` table under each spec's `## 4 Flows` · repaired spec rows · new `## 6`
      questions for what is genuinely not designed
never: a new screen · a new state · a new field · a requirement edit · a status (Stage 6 owns it)
```

This is the **forward** direction, and it is the only stage that runs it: **every requirement item →
the screen that carries it.** Stage 3's grounding test and Stage 6's checks already run the *backward*
direction — every screen element back to a ground — and that direction cannot find a miss, because a
screen that was never drawn has no element to trace. A spec can pass every one of Stage 6's checks
with a whole exception flow missing: each thing on it is properly grounded, nothing on it is invented,
and the flow the client cares about is simply not there. That is the failure this stage exists for.

**It repairs, it does not design.** An item nothing covers is one of three things, and the difference
is the whole judgment here: a screen that really does carry it and whose row failed to say so
(→ fix the row), something genuinely not designed (→ a `## 6` question), or something deliberately out
of scope (→ a `## 6` line citing what put it out). Drawing the missing screen is Stage 3's job, and a
verify pass that starts designing has stopped verifying.

## Part 1 — Build the requirement item list, by id, not by body

Do **not** re-read the in-scope UCs in full — Stage 3's workers already did, and a second full read in
the orchestrator is the context this pipeline fans out to avoid. `Grep` the ids and their one-line
text:

```text
per feature designed this run, per in-scope UC (the ones on the Stage 1 work-list as NEW | CHANGED):

  steps       {uc_dir}/UC-### …  ## 2 Main Success Scenario   → every S# row NOT marked removed
  flows       same file          ## 3 Alternative & Exception  → every A# / E# row NOT marked removed
  rules       every BR-### those rows cite that constrains WHAT THE ACTOR SEES OR MAY DO
              (a purely back-office calculation rule constrains no screen — say so once, in the
               verdict cell, rather than listing every one)
  fields      every EN-### field a step READS or WRITES — not every field the entity owns. An entity
              with forty fields whose flow touches four contributes four rows
  directives  the owning hub's ## Design Directives rows still at Status: open
  principles  {design_principles_file} rows still `active`
```

A **removed** step or flow contributes no row: it is not a gap, it is a step that no longer exists.
A UC the work-list marked `CURRENT` contributes no row either — its coverage was verified the run that
designed it, and re-verifying it here would re-open questions a human already closed.

## Part 2 — Match each item against the spec on disk

Read the UX spec's `## 2 Screen Inventory` (its `Serves` column), `## 3`'s screen specs (regions,
elements, States, Interactions), and `## 4`'s flows. Match by **id**, never by resemblance: a screen
whose `Serves` cell says `UC-003 S4` covers `S4`; a screen that merely looks like it would is not a
match, and treating it as one is how a step gets signed off unbuilt.

```text
item found in Serves / a State / an element               → covered
item plainly IS on a screen, but no row says so           → REPAIR the row, then covered
item is nowhere on any screen of any spec this run        → not designed
item is excluded by something ON RECORD                   → out of scope, and cite what excluded it
```

**The repair is narrow and it is the orchestrator's.** Add the missing `S#`/`A#`/`E#` to a `Serves`
cell, name the `BR-###` behind a state that already exists, add an entity field to an element list
that already renders that entity. That is bookkeeping a worker under-recorded. It is **not** a repair
to add a state, a screen, an element, or a control — those are new design, and new design is a Stage 3
dispatch on the next run, never an edit made here (D3).

## Part 3 — What a real gap becomes

```text
not designed, and the answer is a DESIGN call
    → - [ ] Q: <what is not designed, in plain business words> (owner: team) (ref: UX-###)
      e.g. "The flow for a payment that fails after the record was created has no screen — which
      screen does the actor land on, and what can they do from there?"

not designed, and the answer would change WHAT THE SYSTEM DOES
    → the same line, marked as a REQUIREMENT GAP, owner: client
    → /bigin-transform-signal resolves it. NEVER written onto the UC here (D4) — Stage 6 Part 4's
      one ## Discussion line is the only thing this skill ever puts on a UC

out of scope
    → NOT a question. A `## 6` line stating the exclusion and citing what stated it:
      "EN-002.tax_id is not shown on any member screen — hub ## Design Directives #2."
    → an exclusion with nothing citable behind it is NOT out of scope. It is a gap, and writing it
      as an exclusion is how a field the client expected to see disappears with an explanation
      nobody made
```

One question per item, and check `## 6` and the UC's own `## 5` before adding it — a question already
open somewhere is mirrored, never re-asked (Stage 6 check 6).

## Part 4 — Write the `### Coverage` table

Under `## 4 Flows`, in each spec this run designed, re-written **whole** every run — a partial table
claims a coverage that was never checked:

```markdown
### Coverage
<!-- Written by Stage 4. Every in-scope requirement item, matched forward to what carries it.
Verdicts: `covered` | `gap → ## 6 Q<n>` | `out of scope — <cited reason>`. Nothing else. -->

| Item | Kind | Covered by | Verdict |
| :--- | :--- | :--- | :--- |
| UC-003 S4 | step | Member Record · Editing | covered |
| UC-003 E2 | exception | — | gap → ## 6 Q1 |
| BR-014 | rule | Member Record · Locked | covered |
| BR-021 | rule | — | out of scope — back-office calculation, no screen surface |
| EN-002.tax_id | field | — | out of scope — hub ## Design Directives #2 |
| directive #3 | directive | Member Directory · filter bar | covered |
| principle #1 | principle | all screens — single accent | covered |
```

`Covered by` names the **screen and the state**, not just the screen: a step served only in an error
state and a step served on the default view are different coverage, and a bare screen name hides the
difference. An item with a `covered` verdict and a `—` in `Covered by` is a contradiction, and Stage 6
check 18 blocks on it.

## Part 5 — Render readiness: is the spec enough input for a render?

Rendering is `/bigin-render-design`'s job and runs whenever a human chooses, possibly weeks later and
on whichever engine they pick. So the spec has to stand on its own as that engine's input **now**,
while the material is still in hand. Per screen, per spec:

```text
□ REGIONS in this platform's vocabulary — web header/nav/main/aside/footer ·
  mobile header/content/tab-bar/sheet/fab. A render engine builds the shell the regions name
□ ELEMENTS carry REAL COPY and REAL FIELD NAMES — the actual words, the actual EN-### fields, enum
  values spelled out. No `Lorem`, no `<label>`, no "the usual fields"
□ every STATE the screen reaches is named and described — default, empty, loading, error, and each
  rule-driven one. An engine renders the states it is given and no others
□ every TOKEN a screen cites exists in {tokens_file} WITH A VALUE — a name alone makes the engine
  pick its own colour
□ the NAV SHELL this screen sits in is resolvable from {nav_map_file}'s ## Structure for this
  platform — an engine with no shell improvises one per screen
□ a `many` screen names its REAL SCALE in words ("about 10,000 records, page 1 of 200") and carries
  its find mechanism. An engine given no scale renders three placeholder rows
□ a mobile (or `both`) screen carries its device facts — 390px frame, safe-area insets, 44×44 tap
  targets, one primary action, sheets rather than modals
□ `relationship_model: modelled` → ## 7's memory rows are concrete enough to render as a real
  variant rather than static text (D7)
```

A box that cannot be ticked is a **spec** gap, so it is fixed here the same way Part 2's repairs are:
fill what is already decided and on record, and raise a `## 6` question for what is not. Never invent
copy, a state, or a scale to make a box tick — a render that came back looking finished off invented
input is the failure this whole pass exists to prevent, arriving one stage later.

## Part 6 — Report to Stage 6

```text
Stage 4:   <slug> UX-### — <N> items checked: <N> covered, <N> gap(s), <N> out of scope
                  <N> row(s) repaired · <N> question(s) raised (<N> requirement gap)
                  render-ready: yes | <N> input gap(s) raised
```

A feature whose every item is `covered` reports `0 gaps` — and that is a real result worth printing,
not silence. Silence reads as "the pass did not run".

## Failure modes

- **Running only the backward direction.** Every screen traces to a ground, every check passes, and
  the exception flow nobody drew is still missing. Backward proves nothing was invented; only forward
  proves nothing was dropped, and a design review catches the invention long before it catches the
  omission.
- **Matching by resemblance instead of by id.** A screen that "obviously handles that" gets an `S#`
  it never served, the step reports as covered forever, and the build discovers it.
- **Designing the missing screen here.** The pass then has no independent verdict left: it drew the
  thing it was checking for. The gap goes in `## 6`, and the screen comes from Stage 3 next run.
- **Turning a gap into an out-of-scope line with no citation.** It reads as a decision. A field the
  client expected then disappears with an explanation nobody made, and the exclusion outlives every
  person who could contradict it.
- **Listing every field of every cited entity.** A forty-field entity whose flow touches four
  produces thirty-six false gaps, the table becomes noise, and the four real ones stop being read.
- **Re-verifying a `CURRENT` UC.** It re-opens questions a human already closed, and the run reports
  a feature going backwards.
- **Writing the gap onto the UC.** D4. The requirement gap goes in `## 6` and is mirrored on the hub;
  `/bigin-transform-signal` is what touches a UC.
- **Skipping Part 5 because nobody is rendering today.** The render happens on a human's schedule,
  from a spec written by a run whose context is gone. Every input missing now is missing then, and
  the engine fills it with something plausible.
- **Ticking a Part 5 box by inventing the input.** Placeholder copy, a guessed scale, an invented
  state: all three make the checklist pass and all three reach the client inside a rendered prototype
  that looks specified.
- **Writing a partial `### Coverage` table.** It claims a coverage nobody checked. Re-write it whole,
  every run, the same rule `absorbed:` follows.
