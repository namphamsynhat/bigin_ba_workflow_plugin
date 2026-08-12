# Routing — which lane a qualified signal goes down

Every signal that clears Stage 2 goes down exactly one lane. A signal that genuinely belongs in two
places was two signals and should have been split at extraction — file the second half back as a
question rather than routing one row twice.

Routing is a decision about the **artifact the signal becomes**, which is the axis
`conventions.md` § Signal → artifact mapping already defines. It is deliberately *not* a
four-way "new requirement / requirement update / design / feedback" split: `new` vs `update` is a
lookup performed inside a lane, not a property of the signal, and `feedback` is a signal `Type`
that can land in any lane depending on what the feedback is about.

## The lane table

| The signal is… | Lane | Guide |
|---|---|---|
| A testable, actionable statement about system behaviour | **FR** | `lane-fr.md` |
| A conditional or policy constraint — feature-level, or governing one FR | **BR** | `lane-br.md` |
| A statement about presentation only: look, layout, tone, visual style, copy voice, interaction feel, accessibility affordance | **Design** | `lane-design.md` |
| A thing the business tracks and its attributes — a data field or entity | **Entity** | `lane-entity.md` |
| An end-to-end flow that genuinely crosses feature boundaries | **Entity** (§ Business Scenario half) | `lane-entity.md` |
| Narrative context — the client's stated why, not actionable on its own | **Context** → the FR's `## Business goal` | `lane-fr.md` |
| A concrete named frustration or cost, with no requirement attached | **Context** → `PP-###` mirror on the FR's `## Problem & Pain Points` | `lane-fr.md` |

A `pain-point` with no attached requirement is not a gap to fill. It stays on record until a later
signal turns it into an FR/BR line or a story resolves it. Never stretch one into a functional
requirement it does not support.

## Reading the signal's `Type` as a hint, not a verdict

Extraction typed each row (`requirement · constraint · decision · feedback · question · answer ·
concern · problem · pain-point`). That type narrows the lane but does not pick it:

| `Type` | Usual lane | Watch for |
|---|---|---|
| `requirement` | FR, or Design if presentation-only | The design boundary test below |
| `constraint` | BR, or Design if it is about look rather than policy | "Must be under 3 seconds" is a BR; "must feel fast" is Design |
| `decision` | FR (as a settled statement of how it works) | A `decision` has no `Why` — do not manufacture one for the FR's `## Business goal` |
| `feedback` | Whatever the feedback is *about* — FR if it changes behaviour, Design if it changes appearance | Feedback on an approved FR still edits it in place (hard rule 7) |
| `problem` / `pain-point` | Context | Never a stretched FR |
| `question` / `concern` | No lane — these are already `Status: question` on the hub | Do not draft from them |
| `answer` | Route by what it answers, not by its own type | It usually unblocks a `held` row rather than becoming one of its own |

## The design boundary test

This is the routing call most likely to drift, because the Design lane skips the PRD and the
approval gate — which makes it the cheap path, and cheap paths attract traffic that does not belong
on them. Apply the test literally.

**A signal is Design only if removing it would change how the feature looks or feels, and not what
it does.**

The operational check: *could a tester write a pass/fail assertion for this that never mentions
appearance?* If yes, it is FR or BR, no matter how visual the client's phrasing was.

| Client said | Lane | Why |
|---|---|---|
| "The dashboard should feel warmer, less corporate" | Design | Pure presentation |
| "Use our brand colours" | Design (durable) | Presentation, and cross-cutting |
| "Show status as coloured chips" | Design | Presentation of data the FR already defines |
| "Ask for confirmation before deleting" | **FR** | Adds a step and a state to the flow — testable without appearance |
| "Show the approver's name next to each row" | **FR** | Adds data to the view; the FR defines what is displayed |
| "Tap targets must be at least 44px" | Design (durable) | Accessibility affordance, no behaviour |
| "Older users must be able to complete this without help" | Design (durable) | A quality goal about the experience, not a behaviour |
| "Only a manager can approve" | **BR** | Policy constraint |

When a signal has both halves — "show the approver's name, and make it subtle" — the behaviour half
is the FR and the presentation half is a Design directive citing that FR. Two destinations, one
signal, both cited from the same Signal Log row's `Destination` cell.

**When the test is genuinely ambiguous, route to FR.** An over-routed FR gets caught at the human
gate; an under-routed design directive skips the gate entirely and quietly steers a prototype.

## New vs. update — a lookup, not a classification

Inside the FR and BR lanes, decide new-vs-update by **reading**, never by how the signal is
phrased. A client saying "we also need…" is not evidence that a second FR is warranted.

1. Read the hub's `fr:`/`br:` frontmatter lists.
2. Open each listed artifact and read its actual content.
3. If any of them covers this subject — even partially, even at a different status — this is an
   **update to that artifact**, in place (hard rule 7: approval does not freeze an FR, and a
   shipped feature does not either).
4. Only when nothing on this feature covers it is this a **new** artifact. Mint the next id by
   `Grep` over `{fr_dir}` or `{br_dir}` (each is its own independent sequence) for the highest
   existing number and increment. Use the `Grep` tool, never a Bash `grep`/`awk` pipeline —
   `conventions.md` § ID scheme explains why a denied shell pipeline silently reuses an id.

A feature normally carries **one FR across its whole life**. Two FRs on one slug is the rare case
where the feature's scope genuinely splits into two independent decisions, and it wants the
`amends:` field plus a human's confirmation — not a routing default.

## Durable vs. feature-scoped — the Design lane's own lookup

The second lookup, made the same way: read before deciding.

- **Durable / cross-cutting** — brand, tone, accessibility, interaction, layout, content, platform
  — applies beyond the feature it was said about. Destination: `{design_principles_file}`.
- **Feature-scoped** — this screen, this flow, this component. Destination: the hub's `## UX Spec`.
- A signal stated about one feature that clearly generalizes lands in **both**, which
  `conventions.md` § Design Principles Register explicitly allows.

Check `{design_principles_file}` before adding a row. `extract-signal` already files durable design
constraints there at extraction time, so the row often exists and the correct action is to cite it,
not to add a second one.

## Recording the routing decision

Whatever lane a signal takes, the hub's Signal Log row records where it went in the `Destination`
cell — the column extraction deliberately leaves blank:

| Lane | `Destination` cell | Resulting `Status` |
|---|---|---|
| FR | `FR-###` | `staged` (or `applied` if folded in immediately on the interactive path) |
| BR | `BR-###` | `staged` |
| Design, durable | `DESIGN-PRINCIPLES #<n>` | `applied` |
| Design, feature-scoped | `<slug> ## UX Spec` | `applied` |
| Entity | `EN-###` (or `ENTITIES.md proposed` if not promoted yet) | `applied` |
| Business Scenario | `SCN-###` | `applied` |
| Context | `FR-### ## Business goal` or `PP-###` | `applied` |

Design, Entity, Scenario, and Context destinations are `applied` on write because nothing about
them is staged behind a gate — the gate exists to protect FR/BR content from entering approved
scope unreviewed, and none of these enter it.
