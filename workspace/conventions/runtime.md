# Conventions — runtime behaviour and reconciliation

How an unattended run checkpoints and resumes, the (planned) reprocess trigger, and the standing
record of where this plugin's skills still differ from this rulebook.

**Read by** a skill running unattended, `/bigin-upgrade-project`, and `bigin-ba` / `/bigin-run`
when they need migration status (§ Reconciliation notes is the single source for that).

## Absorbed — the reprocess trigger (**Planned**)

`sources:` answers *"which upstream artifacts does this one trace to?"* — a permanent,
never-pruned traceability record (hard rule 3). It cannot answer *"is this artifact still
current?"*, and since hard rule 7 nothing else could either: a CR edits an approved UC **in
place** — same id, bumped `version`, no new id anywhere — so a PRD section that cites `UC-007`
keeps looking covered no matter how far `UC-007`'s content has since moved. The failure mode this
guards against: new intake updates a UC, the human re-approves it, and the feature's
PRD/epics/prototype sit stale from the cascade — visually identical to freshly drafted work
awaiting review, with nothing anywhere saying "the downstream steps need to re-run."

**`absorbed:` is the record that would close it, once built.** Every artifact downstream of
another would carry it:

| Artifact | `absorbed:` entries | Written by |
|---|---|---|
| PRD | `UC-###@version` for each approved UC folded into it, plus `UX-###@version` in `design_absorbed:` | **retired** — `/bigin-generate-prd` was removed in 1.13.0; existing stamps stay as written, frozen |
| Epic/Story | `PRD-###@version` (or `UC-###@version` on the lightweight path) it decomposes | by hand — no skill |
| Prototype | `UC-###@version` / PRD section version it designed from | `/bigin-generate-design` |

**The rule, once implemented: an artifact is stale when an upstream it *cites* has a current
`id@version` that its `absorbed:` doesn't list.** Two states, don't conflate them:

- **Never processed** — the upstream id appears in no downstream `sources:` at all. The
  downstream step simply hasn't run for it yet.
- **Processed, then drifted** — cited, but the version moved on. This is the re-approved-CR case,
  and the one that's invisible without this field.

Whoever produces an artifact **re-stamps** its `absorbed:` on every run — that's what makes this
self-healing rather than another mirror to go stale: there is no separate counter, and a re-run
cannot leave a false "current" claim behind. `/bigin-generate-design` stamps `UX-###`, so "this
design is stale" is detectable today (the PRD row was live until the PRD stage was retired in 1.13.0). `/bigin-generate-stories`
stamps `UC-###@version` and `UX-###@version` on every `EP-###` and `US-###` it writes, so "these stories have
drifted" is detectable too; an approved story that drifted is reported, never rewritten.

## Resumable unattended apply (checkpoint + idempotent writes)

An unattended apply is a multi-file write — the UC or BR, its hubs, `FEATURES.md`, sometimes the source
INT note — with no database transaction, and a run can be killed between any two writes. Since v1.10.0
the engine (`bin/bigin apply`, `bin/bigin ledger release`) is the one place that guarantee lives:

1. **Idempotent by change-set id.** Every applied set's id is recorded in the artifact's `## Changelog`
   (`cs: …`); re-applying it is a no-op reported as `already`. A created UC/BR records `created by <id>`.
2. **One write per artifact, verified.** All of an artifact's sets are composed in memory and written
   once: backup → atomic replace → re-read verify (every heading present, no untouched section changed,
   no unset frontmatter key changed) → restore on failure. A write whose file changed on disk since it
   was read is refused, never merged blindly.
3. **Mirrors are re-derived, never appended once.** Signal Log flips, `links sync`, `hub refresh`,
   `status` are recomputed from the artifacts' current state; running them again is a no-op.
4. **Run state is machine-readable.** `_runs/<run-id>/` holds `plan.json`, the agents' task files,
   `results.jsonl`, and `metrics.jsonl`; re-running a workflow with the same run id skips finished tasks
   (`bin/bigin run done`). A kill leaves a clean resume point because every write is atomic and engine-only.

The artifacts plus the ledger (`01-Requirements/_ledger/*.jsonl`, gated change sets) are the ground truth.
Re-running the same skill from a fresh session re-derives where it left off.

## Reconciliation notes for this plugin

Concrete gaps between this document and the plugin's actual skills, collected here instead of as
scattered inline caveats — resolve and delete each line as the corresponding skill is migrated.

- ~~**Plugin-internal paths were unreachable at runtime.**~~ **Resolved (plugin 1.2.0).** The rulebook
  and templates are now materialized into the project by `/bigin-new-project`
  (`_bigin/conventions/`, `_bigin/stages/`, `_bigin/templates/`), and every skill, dispatch prompt, and
  template refers to them project-relatively. Anything still pointing at `references/…`,
  `skills/*/SKILL.md`, or `skills/*/template/…` for a file a subagent has to read is a bug.
  `${CLAUDE_PLUGIN_ROOT}` is used only in the orchestrator, never in a subagent: `/bigin-new-project` and
  `/bigin-upgrade-project` resolve the copy source; every skill's precondition reads `plugin.json`'s
  `version` (`version-check.md` § Workspace version check); and every engine call runs
  `"${CLAUDE_PLUGIN_ROOT}/bin/bigin" …` (v1.9.0+; `hooks/bigin-lint.py` remains as a shim for
  `bin/bigin lint`). Agents get absolute card and task-file paths instead — never the variable.
  An unavailable checker is always **reported**, never read as a pass.
- ~~**The design stage was on the old layout.**~~ **Resolved.** `/prototype-design` is superseded by
  **`/bigin-generate-design`**, which reads `01-Requirements/_ucs/` directly, accepts a feature
  carrying several UCs and a UC spanning several features, and writes `04-UIUX/UX-<NNN> …` plus the
  shared design system. It runs off UCs, not a PRD, so it does not wait on `/approve-uc`. Its rules
  are in `_bigin/conventions/design-conventions.md` — **a separate rulebook on purpose**; design
  conventions and requirement conventions are never merged into this file. `/prototype-design` has
  been deleted; nothing routes to it.
- ~~**The approval stage was on the old layout and the retired `FR-###` artifact.**~~ **Resolved.**
  `/approve-fr` is superseded by **`/approve-uc`**, which reads and writes `01-Requirements/_ucs/`
  directly and re-derives the UC's live state (a human may edit the file directly while reviewing,
  outside `/bigin-transform-signal`) rather than trusting stale status. It touches only the UC's own
  file — promoting/extending any `EN-###` the UC references is **`/sync-entities`**'s job, run
  separately (`registers.md` § Entity Data Model), not part of the same gate any more. `/approve-uc` does **not**
  write an epic or story — that's `/bigin-generate-stories`, a separate stage run when convenient, so `approved`
  means "feature material" (`feature-hub.md` § Feature material) and the stories stage picks it up on its next run rather than
  the approval producing one inline. `/approve-fr` is
  kept only so old references resolve; do not run both.
- **The epic/story stage is built (1.13.0) as `/bigin-generate-stories`; the old `consolidate-prd` stays deleted.** That skill was
  the last thing on the retired pre-migration layout (`.bigin/features/FR-<id>-*.md`, `.bigin/PRD.md`,
  `.bigin/epics.md`, inline `Status:` headings) and on the retired `FR-###` artifact, so it could not
  run against any project on the `01-Requirements/_ucs/`/`_brs/` model. Rather than keep a skill that
  halted unconditionally, it was removed in 1.8.7. Nothing routes to it and nothing should.
  Consequences the rest of the plugin respects:
  - `consolidated` is a **legacy-only, unreachable** UC status. `core.md` § Status vocabularies keeps it defined
    because a pre-migration vault may already carry it; nothing writes it, and nothing may gate on it.
  - `enriched` is unreachable too, for an unrelated reason — enrichment moved off the UC entirely when
    `enrich-feature` was retargeted (below). `draft → approved` is the live path.
  - **Four exits from `/bigin-transform-signal` work:** design (`/bigin-generate-design`), approval
    (`/approve-uc`), epics and stories (`/bigin-generate-stories`, then `/approve-story`), and the human.
    `/bigin-generate-prd` was retired in 1.13.0 — stories take the use cases and the prototype directly.

  `/bigin-generate-stories` reads `01-Requirements/_ucs/UC-<NNN> <Title>.md`, accepts a feature carrying
  **several** UCs plus a UC spanning **several** features (`primary_feature` decides which epic slices it),
  and cuts them into use-case slices, flows first (`use-case.md` § Traceability chain), never one story per
  requirement line. A legacy `PRD-###` is optional context only.
- **`enrich-feature` was retargeted, not migrated on the old axes — it's live.** It never reads
  `.bigin/features/` and was never on the FR→UC axis; it was rescoped from a *per-UC* design (never
  built) to a *per-feature* one (built, live): research the feature's stated scope automatically the
  moment its hub is first created — `/extract-signal` § Step 2a — and let a human re-run it later,
  on demand, via `/enrich-feature` itself. Its only footprint is the feature hub's
  `## Domain Research` section and a report under `01-Requirements/_research/<slug>/`; it never
  touches a UC, `## Domain Concerns` no longer exists as a UC section, and the summary block is
  permanently retired rather than something this skill fills. `/bigin-ba` routes to it for a manual
  refresh, same as any other live stage.

  § Absorbed is real for design: `/bigin-generate-design` stamps `UC-###@version` on `UX-###`,
  re-stamped whole each run, which is what makes "this design is stale" detectable. (`PRD-###` carried
  the same stamp until the PRD stage was retired in 1.13.0.) `/bigin-generate-stories` stamps `EP-###`/`US-###` the same way (1.13.0).
- **Vaults created before the UC migration need a first-touch adoption pass.** `FR-###` and `SCN-###`
  are retired but not deleted (hard rule 1). The adoption path is defined and unattended-safe —
  `_bigin/stages/transform/3-lane-uc.md` § Adopting an existing FR: the first signal that touches a
  feature with FRs mints a UC, lists them in `absorbs:`, stages their existing lines as proposed flow
  steps for the human gate, and stamps each FR `absorbed_by:`. **A feature that receives no new signal
  is never migrated**, by design: nothing rewrites requirement content unprompted. Expect a vault to
  hold both models for as long as some features stay quiet.
- ~~**FR/BR status vocabulary decided but not yet applied where it's written down.**~~ **Resolved.**
  `_bigin/templates/use-case.md`, `_bigin/templates/br.md`, and that skill's `SKILL.md` now
  all use `core.md` § Status vocabularies' list (`draft → enriched → approved → consolidated`, plus
  `needs-clarification`/`removed`) and land results on `draft`, never the retired `in-review`.
  Anything still writing `in-review` or `superseded` onto a UC/BR is a bug.
- ~~**Command order mismatch.**~~ **Resolved in 1.13.0** with the PRD stage's retirement: the Full chain
  is now written `INT → UC/BR → UX (+ prototype) → approve → EP → US`, which is the order things
  actually run — `/bigin-generate-design` runs off `UC-###` as soon as a UC has a main flow, and the
  stories stage reads the design and its prototype snapshot. `UX` is re-run whenever a UC drifts.
- ~~**PRD file granularity was undecided.**~~ **Historical — the PRD stage was retired in 1.13.0.** It had settled on one file per feature:
  `/bigin-generate-prd` writes `02-PRD/PRD-<NNN> <Feature>.md`, one per `FEATURES.md` slug, carrying
  every currently-`approved` UC on that feature (a cross-feature UC lands in its `primary_feature`'s
  PRD, and every participating slug appears in `features:`). This matches how the rest of the vault is
  organised — the hub, the `UX-###`, and the hub's own `prd:` field are all per feature — and it makes
  per-feature staleness detectable via `absorbed:` (§ Absorbed). The two rejected readings, recorded so
  they don't come back: one vault-wide `PRD.md` with a section per feature (no per-feature staleness,
  and `prd:` degrades to a section anchor), and one PRD per UC (a PRD is a feature-level document; per
  UC it is just a reformatted use case). **`UX-###` is settled the same way**: one file per feature,
  `04-UIUX/UX-<NNN> <Feature>.md`, per `_bigin/conventions/design-conventions.md`.
- ~~**Epic/Story file granularity was undecided.**~~ **Resolved (1.13.0) — one folder per epic, one file per
  story.** `03-Epics-Stories/EP-<NNN> <Feature>/` holds the epic, one `US-<NNN> <Title>.md` per use-case slice, and
  `_snapshot/<date>-v<N>/` — the prototype frozen at the time of writing, because a live prototype keeps changing
  under an approved story. One file per story so each can be reviewed and approved on its own; the rejected
  reading — one file per epic with nested stories — made per-story approval and drift clumsy.
- **No front-end app exists yet to consume this vault.** A companion front-end is planned as a
  separate repository (not an Obsidian plugin bundled with this one) — treat every "a front-end
  app" mention above as a future integration point, not a dependency this plugin currently has.
