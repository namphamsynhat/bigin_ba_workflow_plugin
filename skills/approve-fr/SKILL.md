---
name: approve-fr
description: Approve a feature's Functional Requirements and generate or update the consolidated PRD. Use once enrichment concerns are resolved or accepted.
argument-hint: "<feature-id, e.g. FR-003>"
---

# Approve FR

See `_bigin/rules/conventions.md` for the plugin-wide ID scheme and artifact conventions (§
Reconciliation notes there flags that this skill still reads the pre-migration `.bigin/` layout
below rather than `01-Requirements/_frs/`/`PRD.md` under `02-PRD/` — treat that as the known gap,
not a new one to fix here).

## Precondition — check this first

This skill still reads the pre-migration `.bigin/` layout. `/bigin-transform-signal` writes the
current one (`01-Requirements/_frs/`, `_brs/`), and nothing bridges them yet.

**If `.bigin/features/` is absent while `01-Requirements/_frs/` has files, halt.** Say that this stage
hasn't been migrated onto the `01-Requirements/` layout, name the FR files that are waiting, and stop.
Do not fall back to reading `01-Requirements/` — the sections and status vocabulary differ, so a
best-effort read produces a plausible artifact built on the wrong contract. Reporting "nothing found"
is the worse failure: it reads as an empty backlog rather than a missing bridge.

## Input

Read `.bigin/features/FR-<id>-*.md`. If `Status` is not `Enriched`, tell the user enrichment should run first (`/enrich-feature`) and ask whether they want to override and approve anyway.

## What to do

1. Confirm with the user that they intend to approve this feature — show a short summary of its FRs, pain points, and any unresolved Domain Concerns.
2. On confirmation, set `Status: Approved` in the feature file.
3. Read `.bigin/PRD.md` (create it with a `# Product Requirements Document` heading if missing).
4. Write or replace **only this feature's section** in the PRD (matched by its `FR-<id>` heading), containing: feature summary, Functional Requirements, Pain Points, Entity Map, and any accepted-risk Domain Concerns. Leave every other feature's section untouched.
5. Confirm the PRD update to the user and tell them to run `/prototype-design <feature-id>` next.
