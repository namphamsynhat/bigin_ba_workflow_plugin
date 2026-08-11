---
description: Merge prototype design decisions back into the PRD, reconcile any FR changes the prototype surfaced, and generate Epics and User Stories. Use after a feature's prototype design is reviewed.
argument-hint: "<feature-id, e.g. FR-003>"
disable-model-invocation: true
---

# Consolidate PRD

See `references/conventions.md` for the plugin-wide ID scheme and artifact conventions (§
Reconciliation notes there flags that this skill still reads the pre-migration `.bigin/` layout
below rather than `01-Requirements/`/`02-PRD/`/`03-Epics-Stories/` — treat that as the known gap,
not a new one to fix here).

## Input

Read the feature's PRD section (`.bigin/PRD.md`), its feature file (`.bigin/features/FR-<id>-*.md`), and its prototype (`.bigin/prototypes/FR-<id>-prototype.md`).

## What to do

1. Compare the prototype against the existing FRs. If prototyping surfaced new requirements, changed behavior, or new fields/entities, update the feature file's Functional Requirements and the PRD section accordingly — call out each change explicitly to the user rather than silently rewriting.
2. Add a `## Design` subsection to the feature's PRD section summarizing the finalized flows/screens (linking to the prototype file).
3. Generate/append to `.bigin/epics.md`:

   ```
   # Epic: <Feature Name> (FR-<id>)

   ## <Role>: <goal>
   As a <role>, I want <goal>, so that <benefit>.

   **Acceptance Criteria** (derived from FR-<id>.N):
   - <criterion>
   ```

   Decompose the feature into one epic with one or more user stories, each traceable to specific FR numbers via its acceptance criteria.
4. Report what was generated and flag anything that still needs BA sign-off (e.g. FR changes made in step 1).
