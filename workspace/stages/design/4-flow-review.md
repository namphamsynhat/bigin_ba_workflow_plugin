# Stage 4 — Flow review: does the journey make sense, and does it fix what hurt?

```text
runs: orchestrator, inline, after EVERY Stage 3 worker has reported and BEFORE 5-verify
gate: ONLY when a perception-first-design skill (or a generic critique skill) is installed.
      Not installed → SKIP, silently, report the install line, continue. Nothing here halts.
in:   each UX spec ON DISK (never a worker's report) · {nav_map_file}'s ## Structure
      · each feature's open ## Pain Points rows
out:  a `### Flow Review` table in each spec's ## 5 · flows reordered or re-pointed IN PLACE
      · nav entries re-nested · new ## 6 questions for what this pass may not fix
never: a new screen · a new field · a new capability · a requirement edit · a status (Stage 6 owns it)
       · a verdict on a flow this run did not touch
```

Read `{design_conventions}` § The flow review, § User flows and pain points, § The navigation map,
§ Grounding, and § Open questions first.

This is the only stage that looks at the product **the way a user meets it**. Every other check in
this pipeline is per-artifact: is this element grounded, does this id resolve, does this cell say what
the file beside it says. None of them can see that a four-screen journey delivers the same outcome a
two-screen one would, that the flow's success screen is a dead end, or that the pain point the client
actually complained about is untouched by every screen designed to fix it.

---

## Part 0 — The gate

```text
a perception-first-design skill is installed        → run this stage (Part 5 is its method)
a generic critique skill is installed instead       → run this stage on the built-in method
                                                      (Parts 1-4), and use the critique skill for
                                                      Part 5 in whatever shape it offers
NEITHER is installed                                → SKIP THE WHOLE STAGE.
                                                      Write NO ### Flow Review table.
                                                      Do NOT leave an empty one — an empty table
                                                      reads as "reviewed, nothing found".
                                                      Report `flow review: skipped — not installed`
                                                      plus ONE install line, and continue to
                                                      5-verify.
```

**The gate is deliberate, and it is not laziness.** A flow critique run without a method is a
paragraph of plausible opinion that lands in the spec as a `sound` verdict, and a `sound` verdict is
the strongest claim this pipeline makes about a journey. A skipped review says "nobody looked", which
is true and recoverable. A faked one says "somebody looked and it was fine", which is neither.

Detection, the install line, and how to drive the installed skill: `method-layer.md` § Stage 4.

---

## Part 1 — Walk each flow, as the actor

Per UX spec designed this run, per `## 4 Flows` entry. Read the flow, then read the `## 3` block of
every screen on its `Path`. Walk it in order and answer five questions:

```text
1  DOES IT ARRIVE?      does the Path actually end where `Success` says it does, and does every
                        `Failures` line land on a screen or state that really exists in ## 3?
                        A flow ending on a screen nothing declares is a dead end the client meets
                        for the first time in a prototype.

2  IS EVERY STEP EARNED? per screen on the Path: what does the actor do here that they could not
                        have done on the screen before or after it? A screen the actor passes
                        through without acting is a step in the count and nothing in the journey.
                        `Steps to goal` is where this shows: two flows delivering comparable
                        outcomes at 2 and 6 screens is the signal, not the number itself.

3  CAN THEY GET BACK?    from every screen on the Path, is there a way back to the previous one and
                        out to somewhere in the nav shell? A wizard step with no exit and a detail
                        screen with no route back are the two that reach a client most often.

4  DOES IT START WHERE   the flow's `Entry` is a trigger in plain words. Is the FIRST screen on the
   THE ACTOR IS?         Path reachable from {nav_map_file}'s ## Structure, or from a screen that
                        is? An entry point reachable only by knowing the URL is not an entry point.

5  DOES IT FIX THE       for each PP-### in `Resolves`: name the screen AND the moment in the journey
   PAIN POINT?           where the actor stops experiencing that pain. "The queue is sorted by date"
                        is not an answer to "reviewers can never find what they were working on
                        yesterday" unless something on that screen actually surfaces yesterday's
                        work.
```

Question 5 is the one this stage exists for. The other four are hygiene a careful reader would catch;
question 5 is the one nobody catches, because a flow that delivers every UC step reads as complete
whether or not it makes the client's day better.

---

## Part 2 — Walk the navigation, as a stranger

Once per run, not per feature — the shell is vault-wide. Read `{nav_map_file}`'s `## Structure`
whole, alongside every screen inventory this run touched:

```text
□ every entry's `Points to` names a screen that really exists in some UX spec
□ every top-level entry is something an actor would look for by that NAME — a label nobody in the
  flows uses is an invented vocabulary, however tidy the tree looks
□ no two entries reach the same screen (two doors, and they drift the first time one path changes)
□ every screen that a flow's `Entry` starts on is reachable: it has an entry, or the screen that
  opens it does
□ nesting depth matches how the actor thinks, not how the features are filed — a destination three
  levels down that a flow reaches on every run belongs higher, and a `PP-###` about finding things
  is a citation for saying so
□ on `mobile`: at most 5 top-level entries, and the five are the five things actors do most, judged
  against the flows — not the five features that happened to be designed first
□ on `both`: each shell is judged on its own. An entry the web sidebar carries and the phone does
  not is normal; the check is that each tree works, not that they match
```

**A re-nest is the one structural change this pass makes** — and it is still append-only (D1). Moving
`reports` under `settings` means: add the new row at `settings.reports`, retire the old `reports` row
in § Removing an entry with `re-nested to settings.reports` as its reason, and update the `## 5`
Navigation rows of every spec citing the old id. Never edit an `id` in place; every screen spec
citing the old path would silently point at nothing.

---

## Part 3 — Fix what is already decided; ask about the rest

The same line `5-verify` holds, applied to journeys instead of bookkeeping.

```text
FIX IN PLACE — every one still grounded (§ Grounding), every one changelogged:
    the ORDER of screens in a flow's Path
    which screen or state an ## 3 Interactions row leads to
    the ORDER of elements inside a screen's element table
    a nav entry's placement, nesting, or sibling order
    copy that misleads about what a control does
    a state a flow plainly reaches that the screen's States table failed to declare
      → ONLY when a BR, an exception flow, or an entity constraint already grounds it. A state
        nothing grounds is a question, exactly as it was in Stage 3

ASK IN ## 6 — never fix:
    a screen that should exist and does not
    a field, a capability, an export, a bulk action nothing grants (D8)
    a pain point the flows cannot resolve as the requirements stand
    a flow whose `Steps to goal` is high because the REQUIREMENTS make it so — that is not a design
      problem, and shortening it would drop a step a BR requires
    anything that would change what the system DOES → a requirement gap, owner: client
```

**Drawing the missing screen here is the failure that costs most.** The pass then has no independent
verdict left: it graded the thing it just built. The question goes in `## 6`, the screen comes from
`3-screens` next run, and the flow keeps its `gap` verdict in the meantime — which is exactly the
signal a human reviewing this spec needs to see.

---

## Part 4 — Write the `### Flow Review` table

Under `## 5 Navigation & Flow Review`, in each spec this run designed, re-written **whole** every run:

```markdown
### Flow Review
<!-- Written by Stage 4 (4-flow-review.md). One row per ## 4 flow. Verdicts: `sound` |
`improved — <what changed>` | `gap → ## 6 Q<n>`. Nothing else. -->

| Flow | Actor | Steps to goal | Resolves | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| Submit a request | Requester | 3 | PP-002 | sound |
| Review the queue | Reviewer | 4 → 2 | PP-004 | improved — queue opened straight to in-progress; two confirm screens merged |
| Reassign a request | Reviewer | 2 | — | gap → ## 6 Q3 |
```

```text
sound                        the journey works, and its pain point is fixed where the row says.
                             Naming a PP-### in `Resolves` and giving `sound` without having found
                             the moment it is fixed (Part 1 Q5) is the one dishonest cell here
improved — <what changed>    say WHAT, in a phrase. A human diffs this against what they last read;
                             "improved — reviewed and adjusted" tells them nothing and they re-read
                             the whole spec to find out
gap → ## 6 Q<n>              points at a question that really exists and is unchecked
```

`Steps to goal` shows the change when there was one — `4 → 2` — and the single number when there was
not. A flow this pass did not touch keeps its Stage 3 number, unchanged.

**Then update `## 4 Flows` itself.** A reordered Path, a re-pointed failure end, a merged pair of
screens: the flow section is the record, and the review table is the note about what happened to it.
A verdict of `improved` over an unchanged `## 4` is a claim with nothing behind it.

---

## Part 5 — The installed skill's own pass

Everything above is the built-in walk, and it runs whichever skill gated this stage. Part 5 is where
the installed skill contributes its own method, on the flows and screens **this run drafted** and
nothing else.

Read `method-layer.md` § Stage 4 for which modes to use and which to refuse. The short version, for
perception-first design specifically:

```text
Mode 1  evaluate / checklist    walks an artifact against the 5 layers, flags what fails   ← use this
Mode 2  solve / derivation      generates a solution FROM the 5 layers, bottom-up          ← never
Mode 3  analyze                 predicts consequences of a hypothetical change             ← never
```

Modes 2 and 3 **produce** something — a solution, a predicted consequence — from psychology alone,
with no UC, BR, entity, or pain point in the loop. That is precisely the ungrounded design call D3
exists to catch, wearing a citation. The checklist walks what is already there.

Sort every finding the same way Part 3 does:

```text
a finding about ORDER, EMPHASIS, WORDING, or DENSITY   → Part 3's fix-in-place list. Apply it, cite
                                                         the layer, changelog it
a finding that would ADD, REMOVE, or REORDER something → back through the grounding test:
the requirements never asked for                         grounded → apply it and cite the ground
                                                         ungrounded → a ## 6 question, same as any
                                                                      other ungrounded decision
```

**A checklist finding is never a fourth ground.** "The audit flagged it" does not license a screen, a
field, a state, or a capability — it is ground 2b at best (`{design_conventions}` § Grounding), which
shapes how a grounded thing is built and grounds nothing on its own.

Run it **at most once per flow per run**. A pass re-critiquing its own fixes in a loop is scope creep
wearing a quality label.

---

## Part 6 — Report to Stage 6

```text
Stage 4:   <slug> UX-### — <N> flow(s) reviewed: <N> sound, <N> improved, <N> gap(s)
                  <N> pain point(s) confirmed resolved, <N> not resolved (question raised)
                  nav: <N> entr(y/ies) re-nested | none · <N> question(s) raised
           method: <pfd (mode 1) | <critique skill> | SKIPPED — not installed>
```

A run where every flow came back `sound` reports that, and it is a real result worth printing — not
silence. Silence reads as "the pass did not run", which is the one thing this report has to
distinguish from a genuine skip.

## Failure modes

- **Running this stage with no method installed.** The table lands in the spec claiming every journey
  was reviewed, `sound` becomes the vault's strongest claim about a flow, and nobody ever looks
  again. A skip is recoverable; a fabricated review is not.
- **Leaving an empty `### Flow Review` table on a skip.** It reads as "reviewed, nothing found" —
  the same false claim, with the effort of writing a heading. Write no table at all.
- **Designing the missing screen here.** The pass grades what it just built and has no independent
  verdict left. The question goes in `## 6`; the screen comes from `3-screens` next run.
- **Giving a flow `sound` without finding the moment its pain point is fixed.** Part 1 Q5 is the
  whole reason this stage exists. A flow that delivers every UC step and touches nothing the client
  complained about is exactly the design that reviews well and disappoints in the room.
- **Writing `improved — reviewed and adjusted`.** A human diffs the phrase against what they last
  read. A verdict with no content in it costs them the whole spec.
- **An `improved` verdict over an unchanged `## 4 Flows`.** The review table is a note about what
  happened to the flows; if nothing happened to them, nothing was improved.
- **Editing a nav entry's `id` in place to re-nest it.** Every screen spec citing the old path now
  points at nothing, and D1's whole record of why the IA looks the way it does is gone. Add the new
  row, retire the old one, update the citations.
- **Shortening a flow the requirements made long.** A five-step approval a BR requires is five steps.
  Cutting one is a design deciding what the system does — and the step reappears in the build, after
  the client approved a journey that did not have it.
- **Letting a checklist finding ground a new screen or field.** Ground 2b at best. An invented screen
  arriving with a psychology citation reviews as designed where a bare guess would have been caught.
- **Reviewing flows this run did not touch.** A `CURRENT` feature's journeys were reviewed when they
  were designed; re-opening them now re-raises questions a human already closed and reports a feature
  going backwards.
- **Running the pass twice on the same flow.** The second pass critiques the first pass's fixes,
  which is a loop with a quality label on it, not a second opinion.
