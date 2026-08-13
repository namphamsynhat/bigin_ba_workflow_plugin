---
name: enrich-feature
description: Enrich a drafted feature's requirements with domain research and an entity map, surfacing concerns before approval. Use after /bigin-transform-signal has produced or updated a feature's FR(s)/BR(s).
argument-hint: "<feature-id, e.g. FR-003>"
---

# Enrich Feature

See `_bigin/conventions/conventions.md` for the plugin-wide ID scheme and artifact conventions (§
Reconciliation notes there flags that this skill still reads the pre-migration `.bigin/` layout
below rather than `01-Requirements/_frs/` — treat that as the known gap, not a new one to fix here).

## Precondition — check this first

This skill still reads the pre-migration `.bigin/` layout. `/bigin-transform-signal` writes the
current one (`01-Requirements/_frs/`, `_brs/`), and nothing bridges them yet.

**If `.bigin/features/` is absent while `01-Requirements/_frs/` has files, halt.** Say that this stage
hasn't been migrated onto the `01-Requirements/` layout, name the FR files that are waiting, and stop.
Do not fall back to reading `01-Requirements/` — the sections and status vocabulary differ, so a
best-effort read produces a plausible artifact built on the wrong contract. Reporting "nothing found"
is the worse failure: it reads as an empty backlog rather than a missing bridge.

## Input

Read `.bigin/features/FR-<id>-*.md` for the feature named in `$ARGUMENTS`. If no id is given, list `Status: Draft` features as candidates and ask which one.

## What to do

1. **Domain research**: based on the feature's FRs and pain points, research the relevant business/technical domain (use WebSearch if available) to surface known edge cases, industry-standard approaches, compliance/regulatory concerns, and common failure modes similar products have hit. Keep findings specific to this feature, not generic advice.
2. **Entity mapping**: identify the entities involved in the FRs (actors, data objects, systems, external integrations) and their relationships.
3. Append two sections to the feature file — don't touch existing sections:

   ```
   ## Domain Concerns
   - <concern>: <why it matters, and what to decide/mitigate>

   ## Entity Map
   - <Entity> (actor|data|system): <relationships to other entities>
   ```
4. Update `Status:` to `Enriched`.
5. Summarize the concerns to the user and ask whether each needs resolving now or can be accepted as a known risk before approval. Record their call inline next to each concern (`resolved`, `accepted risk`, or `deferred`).
6. Tell the user to run `/approve-fr <feature-id>` when ready.
