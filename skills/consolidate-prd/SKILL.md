---
name: consolidate-prd
description: Merge prototype design decisions back into the PRD, reconcile any requirement changes the prototype surfaced, and generate Epics and User Stories. Use after a feature's prototype design is reviewed.
argument-hint: "<feature-id, e.g. FR-003>"
---

# Consolidate PRD

Closes the loop after a prototype review: reconciles what designing revealed back into the PRD, then
decomposes the feature into buildable work.

This is the final Load stage of the extract → transform → load pipeline.

> **Artifact Standard:** Outputs:
>> **A reconciled PRD section** — requirement changes the prototype surfaced, each called out explicitly, plus a `## Design` subsection summarizing the finalized flows/screens and linking to the prototype.
>> **Epics and User Stories** — one epic per feature in `.bigin/epics.md`, each story traceable to specific requirement numbers through its acceptance criteria.

---

## Non-Negotiable Core Rules

* **Precondition halts, never degrades:** this skill still reads the pre-migration `.bigin/` layout (§ Precondition).
* **Never silently rewrite a requirement:** every change the prototype forced is named to the user.
* **Every story traces:** acceptance criteria cite the requirement numbers they derive from. A story with none is unapproved scope.
* **Requirement changes need sign-off:** flag them at the end rather than treating the merge as approval.

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

Read the feature's PRD section (`.bigin/PRD.md`), its feature file
(`.bigin/features/FR-<id>-*.md`), and its prototype (`.bigin/prototypes/FR-<id>-prototype.md`).

## What to do

* **Goal:** get the PRD and the prototype telling the same story, then break it into stories.
* **Action:**
  1. **Reconcile.** Compare the prototype against the existing requirements. Where prototyping surfaced new requirements, changed behavior, or new fields/entities, update the feature file and the PRD section — calling out each change explicitly rather than rewriting silently.
  2. **Record the design.** Add a `## Design` subsection to the feature's PRD section summarizing the finalized flows/screens, linking to the prototype file.
  3. **Decompose.** Generate or append to `.bigin/epics.md` — one epic per feature, with one or more user stories:

     ```
     # Epic: <Feature Name> (FR-<id>)

     ## <Role>: <goal>
     As a <role>, I want <goal>, so that <benefit>.

     **Acceptance Criteria** (derived from FR-<id>.N):
     - <criterion>
     ```
  4. **Report** what was generated, and flag anything still needing BA sign-off — the step 1 requirement changes above all.
