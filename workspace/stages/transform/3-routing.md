# Routing — which lane a qualified signal goes down

Every signal that clears Stage 2 goes down exactly one lane. A signal that genuinely belongs in two
places was two signals and should have been split at extraction — file the second half back as a
question rather than routing one row twice.

**A Signal Log row is a theme, and can carry more than one signal** (`conventions.md` § Feature
Hub) — a `Type` cell reading `requirement + constraint` says so outright. Route **per clause**, not
per row: the behaviour clause goes down the UC lane, the policy clause down the BR lane, and the
row's `Destination` cell lists both (`UC-012 S6 · BR-004`). That is not the same as routing one signal
twice — each clause is its own signal, filed together because a drafter writes them together. What a
themed row must never do is get routed once on its dominant type, silently dropping its other
clauses; if a clause has no lane, say so in the report rather than letting it disappear.

Routing is a decision about the **artifact the signal becomes**, which is the axis
`conventions.md` § Signal → artifact mapping already defines. It is deliberately *not* a
four-way "new requirement / requirement update / design / feedback" split: `new` vs `update` is a
lookup performed inside a lane, not a property of the signal, and `feedback` is a signal `Type`
that can land in any lane depending on what the feedback is about.

## The lane table

| The signal is… | Lane | Guide |
|---|---|---|
| A testable, actionable statement about system behaviour — a step in what a user does, or what the system does back | **UC** | `3-lane-uc.md` |
| An end-to-end flow, including one that crosses feature boundaries | **UC** (one UC, `features: []` listing each) | `3-lane-uc.md` |
| A conditional or policy constraint — feature-level, or governing one workflow | **BR** | `3-lane-br.md` |
| A statement about presentation only: look, layout, tone, visual style, copy voice, interaction feel, accessibility affordance | **Design** | `3-lane-design.md` |
| A thing the business tracks and its attributes — a data field or entity | **Entity** | `3-lane-entity.md` |
| Narrative context — the client's stated why, not actionable on its own | **Context** → the UC's `## 1` Business Need / Goal | `3-lane-uc.md` |
| A concrete named frustration or cost, with no requirement attached | **Context** → the `PP-###` id on the UC's `pain_points:` | `3-lane-uc.md` |

A `pain-point` with no attached requirement is not a gap to fill. It stays on record until a later
signal turns it into a flow step or a story resolves it. Never stretch one into a step it does not
support.

**There is no Scenario lane.** A cross-feature flow is a UC whose `features:` lists every slug it
touches — the retired `SCN-###` register was an approximation of exactly this, and a UC carries the
actors, flows, rules, and review gate it never had (`conventions.md` § Business Scenarios (retired)).

## Reading the signal's `Type` as a hint, not a verdict

Extraction typed each row (`requirement · constraint · decision · feedback · question · answer ·
concern · problem · pain-point`). That type narrows the lane but does not pick it:

| `Type` | Usual lane | Watch for |
|---|---|---|
| `requirement` | UC, or Design if presentation-only | The design boundary test below |
| `constraint` | BR, or Design if it is about look rather than policy | "Must be under 3 seconds" is a BR; "must feel fast" is Design |
| `decision` | UC (as a settled statement of how it works) | A `decision` has no `Why` — do not manufacture one for the UC's Business Need |
| `feedback` | Whatever the feedback is *about* — UC if it changes behaviour, Design if it changes appearance | Feedback on an approved UC still edits it in place (hard rule 7) |
| `problem` / `pain-point` | Context | Never a stretched flow step |
| `question` / `concern` | No lane — these are already `Status: question` on the hub | Do not draft from them |
| `answer` | Route by what it answers, not by its own type | It usually unblocks a `held` row rather than becoming one of its own |

## The design boundary test

This is the routing call most likely to drift, because the Design lane skips the PRD and the
approval gate — which makes it the cheap path, and cheap paths attract traffic that does not belong
on them. Apply the test literally.

**A signal is Design only if removing it would change how the feature looks or feels, and not what
it does.**

The operational check: *could a tester write a pass/fail assertion for this that never mentions
appearance?* If yes, it is UC or BR, no matter how visual the client's phrasing was.

| Client said | Lane | Why |
|---|---|---|
| "The dashboard should feel warmer, less corporate" | Design | Pure presentation |
| "Use our brand colours" | Design (durable) | Presentation, and cross-cutting |
| "Show status as coloured chips" | Design | Presentation of data a step already defines |
| "Ask for confirmation before deleting" | **UC** | Adds a step and a state to the flow — testable without appearance |
| "Show the approver's name next to each row" | **UC** | Adds data to what a step displays |
| "Tap targets must be at least 44px" | Design (durable) | Accessibility affordance, no behaviour |
| "Older users must be able to complete this without help" | Design (durable) | A quality goal about the experience, not a behaviour |
| "Only a manager can approve" | **BR** | Policy constraint |

When a signal has both halves — "show the approver's name, and make it subtle" — the behaviour half
is a UC step and the presentation half is a Design directive citing that step. Two destinations, one
signal, both cited from the same Signal Log row's `Destination` cell.

**When the test is genuinely ambiguous, route to UC.** An over-routed step gets caught at the human
gate; an under-routed design directive skips the gate entirely and quietly steers a prototype.

## Which UC — new or update

Inside the UC lane, decide new-vs-update by **reading**, never by how the signal is phrased. A client
saying "we also need…" is not evidence that a second UC is warranted; most new signals are a step, a
branch, or a rule inside a workflow that already exists.

1. Read the hub's `uc:` frontmatter list — and, for a signal that sounds cross-feature, the `uc:`
   lists of the other hubs it plausibly touches.
2. Open each listed UC and read its actual content: the goal in `title`, `## 1`, and the flow.
3. **Same goal → update that UC**, in place, at any status (hard rule 7: approval does not freeze a
   UC, and a shipped feature does not either). "Same goal" means the same actor sitting down to
   accomplish the same thing — a new step, a new branch, a changed validation, and a new rule are all
   updates, not new UCs.
4. **A different goal → a new UC.** Mint the next id by `Grep` over `{uc_dir}` for the highest
   existing number and increment (`conventions.md` § ID scheme — use the `Grep` tool, never a Bash
   pipeline).

Two tests worth applying literally, because they are where this drifts:

- **The boss test.** If the signal describes something nobody would sit down and do as a unit of real
  work, it is not a UC — it is a step in one (`3-lane-uc.md` § Granularity).
- **A feature can carry several UCs.** Unlike the retired one-FR-per-feature norm, a feature with
  four genuinely distinct user goals gets four UCs, and that is correct rather than fragmentation.
  What it must not get is two UCs for the same goal.

For a cross-feature UC, also decide **`primary_feature`** — the feature whose actor holds the goal.
That decides which subagent may write the file (`3-lane-uc.md` § Ownership); every other
participating feature is listed in `features:` and gets a hub pointer in Stage 4.

## Durable vs. feature-scoped — the Design lane's own lookup

The second lookup, made the same way: read before deciding.

- **Durable / cross-cutting** — brand, tone, accessibility, interaction, layout, content, platform
  — applies beyond the feature it was said about. Destination: `{design_principles_file}`.
- **Feature-scoped** — this screen, this flow, this component. Destination: the hub's
  `## Design Directives`.
- A signal stated about one feature that clearly generalizes lands in **both**, which
  `conventions.md` § Design Principles Register explicitly allows.

Check `{design_principles_file}` before adding a row. `extract-signal` already files durable design
constraints there at extraction time, so the row often exists and the correct action is to cite it,
not to add a second one.

## Recording the routing decision

Whatever lane a signal takes, the hub's Signal Log row records where it went in the `Destination`
cell — the column extraction deliberately leaves blank. A themed row lists every destination its
clauses reached, ` · `-joined, and only reaches a terminal `Status` once all of them are recorded:

| Lane | `Destination` cell | Resulting `Status` |
|---|---|---|
| UC | `UC-###`, or `UC-### S<n>` / `UC-### E<n>` when the target already exists | `staged` (or `applied` if folded in immediately on the interactive path) |
| BR | `BR-###` | `staged` |
| Design, durable | `DESIGN-PRINCIPLES #<n>` | `applied` |
| Design, feature-scoped | `<slug> ## Design Directives` | `applied` |
| Entity | `EN-###` (or `ENTITIES.md proposed` if not promoted yet) | `applied` |
| Context | `UC-### § 1` or `PP-###` | `applied` |

Design, Entity, and Context destinations are `applied` on write because nothing about them is staged
behind a gate — the gate exists to protect UC/BR content from entering approved scope unreviewed, and
none of these enter it.
