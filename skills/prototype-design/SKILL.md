---
name: prototype-design
description: RETIRED — superseded by /bigin-generate-design, and not runnable besides. Kept only so old references to it resolve. It reads the retired pre-migration `.bigin/PRD.md` / `.bigin/prototypes/` layout, which does not exist in a project on the current `01-Requirements/_ucs/` model. Never invoke it, never route to it, and never run it alongside /bigin-generate-design. Design work goes to /bigin-generate-design, which reads UCs directly and needs no PRD and no approval first.
argument-hint: "(retired — use /bigin-generate-design)"
---

# Prototype Design — RETIRED

**Superseded by `/bigin-generate-design`. Do not run this, and never run both.**

`/bigin-generate-design` is the design stage: it reads `01-Requirements/_ucs/` directly, accepts a
feature carrying several UCs and a UC spanning several features, and writes
`04-UIUX/UX-<NNN> <Feature>.md` plus the shared append-only design system and two self-contained
prototype prompts. It runs off UCs rather than a PRD, so it does not wait on `/approve-uc`. Its rules are
`_bigin/conventions/design-conventions.md` — a separate rulebook on purpose.

This file is kept only so existing references to `/prototype-design` resolve to an explanation instead of
nothing. On top of being superseded, it is also **not runnable**: it reads `.bigin/PRD.md` and writes
`.bigin/prototypes/`, neither of which exists in a migrated project.

**When invoked:** say it is retired, point at `/bigin-generate-design`, and stop. Everything below is
kept as history of what it used to do — do not follow it.

---

## Historical contract (retired — do not execute)

Turned an approved feature into a text-level design a designer or engineer could act on directly, with
every flow step traceable back to the requirement it satisfied.

> **Artifact Standard:** Outputs a **prototype document** — `.bigin/prototypes/FR-<id>-prototype.md`: the flows that deliver the feature (each step citing the requirement it satisfies) and the screens/states they move through, including the edge-case states (empty, error, loading). Wireframe-level text, not a visual mockup — no mockup tooling is wired into this plugin.

---

## Non-Negotiable Core Rules

* **Precondition halts, never degrades:** this skill still reads the pre-migration `.bigin/` layout (§ Precondition).
* **Approved input only:** an unapproved feature goes back to `/approve-uc`, not into a prototype.
* **Traceable, not decorative:** a flow step that satisfies a requirement cites it. An untraceable step is scope nobody approved.
* **Concrete over pretty:** textual detail an engineer can build from beats a tidy outline.

---

## Precondition — check this first

`/bigin-transform-signal` writes the current layout (`01-Requirements/_ucs/`, `_brs/`); this skill still
reads `.bigin/`, and nothing bridges them yet.

**If `.bigin/features/` is absent while `01-Requirements/_ucs/` or `_frs/` has files, halt.** Say this
stage hasn't been migrated onto the `01-Requirements/` layout, name the files that are waiting, and
stop. Don't fall back to reading `01-Requirements/` — the sections and status vocabulary differ, so a
best-effort read produces a plausible artifact built on the wrong contract. Reporting "nothing found"
is the worse failure: it reads as an empty backlog rather than a missing bridge.

`_bigin/conventions/conventions.md` § Reconciliation notes tracks this gap — it is known, not new.

## Input

Read the approved feature's section in `.bigin/PRD.md`. If the feature isn't `Approved`, tell the user
to run `/approve-uc` first.

## What to do

* **Goal:** specify the flows, screens, and states that satisfy the feature's requirements.
* **Action:**
  1. Design the key screens/states, the interactions between them, and the edge-case states where relevant.
  2. Write `.bigin/prototypes/FR-<id>-prototype.md`:

     ```
     # FR-<id> Prototype

     ## Flows
     - <flow name>: <step-by-step, referencing FR-<id>.N where a step satisfies a specific requirement>

     ## Screens / States
     - <screen>: <purpose, key elements, states>
     ```
  3. Ask the user to review it, and mention that `/consolidate-prd <feature-id>` merges any changes back into the PRD and generates epics/stories.
