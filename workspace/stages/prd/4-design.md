# Stage 4 — Design, scope, and open decisions: §§ 9-12

```text
runs: per feature (orchestrator inline, or one worker per feature)
in:   {ux_dir}/UX-<NNN> <Feature>.md (§ 1-§ 6) · {design_principles_file} rows it applied ·
      the hub's ## Design Directives · the PENDING list from Stage 1 · every folded UC's § 5 and § 6
out:  §§ 9-12 of {prd_dir}/PRD-<NNN> <Feature>.md, plus § 6's Screen column backfilled
never: inventing a screen, a state, or a visual decision (P6) · a token name, hex, or px (P1) ·
       editing the UX spec (P4) · restating a prototype prompt
```

## § 9 Experience & Design — report the design, never decide it

The design already exists or it does not. This section quotes it.

```text
no UX spec for this feature   → one line: "No screens designed yet — /bigin-generate-design has not
                                run for this feature." Then move to § 10. NOT a blocker, and NOT a
                                reason to describe screens from the flows
UX spec exists                → fill § 9 from it, and record UX-###@version for design_absorbed:
```

**What to take, and from where:**

| § 9 element | Source in the UX spec |
|---|---|
| `Design spec` + version | its frontmatter `id`, `status`, `version` |
| `Platform` | § 1 Design Brief `Platform` |
| `Design intent, as stated to us` | § 1 `Principles applied` + `Directives applied` — the client's words, not the row numbers alone |
| **Screens** table | § 2 Screen Inventory: `Screen`, `Purpose` → `What the actor does there`, `Serves` → the § 5 capability whose UC owns those `S#` ids |
| **Journeys** table | § 4 Flows: `Path` → `The path through the screens`, `Success` → `Ends on` |
| `Prototype` | say the prompts are in `UX-<NNN> § Prototype Prompt — Claude design` / `— Figma Make`. **Point, never restate** |
| `Known design gaps` | § 6 Open Questions, unchecked lines only, translated to business words |

**What never crosses from the design side into this document** (`{design_conventions}` D2, and P1
here): a token name, a hex value, a px value, a font, a component name, a region layout, an
interaction table. A business reader cannot verify any of it, and duplicating it here creates a
second, drifting source for something the design system owns.

**Backfill § 6's `Screen` column now.** The UX spec's § 2 `Serves` column cites `S#` ids directly, so
the mapping is a lookup, not a judgment: for each `S#` in § 6, the screen whose `Serves` lists it.

```text
one screen serves the step        → name it
several screens serve one step    → name the one the actor is on when the step happens
no screen serves the step         → "—", and one line in Known design gaps. Never the nearest screen
```

`Serves` citing an `S#` that no folded UC has → the design is stale against the requirement. Report
`design stale → /bigin-generate-design`; do not repair the mapping by inference.

## § 10 Scope & Release Framing

**In scope** is § 5's capability list. Do not restate the rows — one line pointing at § 5 keeps them
from drifting apart.

**Out of scope** takes only explicit exclusions: a client statement in an intake, a settled
decision-log row in a folded UC's § 5 that closed scope, a non-goal from § 3. `Stated by` cites it.

**Never invent phasing.** No MVP/Growth/Vision split, no "phase 2", unless a source asked for phased
delivery. Everything approved is one release unless stated otherwise — a boundary this document
invents becomes a boundary the client is told they agreed to.

**Pending scope** is Stage 1's PENDING list — every UC on this feature that is not `approved` but has
a drafted main flow:

```text
UC                       the id
Goal                     its title:
Status                   draft | needs-clarification | enriched
What it is waiting on    needs-clarification → "N open question(s)" (count § 5's unchecked lines)
                         draft/enriched      → "human sign-off — /approve-uc"
```

Write `pending_uc:` in frontmatter to match. This table is the reason the PRD can be generated on a
part-approved feature without reading as sign-off on unapproved scope (P2): the reader sees exactly
what is missing and why. Nothing from these UCs appears in §§ 5-9 — not a capability row, not a flow,
not a screen.

## § 11 Open Business Decisions

Pool, into one list, in this order:

1. every unchecked `- [ ] Q:` line in each folded UC's § 5 **Still open**
2. every unchecked line in the UX spec's § 6 that is marked a **requirement gap**
3. anything this run could not answer from the artifacts — a § 3 goal with no measure, a `BR-###`
   with no enforcement point, two rules that contradict, a `PP-###` no capability addresses

Rules for the list:

```text
- keep the ORIGINAL SENTENCE for 1 and 2 — the same question, worded identically, so a human
  answering it here and a human answering it on the UC are answering one question, not two
  ({conventions_reference} § One question, two places)
- (ref: …) always names where it lives: UC-<NNN> § 5, or UX-<NNN> § 6, or PRD-<NNN> for a
  gap this run found
- one decision per line, self-contained, plain business language
  ({conventions_reference} § Open Questions wording)
- never write an A: line here. A decision is answered on the artifact that owns it and folded in by
  /bigin-transform-signal or /bigin-generate-design; this list is refreshed from them on the next run
```

An `approved` UC normally contributes nothing to this list — its questions were resolved before
approval. If one does, a later edit reopened it (hard rule 7), and that is worth naming in the
report: the feature is part-approved with live questions.

## § 12 Assumptions, Dependencies & Constraints

Only what a source stated. Each subsection is `none stated` rather than filled:

| Subsection | Where it actually comes from |
|---|---|
| Assumptions | a UC's § 5 decision log ("we assumed X and proceeded"), an intake statement, `{project_file}` |
| Depends on | another feature's slug, a third party named in a UC step, a client data hand-over |
| Constraints | a folded UC's § 6 Special Requirements (volume, frequency, compliance, channel), a stated deadline in `{project_file}` |

A UC's § 6 is the section most often skipped by an upstream stage and the only place a scoped
non-functional constraint lives in this vault — read it on every folded UC before writing
`none stated`.
