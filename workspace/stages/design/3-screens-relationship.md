# Stage 3, Part 4b continued — writing `## 7`, on a feature that passed the trigger

```text
runs: the screens worker, ONLY when 3-screens.md Part 4b's trigger test passed 3 of 3
in:   the worklist's entities (their fields), the rule mirrors, the UC triggers
out:  ## 7 Relationship Model — and, usually, more requirement gaps in ## 6 than rows
```

Read `design-review.md` § The relationship model first.

### What you write, and what grounds it

Four sub-blocks (the template carries the tables). Every row is grounded per `design-grounding.md` § Grounding or it is
not a row:

```text
Relationship Context   duration · frequency · the AUTONOMY CEILING · memory sensitivity
                       ← a UC trigger/post-condition, a BR, an active principle row, a directive
                       "not stated" is a real value → a requirement gap in ## 6. Never a plausible
                       number: "users return weekly" invented here becomes a fact downstream.

Memory Architecture    what it carries between sessions · WHICH EN-### FIELD holds it · which
                       screen surfaces it · who may see, correct, or clear it
                       ← the entity field, ALWAYS. No field → not a row, a requirement gap.

Trust Map              per screen or per agent decision: what it SHOWS vs what it DOES at stage 1
                       (transparent) / 2 (selective) / 3 (autonomous), and the correction path
                       ← a BR about who may do this, a confidence/threshold rule, or an E-flow
                       Only fill a stage a BR actually GRANTS (D7). An unfilled stage 3 is the
                       correct answer when nothing granted autonomy.

Proposed Measures      at most THREE, owner team, each naming what would be observed and which row
                       above it tests. Never a requirement, never a target, never a screen.
```

A trust stage is **not** a state. `## 3`'s States table is within one session (empty, loading,
error, success). A trust stage is the same screen at relationship month 1 versus month 12 — put it
in `## 7` and, where it changes what a screen shows, note the stage next to that element in `## 3`.

### The guardrail — this is where an agentic run goes wrong

An installed relationship-UX skill hands you a pattern catalog: memory dashboards, goal dashboards,
planning canvases, preference-evolution maps, contextual timelines. Those are **whole screens**, and
they arrive with a citation, which makes an invented screen look designed.

```text
an external pattern is ground 2b (`design-grounding.md` § Grounding) — it shapes HOW something already grounded is built.
it can NEVER ground THAT a screen, field, or state exists.

"the relationship-UX skill recommends a memory dashboard"     → not a ground. Not a screen.
"UC-014 S3: the reviewer checks what the assistant learned"    → a ground. Now design that screen,
                                                                 and use the catalog for its shape.
```

Same test as Part 2's: **never invent a screen the flow never asked for**, however good the pattern.

### The gaps are the deliverable

A UC almost never states an autonomy ceiling, a retention rule, or who owns the memory. So a real
agent feature produces **more requirement gaps here than design rows** — that is this section
working, not failing. Each one goes in `## 6`, marked `requirement-gap`, and belongs to
`/bigin-transform-signal`. Write none of them onto the UC (D4).

The recurring five, all requirement gaps whenever unanswered:

```text
what may the agent do WITHOUT asking, and above what confidence?   → autonomy. A BR, or a gap.
how long is this remembered, and can the user clear it?            → retention. A BR, or a gap.
who else can see what it learned about this user?                  → visibility. A BR, or a gap.
what happens when it is WRONG — who is accountable, what is undone? → an E-flow, or a gap.
does the user know it is learning from them?                        → disclosure. A BR, or a gap.
```
