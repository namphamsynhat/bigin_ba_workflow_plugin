---
name: approve-fr
description: Approve a feature's requirements and generate or update the consolidated PRD. Use once enrichment concerns are resolved or accepted.
argument-hint: "<feature-id, e.g. FR-003>"
---

# Approve FR

Marks a feature approved on the human's explicit call, then folds it into the consolidated PRD.

This is the approval gate of the extract → transform → load pipeline — the one point where a drafted
requirement becomes committed scope.

> **Artifact Standard:** Outputs:
>> **An approved feature file** — `Status: Approved`, set only after the human confirms.
>> **One PRD section per feature** — the feature's summary, requirements, pain points, entity map, and accepted-risk domain concerns, written into `.bigin/PRD.md` under its own `FR-<id>` heading. Every other feature's section stays untouched.

---

## Non-Negotiable Core Rules

* **Precondition halts, never degrades:** this skill still reads the pre-migration `.bigin/` layout (§ Precondition).
* **Never approve on the user's behalf:** approval is a human decision, confirmed against a summary they can see.
* **Section-scoped PRD writes:** replace only this feature's section, matched by its `FR-<id>` heading.
* **Enrichment is expected, not enforced:** an un-enriched feature gets the recommendation and an explicit override choice, not a silent pass.

---

## Precondition — check this first

`/bigin-transform-signal` writes the current layout (`01-Requirements/_ucs/`, `_brs/`); this skill still
reads `.bigin/features/`, and nothing bridges them yet.

**If `.bigin/features/` is absent while `01-Requirements/_ucs/` or `_frs/` has files, halt.** Say this
stage hasn't been migrated onto the `01-Requirements/` layout, name the files that are waiting, and
stop. Don't fall back to reading `01-Requirements/` — the sections and status vocabulary differ, so a
best-effort read produces a plausible artifact built on the wrong contract. Reporting "nothing found"
is the worse failure: it reads as an empty backlog rather than a missing bridge.

`_bigin/conventions/conventions.md` § Reconciliation notes tracks this gap — it is known, not new.

## Input

Read `.bigin/features/FR-<id>-*.md`. If `Status` is not `Enriched`, say enrichment should run first
(`/enrich-feature`) and ask whether to override and approve anyway.

## What to do

* **Goal:** convert a reviewed feature into committed scope, visible in one consolidated document.
* **Action:**
  1. Show a short summary — requirements, pain points, any unresolved Domain Concerns — and confirm the user intends to approve.
  2. On confirmation, set `Status: Approved` in the feature file.
  3. Read `.bigin/PRD.md`, creating it with a `# Product Requirements Document` heading if missing.
  4. Write or replace **only this feature's section**: feature summary, requirements, pain points, entity map, accepted-risk domain concerns.
  5. Confirm the PRD update and tell the user to run `/bigin-generate-design <feature-id>` next.
