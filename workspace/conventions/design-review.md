# Design Conventions — the flow review and the relationship model

The built-in flow review, and the `## 7` relationship model the few features that earn one carry.

**Read by** design stages 4 and 6.

## The flow review

`4-flow-review` — a pass over the flows and the navigation **as a whole**, after every screen exists
and before coverage is verified. It is the only stage that looks at the product the way a user meets
it: not "is this screen grounded?" but "does this journey make sense, and does it fix what the client
said hurt?"

**It runs every time, unconditionally, on the built-in walk** (`4-flow-review.md` Parts 1-4) — no
skill to detect, nothing to skip. A deeper, corpus-backed critique (perception-first-design or
similar) is a separate, manual step a human reaches for after `/bigin-render-design-od` has produced
a rendered artifact — that kind of tool is built to evaluate a live artifact, not a markdown spec, and
it is never invoked from inside this pipeline.

### What it may change, and what it may only ask

```text
MAY CHANGE, in place        the flow's screen ORDER · which screen an interaction leads to · a nav
                            entry's placement or nesting · a screen's element ORDER · copy that
                            misleads · a state a flow reaches but no screen declared
                            → every one of these is still GROUNDED (`design-grounding.md` § Grounding) and changelogged

MAY ONLY ASK (## 6)         a screen that should exist and does not · a field, capability, or state
                            nothing grants · a pain point the flows cannot fix as specified · a
                            requirement gap of any kind
                            → the fix is a 3-screens dispatch next run, or /bigin-transform-signal.
                              A review pass that draws the missing screen has stopped reviewing
```

The line is the same one `5-verify` holds: **repair what is already decided; ask about what is not.**
The difference is direction — this pass repairs the *journey* between screens, `5-verify` repairs the
*bookkeeping* about them.

### The verdicts

Each flow gets one row in the UX spec's `## 5 Navigation & Flow Review`:

```text
sound                        the journey works as specified, and its pain point is fixed where the
                             row says it is
improved — <what changed>    the pass reordered, re-pointed, or re-worded something. Say what, in a
                             phrase, so a human can diff it against what they last read
gap → ## 6 Q<n>              the journey does not work and the fix is not this pass's to make
```

## The relationship model

`## 7 Relationship Model` on a UX spec. **Conditional** — it exists only on a feature that passes the
relationship trigger (`3-screens.md` Part 4b). Most features never get one, and an *empty* one is
worse than none: it reads as "the relationship was considered and there isn't one" when nobody looked.

It exists because one thing an agent feature's design must say has nowhere else to live:

```text
a STATE        within ONE session    empty · loading · error · success        → ## 3, per screen
a TRUST STAGE  across MONTHS         what the agent shows, suggests, or does  → ## 7
                                     alone at relationship month 1 vs 12
```

`## 3`'s `States` table is within-session by construction. A screen that discloses its full reasoning
to a new user and acts quietly for a year-old one is not in two states — it is the same state at two
points in a relationship, and squeezing that into `States` produces a spec that reads as a bug.

### The three parts, and what grounds each

| Part | Rows | Grounded by |
|---|---|---|
| **Relationship Context** | expected duration · interaction frequency · the autonomy **ceiling** · memory sensitivity | a UC's trigger/post-conditions, a BR, an active DESIGN-PRINCIPLES row, or a hub directive |
| **Memory Architecture** | what the agent carries between sessions · where that lives · who can see, correct, or clear it | **an `EN-###` field, always.** A system cannot remember what nothing stores |
| **Trust Map** | per screen or per agent decision: what stage 1 / 2 / 3 shows vs does, and the correction path | a `BR-###` about who may do this, a confidence or threshold rule, or a UC exception flow |
| **Proposed Measures** | at most **three**, each naming what would be observed and which row above it tests | owner: **team**. Never a requirement, never a screen |

### The rules that make this safe

```text
a Memory Architecture row with no EN-### field behind it   → a REQUIREMENT GAP, not a design row.
                                                             The field is the design's only evidence
                                                             the memory exists at all.
an autonomy stage no BR-### granted                        → a REQUIREMENT GAP (D7). Design may
                                                             describe how autonomy is DISCLOSED;
                                                             it never decides that it exists.
a retention or forgetting rule nothing stated              → a REQUIREMENT GAP. "The user can clear
                                                             their history" is a behaviour promise.
a Proposed Measure                                         → stays a measure. It never licenses a
                                                             screen, a field, or an event to track —
                                                             instrumentation is behaviour too.
a memory, goal, or trust SCREEN from a pattern catalog     → 2b alone (`design-grounding.md` § Grounding). Not a ground.
```

The gaps are the point. A UC almost never states an autonomy ceiling, a retention rule, or who owns
the memory — so a well-run relationship model on a real agent feature produces **more requirement
gaps than design rows**, and that is the section working, not failing. `/bigin-transform-signal` owns
every one of them; this stage writes none of them onto a UC (D4).

### What this section is not

```text
NOT a persona            the UCs already carry actors. Never invent a user to have a relationship with.
NOT an architecture      no schema, no storage design, no retention implementation. A field name and
                         an owner, nothing past that.
NOT a metrics plan       three proposed measures, team-owned. Dashboards, instrumentation, and
                         targets are product work happening somewhere else.
NOT a reason to add      it describes the relationship the requirements already imply. It never
    screens             discovers that the product needs a memory dashboard.
```
