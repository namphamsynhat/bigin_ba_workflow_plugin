# Stage 3 — Slice: cut each approved use case into stories

```text
runs: orchestrator for ≤ 2 features, else one worker per feature (references/agent-dispatch.md)
in:   each SLICE UC in full (§§ 1-6) + its BR-### files + the UX spec §§ 2-4 + SNAPSHOT.md
out:  the slice plan: stories with priority, slice_of, screens, rules, after — and the coverage matrix
never: writing a story file yet · inventing a path the use case does not have
```

Method: **Use-Case 2.0** (Jacobson) — a story is a slice of one use case, one or more paths through it that delivers
value — split with **SPIDR** (Paths, Interface, Data, Rules; Spikes become questions).

## Part 1 — Slice in this order

```text
1  MAIN PATH       S1…Sn of § 2, as ONE story, P1. The thinnest path that delivers the goal end to end.
                   Too big to estimate (> ~7 steps across > 3 screens)? Split on the INTERFACE seam
                   (screen groups) or the DATA seam (one kind of record first) — each part still ends
                   in something a user can see done.
2  ALTERNATIVES    each A# that is a different way to reach the goal → its own story, P2,
                   after: [main path story]
3  EXCEPTIONS      each E# that needs its own screen, its own decision, or its own record change
                   → its own story, P2/P3. An E# that only shows a message on the same screen →
                   FOLDED into its parent story as an acceptance criterion, not a story
4  RULES           a BR whose many cases would bloat one story (a pricing table, an eligibility
                   matrix) → one story per rule group, after: [the story that first applies it]
5  SPIKES          an unknown is NOT a story — it is a § 8 question on the story it blocks
```

Priority: P1 = the main path and anything without which the goal fails; P2 = alternatives and exceptions users
hit regularly; P3 = rare exceptions. A use case that states frequency or importance overrides this default — cite it.

## Part 2 — Per story, record

```text
title       what the user gets, active ("Book a free slot", "Join the waitlist when full")
role        the UC's primary actor (or secondary, for a reviewer's slice)
slice_of    "UC-<NNN> S1–S6", "UC-<NNN> A2", "UC-<NNN> E1" — exactly the paths it delivers
screens     the UX § 2 screens those steps run on (UX § 2 Serves column → S# lookup, never a guess)
rules       BR-### whose "Enforced at" lands on one of those steps
entities    EN-### the steps show or change
after       only a real dependency
folds       the E# flows folded in as acceptance criteria
```

## Part 3 — The coverage matrix

Every `S#`, `A#`, `E#` of every SLICE use case appears exactly once in the epic's § 7, mapped to the story that
delivers it (a folded `E#` maps to its parent story). A path deliberately left out — because the human said so in
the use case — says `out of scope — <cite>`. **No row may be blank.** A blank row means a path will not be built and
nobody will notice; Stage 5 blocks on it.

## Part 4 — INVEST check before writing

Per story: Independent (could ship without the next one — else merge or set `after:`), Negotiable, Valuable (a user
sees a difference), Estimable (no open unknown — else § 8), Small (one sitting to review), Testable (you can write
its independent test). Fail → re-slice now, not in Stage 5.

## Part 5 — Mint

Once the plan is final: `$BIGIN mint us --spec <json>` (`{title, epic, priority, slice_of, rules, screens, entities, after, snapshot}`) once per **new** story, in story-map order, in the orchestrator — it creates the file from the template and appends the id to the epic's `stories:`. A draft
story whose slice is unchanged keeps its id. Workers never mint.
