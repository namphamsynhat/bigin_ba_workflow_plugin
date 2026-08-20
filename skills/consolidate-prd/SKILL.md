---
name: consolidate-prd
description: NOT RUNNABLE — halted pending migration. This skill still reads the retired pre-migration `.bigin/PRD.md`, `.bigin/features/FR-<id>-*.md`, and `.bigin/prototypes/` layout, none of which exist in a project on the current `01-Requirements/_ucs/` model, so every invocation halts without doing anything. Do not route to it and do not offer it as a next step. **The PRD is not this skill's job any more** — `/bigin-generate-prd` writes one PRD per feature on the current model; what remains unmigrated here is only epic and story generation, which is still cut by hand from approved UCs.
argument-hint: "(not runnable — see the body)"
---

# Consolidate PRD — HALTED, not runnable

**Stop and say so. This skill cannot run against any current project.**

It reads `.bigin/PRD.md`, `.bigin/features/FR-<id>-*.md`, and `.bigin/prototypes/FR-<id>-prototype.md` —
the pre-migration flat-file layout, keyed on the retired `FR-###` artifact and on `/prototype-design`,
which is itself superseded. In a migrated project none of those paths exist.

All three of its upstream inputs moved: the PRD is now `02-PRD/PRD-<NNN> <Feature>.md`, one per feature,
written by **`/bigin-generate-prd`** with `absorbed: [UC-###@version]`; requirements are `UC-###` files;
and prototypes come from `/bigin-generate-design` as `04-UIUX/UX-<NNN> <Feature>.md`. **Only the epics
and stories half of this skill is still missing** — reading a flat `.bigin/PRD.md` that no longer exists
is why it cannot run at all.

## What to do when invoked

1. Say this stage is not migrated and cannot run — name the missing inputs, and
   `_bigin/conventions/conventions.md` § Reconciliation notes as where the gap is tracked.
2. Point at what is live: `/approve-uc` for sign-off, `/bigin-generate-design` for screens and prototype
   prompts, **`/bigin-generate-prd` for the PRD itself**. Only epics and stories are cut by hand, from a
   PRD that now exists as a real, versioned input.
3. Stop. **Do not** fall back to reading `01-Requirements/` — the sections and status vocabulary differ,
   so a best-effort read produces a plausible epic backlog built on the wrong contract, and a second PRD
   competing with the one `/bigin-generate-prd` owns. Reporting "nothing found" is worse: it reads as an
   empty backlog rather than a missing bridge.

---

## The target contract, for whoever migrates this

Not runnable today. Kept so the design intent survives the gap — a specification, not a procedure to
attempt.

**The PRD half of this contract is built** — see `/bigin-generate-prd`, which settled the granularity
question below in favour of one file per feature. What follows applies to whoever migrates the epics and
stories half.

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

- **File granularity, for `EP-###`/`US-###` only.** Whether each is its own file with its own id (what
  the rulebook assumes) or a flat `epics.md` (what this skill used to write). Pick one before building;
  don't let both readings coexist. **`PRD-###` is settled** — one file per feature, `/bigin-generate-prd`
  (§ Reconciliation notes), so an epics stage decomposes a real artifact rather than a section anchor.
- **Where a reconciliation lands.** Design surfacing a requirement change has a live home now — it goes
  back through `/bigin-transform-signal`'s gate as a staged `## Discussion` entry on the UC, not as a
  silent PRD rewrite. That is the rule to build against.

**Rules that carry over unchanged:** never silently rewrite a requirement — name every change design
forced; every story traces; requirement changes need explicit sign-off rather than being treated as
approved by the merge.
