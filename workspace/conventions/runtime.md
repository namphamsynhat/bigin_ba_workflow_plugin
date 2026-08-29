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
| PRD | `UC-###@version` for each approved UC folded into it, plus `UX-###@version` in `design_absorbed:` for the design it reported | `/bigin-generate-prd` — **implemented**, re-stamped whole every run |
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
cannot leave a false "current" claim behind. Two of the three rows above are live —
`/bigin-generate-design` for `UX-###` and `/bigin-generate-prd` for `PRD-###`, so "this design is
stale" and "this PRD has drifted from its use cases" are both detectable today. The epic/story row is
still planned: until it's built, treat any UC edited after its feature's epics were cut as needing a
manual re-check, and note that explicitly in the report rather than assuming they're still accurate.

## Resumable unattended apply (checkpoint + idempotent writes)

An unattended fold-in — matching a human's already-written inline answer to its UC and folding it
in, whether that's `/bigin-transform-signal`'s Stage 1 fold-in, `/extract-signal`'s per-note batch
processing, or a future `--auto` mode — is a multi-file write: the UC itself, the feature hub,
sometimes `FEATURES.md`, sometimes the source INT note. Nothing here runs inside a database
transaction — the process can be killed between any two of those writes by an external timeout or
a session running out of budget, which kills the parent process while an orphaned child keeps
mutating files in the background. Applying an answer directly (rather than staging it for a later
human confirm) removes one failure mode but must not introduce a worse one — a fold-in that's
half-applied across files, with no way to tell "not started" from "partially done" from "fully
done."

The fix is the same one durable-execution agent runtimes converge on for exactly this problem —
checkpointed writes, idempotent retries, an append-only decision trail — applied with the vault's
existing tools, not a new ledger file:

1. **Dedup-check before writing anything.** Before applying an answer, check whether it's already
   landed: does the UC's `## Changelog` already cite this INT id's fold-in, or does the
   `## Open Questions` line already read as resolved (not merely ticked) rather than unticked? If
   yes, this run is a retry of an already-completed apply — do nothing to that UC, and move
   straight to reconciling any mirror that's still behind (step 3). Never re-append a changelog or
   Discussion line just because this run started before checking.
2. **The UC's own file write is the checkpoint — make it one atomic write, and make it first.**
   Compose the *entire* change (requirement body wording, `version` bump, `## Changelog` line,
   re-counted `status`) and write the UC file once. Before that single write lands, nothing has
   changed on disk — a kill at any point up to here leaves the note exactly as it was, correctly
   still eligible for a future run to pick up (no special "in progress" marker needed; there is
   nothing to distinguish from "not started yet"). After it lands, the fold-in is **done** —
   everything downstream is a re-derivable mirror, never the source of truth.
3. **Mirrors are always safe to reconcile, never a one-shot append.** The feature hub's Signal Log
   row, `FEATURES.md`, and the source INT note's own tick/status are all *read from the UC's
   current state* and corrected to match — flip a Signal Log row to `applied` if the UC it points
   at now shows the fold-in, tick the INT note's copy if the UC copy is already resolved. Setting
   an already-correct mirror field again is a no-op, not a duplicate, so this step never needs its
   own resume logic: run it every time, unconditionally, whether this is the first pass or the
   tenth.
4. **A subsequent run's gate check is therefore a 3-way read, not a 2-way one.** For any UC
   carrying a fold-in candidate: (a) **genuinely unanswered** — the INT note's `A:` line is still
   blank → wait for a human, not eligible. (b) **already applied** — the UC's
   `## Changelog`/body already reflect it → not eligible for another apply, but still worth a
   mirror-reconciliation pass (step 3) in case a prior run's kill landed the UC write but not the
   hub refresh. (c) **neither** → apply it now (steps 1–3). This replaces a bare "is the box
   ticked?" check, which can't tell (b) from a half-applied (c) on a resumed run.

No new state file, ledger, or `status:` value is introduced — the artifacts remain the only ground
truth. A stuck fold-in is never a dead end: the next run of the same skill re-derives exactly
where it left off from steps 1 and 4 above, applies what's missing, and reconciles the rest — safe
to invoke repeatedly, including from a fresh session with no memory of the interrupted one.

## Reconciliation notes for this plugin

Concrete gaps between this document and the plugin's actual skills, collected here instead of as
scattered inline caveats — resolve and delete each line as the corresponding skill is migrated.

- ~~**Plugin-internal paths were unreachable at runtime.**~~ **Resolved (plugin 1.2.0).** The rulebook
  and templates are now materialized into the project by `/bigin-new-project`
  (`_bigin/conventions/`, `_bigin/stages/`, `_bigin/templates/`), and every skill, dispatch prompt, and
  template refers to them project-relatively. Anything still pointing at `references/…`,
  `skills/*/SKILL.md`, or `skills/*/template/…` for a file a subagent has to read is a bug.
  `${CLAUDE_PLUGIN_ROOT}` has exactly four legitimate uses, all of them in the orchestrator and none
  in a subagent: `/bigin-new-project` § 2 and `/bigin-upgrade-project` § 5 resolve the copy source;
  every skill's precondition reads `plugin.json`'s `version` for `version-check.md` § Workspace version check; and
  `5-status.md` Part 3 plus `/extract-signal`'s batch check invoke the plugin's own deterministic
  checker (`hooks/bigin-lint.py --full`). A stage file may name that path because Part 3 and the batch
  check both run in the orchestrator — never hand it to a dispatched agent, which cannot resolve it.
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
  write a PRD — that's `/bigin-generate-prd`, a separate stage run when convenient, so `approved`
  means "feature material" (`feature-hub.md` § Feature material) and the PRD picks it up on its next run rather than
  the approval producing one inline. `/approve-fr` is
  kept only so old references resolve; do not run both.
- **The epic/story stage was never built, and `consolidate-prd` has been deleted.** That skill was
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
    (`/approve-uc`), PRD (`/bigin-generate-prd`), and the human. Only the epics/stories exit is
    missing, and it is missing because nobody has built it — not because a skill is broken.

  **Building it remains the largest open item in this plugin.** A replacement would read
  `01-Requirements/_ucs/UC-<NNN> <Title>.md`, accept a feature carrying **several** UCs plus a UC
  spanning **several** features (`primary_feature` decides the chain), and decompose `PRD-###` — which
  is now a real, versioned input — into use-case slices, flows first (`use-case.md` § Traceability chain), never one
  story per requirement line.
- **`enrich-feature` was retargeted, not migrated on the old axes — it's live.** It never reads
  `.bigin/features/` and was never on the FR→UC axis; it was rescoped from a *per-UC* design (never
  built) to a *per-feature* one (built, live): research the feature's stated scope automatically the
  moment its hub is first created — `/extract-signal` § Step 2a — and let a human re-run it later,
  on demand, via `/enrich-feature` itself. Its only footprint is the feature hub's
  `## Domain Research` section and a report under `01-Requirements/_research/<slug>/`; it never
  touches a UC, `## Domain Concerns` no longer exists as a UC section, and the summary block is
  permanently retired rather than something this skill fills. `/bigin-ba` routes to it for a manual
  refresh, same as any other live stage.

  `feature-hub.md` § Feature Hub's "Maintenance contract" row for the epic/story stage describes a target, not a
  current read/write path — `enrich-feature`'s row there is already current.
  § Absorbed is now real for both load stages: `/bigin-generate-design` stamps `UC-###@version` on
  `UX-###`, and `/bigin-generate-prd` stamps it on `PRD-###` (plus `UX-###@version` in
  `design_absorbed:`) — both re-stamped whole each run, which is what makes "this design is stale" and
  "this PRD has drifted" detectable. Only the epic/story row in that table remains planned.
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
- **Command order mismatch**: this document's Full chain is `PRD → EP → US → UX`, but design does not
  sit at the end of it — `/bigin-generate-design` runs off `UC-###` as soon as a UC has a main flow,
  needing neither approval nor a PRD. In practice the two load stages run in either order, and
  `/bigin-generate-prd` is the one that depends on the other: its § 9 reports whatever design exists,
  and says so plainly when none does. So the real order is `INT → UC/BR → (UX ∥ approve) → PRD → EP →
  US`, with `UX` re-run whenever a UC drifts. Decide whether the chain notation above should say so
  explicitly rather than implying a strict sequence nothing follows.
- ~~**PRD file granularity was undecided.**~~ **Resolved — PRD is one file per feature.**
  `/bigin-generate-prd` writes `02-PRD/PRD-<NNN> <Feature>.md`, one per `FEATURES.md` slug, carrying
  every currently-`approved` UC on that feature (a cross-feature UC lands in its `primary_feature`'s
  PRD, and every participating slug appears in `features:`). This matches how the rest of the vault is
  organised — the hub, the `UX-###`, and the hub's own `prd:` field are all per feature — and it makes
  per-feature staleness detectable via `absorbed:` (§ Absorbed). The two rejected readings, recorded so
  they don't come back: one vault-wide `PRD.md` with a section per feature (no per-feature staleness,
  and `prd:` degrades to a section anchor), and one PRD per UC (a PRD is a feature-level document; per
  UC it is just a reformatted use case). **`UX-###` is settled the same way**: one file per feature,
  `04-UIUX/UX-<NNN> <Feature>.md`, per `_bigin/conventions/design-conventions.md`.
- **Epic/Story file granularity is still undecided** — only their status vocab is decided
  (`draft → approved`, `core.md` § Status vocabularies). This document assumes `EP-###`/`US-###` are each their
  own file with their own id. Decide per-artifact files or the flat model when that stage is built — and cut them as **use-case
  slices**, flows first (`use-case.md` § Traceability chain), not one story per requirement line. `PRD-###` is now
  settled either way, so an epics stage has a real, versioned input to decompose.
- **No front-end app exists yet to consume this vault.** A companion front-end is planned as a
  separate repository (not an Obsidian plugin bundled with this one) — treat every "a front-end
  app" mention above as a future integration point, not a dependency this plugin currently has.
