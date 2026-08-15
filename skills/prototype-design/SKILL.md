---
name: prototype-design
description: Produce a text-level prototype design (flows, screens, states) for an approved feature, traceable back to its requirements. Use after a feature is approved.
argument-hint: "<feature-id, e.g. FR-003>"
---

# Prototype Design

Turns an approved feature into a text-level design a designer or engineer can act on directly, with
every flow step traceable back to the requirement it satisfies.

This is the design stage of the extract → transform → load pipeline.

> **Artifact Standard:** Outputs a **prototype document** — `.bigin/prototypes/FR-<id>-prototype.md`: the flows that deliver the feature (each step citing the requirement it satisfies) and the screens/states they move through, including the edge-case states (empty, error, loading). Wireframe-level text, not a visual mockup — no mockup tooling is wired into this plugin.

---

## Non-Negotiable Core Rules

* **Precondition halts, never degrades:** this skill still reads the pre-migration `.bigin/` layout (§ Precondition).
* **Approved input only:** an unapproved feature goes back to `/approve-fr`, not into a prototype.
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
to run `/approve-fr` first.

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
