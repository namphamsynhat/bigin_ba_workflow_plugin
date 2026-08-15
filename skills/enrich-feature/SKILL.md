---
name: enrich-feature
description: Enrich a drafted feature's requirements with domain research and an entity map, surfacing concerns before approval. Use after /bigin-transform-signal has produced or updated a feature's UC(s)/BR(s).
argument-hint: "<feature-id, e.g. FR-003>"
---

# Enrich Feature

Researches a drafted feature's domain and maps its entities, surfacing concerns while they are still
cheap to act on — before approval, not after.

This is the first Load stage of the extract → transform → load pipeline.

> **Artifact Standard:** Outputs, appended to the feature file without touching existing sections:
>> **Domain Concerns** — edge cases, industry-standard approaches, compliance exposure, and failure modes similar products have hit, each specific to this feature and each carrying the human's call (`resolved` · `accepted risk` · `deferred`).
>> **Entity Map** — the actors, data objects, systems, and external integrations the requirements involve, and their relationships.

---

## Non-Negotiable Core Rules

* **Precondition halts, never degrades:** this skill still reads the pre-migration `.bigin/` layout (§ Precondition). Halt rather than best-effort against `01-Requirements/`.
* **Specific, not generic:** findings tie to this feature's requirements and pain points. Generic best-practice filler is worse than no research.
* **Append only:** write the two new sections; never rewrite existing ones.
* **The concern call is the user's:** record it, don't decide it.

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

Read `.bigin/features/FR-<id>-*.md` for the feature named in `$ARGUMENTS`. With no id given, list
`Status: Draft` features as candidates and ask which one.

## What to do

* **Goal:** turn a drafted feature into an enriched one whose risks are on the page and adjudicated.
* **Action:**
  1. **Domain research.** From the feature's requirements and pain points, research the relevant business/technical domain (`WebSearch` where available) for known edge cases, industry-standard approaches, compliance/regulatory concerns, and common failure modes.
  2. **Entity mapping.** Identify the entities the requirements involve and their relationships.
  3. **Append two sections** to the feature file:

     ```
     ## Domain Concerns
     - <concern>: <why it matters, and what to decide/mitigate>

     ## Entity Map
     - <Entity> (actor|data|system): <relationships to other entities>
     ```
  4. Set `Status:` to `Enriched`.
  5. Summarize the concerns and ask, per concern, whether it needs resolving now or can be accepted as a known risk. Record the call inline next to each one.
  6. Tell the user to run `/approve-fr <feature-id>` when ready.
