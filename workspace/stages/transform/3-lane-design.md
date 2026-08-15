# Design lane — directives that reach the design workflow without a PRD

```text
in:   signals routed to Design
out:  a {design_principles_file} row (durable) and/or a hub ## Design Directives row (feature-scoped)
never: a UC step · a BR · anything in PRD.md · Status: reflected
```

This lane exists because a presentation-only signal has nothing for a PRD to consume. Routed through
the UC lane it would either sit in a flow as an untestable step, or wait behind an approval gate it
doesn't need, while whoever runs `/prototype-design` never sees it.

## The chain this lane serves

| Chain | When |
|---|---|
| Full | `INT → UC/BR → PRD → EP → US → UX` — new scope on a `proposed`/`committed`/`not-built` feature |
| Lightweight CR | `INT → UC/BR → US → UX` — a change against a `built` feature |
| **Design** | `INT → design directive → UX` — presentation only, no behaviour change |

A design directive is an **input to** the design workflow, not a requirement about it. It never becomes
a UC step, never enters `PRD.md`, and never carries a `UC-###`/`EP-###`/`US-###`. Its traceability runs
through the hub's Signal Log row.

## Why this lane is not gated

The written gate protects **approved scope**: a UC that folds in a misread signal becomes a contract
the client signed off. A design directive enters no contract — it is read by `/prototype-design`, whose
entire output is a proposal a human reviews before anything is built. Gating the input too adds a
round-trip in front of a review that already happens.

**The asymmetry holds only because the boundary test is strict.** A design directive that turns out to
change behaviour is a **routing bug, not a gating exception**:

```text
found one → re-route to the UC lane
            leave the directive row Status: superseded, Notes: re-routed to UC-### S<n>
            name it in the report
```

Ambiguity *inside* the directive still raises a question — on the hub's `## Open Questions / Gates`, in
plain client language. "Warmer" needs no clarification; "use the new brand palette" does, if nobody has
said which palette.

## Destination 1 — durable, cross-cutting

Brand, tone, accessibility, interaction, layout, content, or platform preference outliving any one
feature. Destination: `{design_principles_file}`.

**Check the register before writing.** `/extract-signal` files durable design constraints there at
extraction time, so the row usually exists already.

| Case | Action |
|---|---|
| row exists, unchanged | cite it. Signal Log: `Status: applied`, `Destination: DESIGN-PRINCIPLES #<n>`, `Notes: already registered` |
| row exists, this signal **refines** it | append a **new** row; flip the old to `Status: superseded`, `Notes: superseded by #<n>`. Never edit the old row's text — append-only |
| row exists, this signal **contradicts** it | append the new row `Status: conflict` and raise one question naming both. Never pick a winner |
| no row | append one, creating the file from `_bigin/templates/design-principles-register.md` if absent |

Bump the register's `version` and append a `## Changelog` line on every write.

> **Column mismatch to expect.** The template's header is `# | Principle | Why | Source | Notes`;
> `conventions.md` § Design Principles Register describes
> `# | Principle / Preference | Category | Source | Status | Notes`. **Append rows matching the header
> the file on disk actually has**, report the mismatch once per run rather than migrating mid-write,
> and record a supersession in `Notes` when there is no `Status` column.

A signal stated about one feature that clearly generalizes lands here **and** in Destination 2 — each
serves a different reader.

## Destination 2 — feature-scoped

This screen, this flow, this component. Destination: the hub's `## Design Directives`, which
`/prototype-design` reads as the feature's presentation brief. Create the section from
`_bigin/templates/feature-hub.md` if the hub predates it — immediately before `## UX Spec`, since
directives are the input and the UX spec is the output.

```text
| # | Directive | Source | Status | Notes |
```

- **`#` is permanent**, hub-local, never renumbered or deleted.
- **`Directive`** — what the design must do, in one sentence, in the client's own terms. Not a
  paraphrase that generalizes it into a principle; if it generalizes, it also belongs in Destination 1.
- **`Source`** — `<INT-###> — <the Signal Log row's own Source cite>`.
- **`Status`** — `open` (not yet in a prototype) · `reflected` (a prototype implements it, set by
  `/prototype-design`) · `superseded` · `conflict`. **Leave `open` — this skill never sets `reflected`.**

Then set the Signal Log row: `Status: applied`, `Destination: <slug> ## UX Spec`.

Leave the hub's `uiux:` field alone — it points at a UX artifact that doesn't exist until
`/prototype-design` runs.

## Where this lane stops today

**Planned — the downstream consumer is not migrated.** `/prototype-design` currently keys on an FR id
and writes `prototypes/FR-<NNN>-prototype.md` from the pre-migration `.bigin/features/` layout. Since
`FR-###` is retired, that gap now applies to every feature.

```text
1  a feature with design directives cannot reach /prototype-design yet — no id it accepts.
   The directives are filed correctly and lose nothing; they are queued.
2  /prototype-design does not yet read ## Design Directives. It DOES read {design_principles_file}
   directly, so Destination 1 is live today; Destination 2 goes live when that skill migrates.
```

Report design-only features explicitly (`next: <slug> ready for /prototype-design (design-only)`) so
the queue is visible rather than silent. **Never mint a placeholder UC** just to give
`/prototype-design` something to key on — a UC with no flow pollutes the feature's material set and
reaches `/approve-fr` as if it were scope.

## What this lane never does

- Write a UC step, a BR, or anything into `PRD.md`.
- Set a hub's `uiux:` field, or write into `## UX Spec`.
- Set `Status: reflected` — that is the prototype's claim to make.
- Delete or rewrite an existing directive or design-principle row. Both registers are append-only.
- Route a behaviour change. Re-read `3-routing.md` § The design boundary test whenever a directive
  starts describing what happens rather than how it looks.
