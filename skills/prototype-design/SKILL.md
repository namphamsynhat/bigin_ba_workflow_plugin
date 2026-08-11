---
description: Produce a text-level prototype design (flows, screens, states) for an approved feature, traceable back to its FRs. Use after a feature is approved.
argument-hint: "<feature-id, e.g. FR-003>"
disable-model-invocation: true
---

# Prototype Design

See `references/conventions.md` for the plugin-wide ID scheme and artifact conventions (§
Reconciliation notes there flags that this skill still reads the pre-migration `.bigin/` layout
below — treat that as the known gap, not a new one to fix here).

## Input

Read the approved feature's section in `.bigin/PRD.md`. If the feature isn't `Approved` yet, tell the user to run `/approve-fr` first.

## What to do

1. Design the flows and screens needed to satisfy the feature's FRs: key screens/states, the interactions between them, and edge-case states (empty, error, loading) where relevant.
2. Write `.bigin/prototypes/FR-<id>-prototype.md`:

   ```
   # FR-<id> Prototype

   ## Flows
   - <flow name>: <step-by-step, referencing FR-<id>.N where a step satisfies a specific requirement>

   ## Screens / States
   - <screen>: <purpose, key elements, states>
   ```

   This is a textual/wireframe-level design — no visual mockup tooling is wired into this plugin — but be concrete enough that a designer or engineer could act on it directly.
3. Ask the user to review it, and mention that `/consolidate-prd <feature-id>` will merge any changes back into the PRD and generate epics/stories.
