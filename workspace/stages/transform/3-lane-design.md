# Design lane — directives that reach the design workflow without a PRD

Handles signals routed to **Design** (`3-routing.md` § The design boundary test). This lane exists
because a presentation-only signal has nothing for a PRD to consume: a PRD section states
functional scope, and "make it feel warmer" adds none. Routed through the FR lane it would either
sit in an FR as an untestable line or wait behind an approval gate it does not need, while the
person who could act on it — whoever runs `/prototype-design` — never sees it.

## The chain this lane serves

`conventions.md` § Traceability chain defines two chains. This lane serves the third:

| Chain | When |
|---|---|
| Full | `INT → FR/BR → PRD → EP → US → UX` — new scope on a `proposed`/`committed`/`not-built` feature |
| Lightweight CR | `INT → FR/BR → US → UX` — a change against a `built` feature |
| **Design** | `INT → design directive → UX` — presentation only, no behaviour change |

A design directive is an **input to** the design workflow, not a requirement about it. It never
becomes an FR line, never enters `PRD.md`, and never carries an `FR-###`/`EP-###`/`US-###` of its
own. Its traceability runs through the hub's Signal Log row, whose `Destination` cell names where
the directive landed.

## Why this lane is not behind the human gate

The written gate protects **approved scope**: an FR that folds in a misread signal becomes a
contract the client signed off. A design directive enters no contract. It is read by
`/prototype-design`, whose entire output is a proposal a human reviews before anything is built —
so gating the input as well adds a round-trip in front of a review that already happens.

The asymmetry is deliberate and bounded. It holds only because the boundary test in `3-routing.md` is
strict: anything testable without reference to appearance is FR or BR, and an ambiguous signal
routes to FR. **A design directive that turns out to change behaviour is a routing bug, not a
gating exception** — when one is found, re-route it to the FR lane, leave the directive row with
`Status: superseded`, `Notes: re-routed to FR-###`, and name it in the report.

Ambiguity inside the directive itself still raises a question — on the hub's
`## Open Questions / Gates`, in plain client language, following `conventions.md` § Open Questions
wording. "Warmer" needs no clarification; "use the new brand palette" does, if nobody has said
which palette.

## Destination 1 — durable, cross-cutting

Brand, tone, accessibility, interaction, layout, content, or platform preference that outlives any
one feature. Destination: `{design_principles_file}`.

**Check the register before writing.** `extract-signal` files durable design constraints there at
extraction time, so the row usually already exists and the correct action is to cite it. Adding a
second row for the same preference is the failure this check prevents.

| Case | Action |
|---|---|
| Row already exists, unchanged | Cite it. Signal Log: `Status: applied`, `Destination: DESIGN-PRINCIPLES #<n>`, `Notes: already registered` |
| Row exists, this signal refines it | Append a **new** row; flip the old row to `Status: superseded`, `Notes: superseded by #<n>`. Never edit the old row's text — the register is append-only, same discipline as the Signal Log |
| Row exists, this signal contradicts it | Append the new row with `Status: conflict` and raise one question naming both. Never pick a winner |
| No row | Append one, creating the file from `_bigin/templates/design-principles-register.md` if it does not exist |

Bump the register's `version` and append a `## Changelog` line on every write, so its own history
stays auditable.

> **Column mismatch to expect.** The template's header is
> `# | Principle | Why | Source | Notes`; `conventions.md` § Design Principles Register describes
> `# | Principle / Preference | Category | Source | Status | Notes`. **Append rows matching the
> header the file on disk actually has**, and report the mismatch once per run rather than
> migrating the file mid-write. When the file has no `Status` column, record a supersession in
> `Notes` instead.

A signal stated about one feature that clearly generalizes lands here **and** in Destination 2 —
`conventions.md` allows both, and each destination serves a different reader.

## Destination 2 — feature-scoped

This screen, this flow, this component. Destination: the hub's `## Design Directives` section,
which `/prototype-design` reads as the feature's presentation brief.

Create the section from `_bigin/templates/feature-hub.md` if the hub predates it —
place it immediately before `## UX Spec`, since directives are the input and the UX spec is the
output.

| # | Directive | Source | Status | Notes |
|---|-----------|--------|--------|-------|

- **`#` is permanent**, hub-local, never renumbered or deleted — same discipline as the Signal Log.
- **`Directive`**: what the design must do, in one sentence, in the client's own terms. Not a
  paraphrase that generalizes it into a principle — if it generalizes, it also belongs in
  Destination 1.
- **`Source`**: `<INT-###> — <the Signal Log row's own Source cite>`.
- **`Status`**: `open` (not yet reflected in a prototype) · `reflected` (a prototype implements it,
  set by `/prototype-design`) · `superseded` (a later directive replaced it, `Notes` pointing at
  the row) · `conflict` (contradicts an earlier directive, awaiting a human).
- Leave `Status: open` — this skill never sets `reflected`.

Then set the Signal Log row: `Status: applied`, `Destination: <slug> ## UX Spec`.

Leave the hub's `uiux:` frontmatter field alone. It points at a UX artifact that does not exist
until `/prototype-design` runs.

## Where this lane stops today

**Planned — the downstream consumer is not migrated.** `/prototype-design` currently keys on an FR
id and writes `prototypes/FR-<NNN>-prototype.md` from the pre-migration `.bigin/features/` layout
(README § Migration note, `conventions.md` § Reconciliation notes). Two consequences until it moves
onto `01-Requirements/`:

1. A feature whose hub has design directives but **no FR** cannot reach `/prototype-design` yet,
   because there is no id to invoke it with. The directives are filed correctly and lose nothing —
   they are simply queued.
2. `/prototype-design` does not yet read `## Design Directives`. It already reads
   `{design_principles_file}` directly, so Destination 1 is live today; Destination 2 becomes live
   when that skill migrates.

Report design-only features explicitly (`next: <slug> ready for /prototype-design (design-only)`)
so the queue is visible rather than silent. Do not work around the gap by minting a placeholder FR
just to give `/prototype-design` something to key on — an FR with no functional content pollutes
the feature's material set and would reach `/approve-fr` as if it were scope.

## What this lane never does

- Write an FR line, a BR, or anything into `PRD.md`.
- Set a hub's `uiux:` field, or write into `## UX Spec` itself.
- Set `Status: reflected` on a directive — that is the prototype's claim to make, not this skill's.
- Delete or rewrite an existing directive or design-principle row. Both registers are append-only.
- Route a behaviour change. Re-read `3-routing.md` § The design boundary test whenever a directive
  starts describing what happens rather than how it looks.
