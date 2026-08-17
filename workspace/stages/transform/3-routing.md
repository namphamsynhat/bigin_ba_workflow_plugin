# Stage 3 — Routing: which lane a qualified signal goes down

```text
every signal that clears Stage 2 → EXACTLY ONE LANE
a signal genuinely belonging in two places was two signals → file the second half back as a question
```

**Route per CLAUSE, not per row.** A Signal Log row is a *theme* and can carry more than one signal — a
`Type` cell reading `requirement + constraint` says so outright. The behaviour clause goes down the UC
lane, the policy clause down the BR lane, and `Destination` lists both (`UC-012 S6 · BR-004`). What a
themed row must never do is get routed once on its dominant type, silently dropping its other clauses.
A clause with no lane is **reported**, not disappeared.

Routing decides **the artifact the signal becomes**. It is deliberately *not* a "new / update / design
/ feedback" split: `new` vs `update` is a lookup performed inside a lane, and `feedback` is a signal
`Type` that can land in any lane depending on what the feedback is about.

## The lane table

| The signal is… | Lane | Guide |
|---|---|---|
| a testable statement about system behaviour — a step a user takes, or what the system does back | **UC** | `3-lane-uc.md` |
| an end-to-end flow, including one crossing feature boundaries | **UC** (one UC, `features: []` listing each) | `3-lane-uc.md` |
| a conditional or policy constraint — feature-level, or governing one workflow | **BR** | `3-lane-br.md` |
| presentation only: look, layout, tone, visual style, copy voice, interaction feel, accessibility affordance | **Design** | `3-lane-design.md` |
| a thing the business tracks and its attributes — a data field or entity | **Entity** | § Entity — cite, never promote, below |
| narrative context — the client's stated why, not actionable alone | **Context** → the UC's `## 1` | `3-lane-uc.md` |
| a named frustration or cost with no requirement attached | **Context** → `PP-###` on the UC's `pain_points:` | `3-lane-uc.md` |

A `pain-point` with no attached requirement is **not a gap to fill**. It stays on record until a later
signal turns it into a flow step. Never stretch one into a step it does not support.

**There is no Scenario lane.** A cross-feature flow is a UC whose `features:` lists every slug it
touches — the retired `SCN-###` register was an approximation of exactly this, without actors, flows,
rules, or a review gate.

## `Type` is a hint, not a verdict

| `Type` | Usual lane | Watch for |
|---|---|---|
| `requirement` | UC, or Design if presentation-only | the boundary test below |
| `constraint` | BR, or Design if about look rather than policy | "under 3 seconds" is a BR; "must feel fast" is Design |
| `decision` | UC, as a settled statement of how it works | a `decision` has no `Why` — never manufacture one for the Business Need |
| `feedback` | whatever the feedback is *about* — UC if behaviour, Design if appearance | feedback on an approved UC still edits it in place |
| `problem` / `pain-point` | Context | never a stretched flow step |
| `question` / `concern` | **no lane** — already `Status: question` on the hub | do not draft from them |
| `answer` | route by what it answers, not its own type | it usually unblocks a `held` row |

## The design boundary test

The routing call most likely to drift, because the Design lane skips the PRD and the approval gate —
which makes it the cheap path, and cheap paths attract traffic that doesn't belong on them.

```text
DESIGN only if removing it would change how the feature LOOKS or FEELS, and not what it DOES

operational check: could a tester write a pass/fail assertion for this that never mentions
                   appearance?   yes → UC or BR, no matter how visual the client's phrasing
```

| Client said | Lane | Why |
|---|---|---|
| "the dashboard should feel warmer, less corporate" | Design | pure presentation |
| "use our brand colours" | Design (durable) | presentation, cross-cutting |
| "show status as coloured chips" | Design | presentation of data a step already defines |
| "ask for confirmation before deleting" | **UC** | adds a step and a state — testable without appearance |
| "show the approver's name next to each row" | **UC** | adds data to what a step displays |
| "tap targets must be at least 44px" | Design (durable) | accessibility affordance, no behaviour |
| "older users must complete this without help" | Design (durable) | a quality goal about the experience |
| "only a manager can approve" | **BR** | policy constraint |

A signal with **both halves** — "show the approver's name, and make it subtle" — is a UC step plus a
Design directive citing that step. Two destinations, one row's `Destination` cell.

**When the test is genuinely ambiguous, route to UC.** An over-routed step gets caught at the human
gate; an under-routed directive skips the gate entirely and quietly steers a prototype.

## Which UC — new or update

Decide by **reading**, never by how the signal is phrased. "We also need…" is not evidence a second UC
is warranted; most new signals are a step, branch, or rule inside a workflow that already exists.

```text
1  read the hub's `uc:` list — and, if the signal sounds cross-feature, the `uc:` lists of the other
   hubs it plausibly touches
2  open each listed UC and read its ACTUAL CONTENT: the goal in `title`, ## 1, and the flow
3  SAME GOAL   → update that UC in place, AT ANY STATUS
                 (approval does not freeze a UC, and neither does a shipped feature)
                 "same goal" = the same actor sitting down to accomplish the same thing
                 a new step, a new branch, a changed validation, a new rule are ALL updates
4  DIFFERENT GOAL → a new UC. Mint the next id by Grep over {uc_dir} for the highest number
                 (use the Grep TOOL, never a Bash pipeline — a denied pipeline silently reuses an id)
```

Two tests worth applying literally:

- **The boss test.** If nobody would sit down and do it as a unit of real work, it is not a UC — it is
  a step in one.
- **A feature can carry several UCs.** Four genuinely distinct user goals get four UCs, and that is
  correct rather than fragmentation. What it must not get is two UCs for one goal.

For a cross-feature UC, also decide **`primary_feature`** — the feature whose actor holds the goal.
That decides which subagent may write the file; every other participating feature is listed in
`features:` and gets a hub pointer in Stage 4.

## Durable vs. feature-scoped — the Design lane's lookup

```text
durable / cross-cutting  → brand, tone, accessibility, interaction, layout, content, platform
                           applies beyond the feature it was said about
                           destination: {design_principles_file}
feature-scoped           → this screen, this flow, this component
                           destination: the hub's ## Design Directives
stated about one feature but clearly generalizes → BOTH
```

**Check `{design_principles_file}` before adding a row.** `/extract-signal` already files durable design
constraints there at extraction time, so the row often exists and the correct action is to cite it.

## Entity — cite, never promote

`/extract-signal` already files a `proposed` row in `{entities_file}` the moment a signal describes a
data field or entity attribute — that row is what this lane cites. Match the signal against
`{entities_file}` and record the citation in the hub row's `Destination` cell (§ Recording the
routing decision, below). If no row exists for a signal that clearly describes one, that's an
extraction gap worth reporting, not backfilling here.

**Never promote a row to a full `EN-###` document, and never report one as a candidate for the
orchestrator to promote.** That lane doesn't exist in this skill any more — a `proposed` row stays a
row until `/approve-uc` promotes it, the first time an approved UC (or a `BR-###` it mirrors) is
actually confirmed to reference it (§ Entity Data Model). Deferring it that far means a UC that never
reaches approval never leaves behind an entity doc nobody ended up needing.

A UC or BR drafted or updated in this run may still cite the entity **by name** against the register
row — there is no `EN-###` id to cite yet, and minting one is not this skill's job.

## Recording the routing decision

The hub row's `Destination` cell — the column extraction deliberately leaves blank — records where the
signal went. A themed row lists every destination its clauses reached, ` · `-joined, and only reaches a
terminal `Status` once all of them are recorded.

| Lane | `Destination` | `Status` |
|---|---|---|
| UC | `UC-###`, or `UC-### S<n>` / `UC-### E<n>` when the target exists | `staged` (or `applied` if folded in on the interactive path) |
| BR | `BR-###` | `staged` |
| Design, durable | `DESIGN-PRINCIPLES #<n>` | `applied` |
| Design, feature-scoped | `<slug> ## Design Directives` | `applied` |
| Entity | `ENTITIES.md proposed` — never promoted here | `applied` |
| Context | `UC-### § 1` or `PP-###` | `applied` |

Design, Entity, and Context are `applied` on write because nothing about them is staged behind a gate —
the gate exists to protect UC/BR content from entering approved scope unreviewed, and none of these
enter it. Entity's `applied` marks the *citation* as done, not the entity as modelled — the row still
waits on `/approve-uc` for that.
