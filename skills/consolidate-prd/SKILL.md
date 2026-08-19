---
name: consolidate-prd
description: NOT RUNNABLE — halted pending migration. This skill still reads the retired pre-migration `.bigin/PRD.md`, `.bigin/features/FR-<id>-*.md`, and `.bigin/prototypes/` layout, none of which exist in a project on the current `01-Requirements/_ucs/` model, so every invocation halts without doing anything. Do not route to it and do not offer it as a next step. PRD, epic, and story generation is not built on the current model; an approved UC is feature material a human hands off (conventions § Feature material).
argument-hint: "(not runnable — see the body)"
---

# Consolidate PRD — HALTED, not runnable

**Stop and say so. This skill cannot run against any current project.**

It reads `.bigin/PRD.md`, `.bigin/features/FR-<id>-*.md`, and `.bigin/prototypes/FR-<id>-prototype.md` —
the pre-migration flat-file layout, keyed on the retired `FR-###` artifact and on `/prototype-design`,
which is itself superseded. In a migrated project none of those paths exist.

Its two upstream inputs are both gone from the live path: nothing writes a `PRD.md` at all today
(`/approve-uc` approves the UC and stops — `_bigin/conventions/conventions.md` § Feature material), and
prototypes come from `/bigin-generate-design` as `04-UIUX/UX-<NNN> <Feature>.md`, on a different model.

## What to do when invoked

1. Say this stage is not migrated and cannot run — name the missing inputs, and
   `_bigin/conventions/conventions.md` § Reconciliation notes as where the gap is tracked.
2. Point at what is live: `/approve-uc` for sign-off, `/bigin-generate-design` for screens and prototype
   prompts. Epics and stories are cut by hand from approved UCs until this is migrated.
3. Stop. **Do not** fall back to reading `01-Requirements/` — the sections and status vocabulary differ,
   so a best-effort read produces a plausible PRD built on the wrong contract. Reporting "nothing found"
   is worse: it reads as an empty backlog rather than a missing bridge.

---

## The target contract, for whoever migrates this

Not runnable today. Kept so the design intent survives the gap — a specification, not a procedure to
attempt.

**Inputs become UC-shaped.** One feature carries several `UC-###`; one UC can span several features, and
`primary_feature` decides which chain owns it. Read each UC's `## 2`/`## 3` flows, its `## 4` rule
mirror, and its `## 5` **Still open** list — not an FR's `## Functional requirements`. The design input
is the feature's `04-UIUX/UX-<NNN> …` and its `absorbed:` list of `UC-###@version` stamps, which is what
makes "this design is stale against the current UC" detectable.

**Epics and stories are cut as use-case slices, flows first** — one story per meaningful path through a
UC's `## 2`/`## 3`, not one story per requirement line
(`_bigin/conventions/conventions.md` § Traceability chain). Acceptance criteria cite the `S#`/`A#`/`E#`
and `BR-###` ids they derive from; a story citing none is unapproved scope.

**Two things still undecided, and they block a clean build** (§ Reconciliation notes):

- **File granularity.** Whether `PRD-###`/`EP-###`/`US-###` are each their own file with their own id
  (what the rulebook assumes) or a flat `epics.md` (what this skill used to write). Pick one before
  building; don't let both readings coexist.
- **Where a reconciliation lands.** Design surfacing a requirement change has a live home now — it goes
  back through `/bigin-transform-signal`'s gate as a staged `## Discussion` entry on the UC, not as a
  silent PRD rewrite. That is the rule to build against.

**Rules that carry over unchanged:** never silently rewrite a requirement — name every change design
forced; every story traces; requirement changes need explicit sign-off rather than being treated as
approved by the merge.
