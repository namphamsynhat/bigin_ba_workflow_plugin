---
name: enrich-feature
description: NOT RUNNABLE — halted pending migration. This skill still reads the retired pre-migration `.bigin/features/FR-<id>-*.md` layout, which does not exist in any project on the current `01-Requirements/_ucs/` model, so every invocation halts without doing anything. Do not route to it, do not gate an approval on the `enriched` status it would have set, and do not offer it as a next step. Domain research on a drafted requirement is done by hand, or by `/bigin-ba` doing the research inline, until this is migrated to per-UC enrichment.
argument-hint: "(not runnable — see the body)"
---

# Enrich Feature — HALTED, not runnable

**Stop and say so. This skill cannot run against any current project.**

It reads `.bigin/features/FR-<id>-*.md` — the pre-migration flat-file layout, keyed on the retired
`FR-###` artifact. `/bigin-transform-signal` writes `01-Requirements/_ucs/UC-<NNN> <Title>.md` with
`status:` frontmatter instead, and nothing bridges the two. In a migrated project `.bigin/features/`
does not exist, so there is no input to read and no run that can succeed.

## What to do when invoked

1. Say this stage is not migrated and cannot run — name `.bigin/features/` as the missing input and
   `_bigin/conventions/conventions.md` § Reconciliation notes as where the gap is tracked.
2. Point at what is live instead: the UC is already reviewable (`/approve-uc`) and already designable
   (`/bigin-generate-design`); neither waits on enrichment.
3. Stop. **Do not** fall back to reading `01-Requirements/` — the sections and status vocabulary differ,
   so a best-effort read produces a plausible artifact built on the wrong contract, which is worse than
   no artifact. Reporting "nothing found" is worse still: it reads as an empty backlog rather than a
   missing bridge.

## Consequences other skills must respect

- **`enriched` is unreachable.** Nothing writes it today, so nothing may gate on it.
  `draft → approved` is the live path. `/approve-uc` mentions enrichment **only** when
  `.bigin/features/` actually exists on disk — otherwise it says nothing, rather than asking
  "enrichment hasn't run, proceed anyway?" on every approval forever.
- **`/bigin-ba` does not route here.** Its pipeline list marks this stage halted. When domain research
  is genuinely needed on a drafted requirement, it does the research itself and records what it found;
  it does not invoke this skill to do it.

---

## The target contract, for whoever migrates this

Not runnable today. Kept so the design intent survives the gap — this is a specification, not a
procedure to attempt.

**Scope changes from per-feature to per-UC.** The unit of enrichment is one `UC-###`, not one feature:
a feature carries several UCs, and a UC can span several features, so "enrich the feature" has no
single input any more. Read the UC's `## 2`/`## 3` flows, its `## 4` rule mirror, and its `## 5`
**Still open** list (not `## Open Questions`).

**Outputs, appended to the UC file without touching existing sections:**

- **`## Domain Concerns`** — edge cases, industry-standard approaches, compliance exposure, and failure
  modes similar products have hit, each tied to a specific `S#`/`A#`/`E#` or `BR-###` on this UC, and
  each carrying the human's call (`resolved` · `accepted risk` · `deferred`). Generic best-practice
  filler is worse than no research. `_bigin/conventions/conventions.md` § Feature Hub's
  `## Domain Research` bullet is the settled destination for the *hub-level* log of these runs; the
  findings themselves go on the UC.
- **The `> [!summary]-` block** on the UC, which `3-lane-uc.md` § Creating a new UC already leaves
  blank for this stage to fill.

**Rules that carry over unchanged:** append only, never rewrite an existing section; the concern call is
the human's to make, recorded not decided; and an unattended run records every concern with no call made
rather than adjudicating one (`agents/bigin-ba.md` § Working unattended alongside a live review).

**What it must not do:** write `status: enriched` before `## Domain Concerns` actually exists on the UC;
promote an entity (that is `/sync-entities`); or touch `## 1`–`## 6`.
