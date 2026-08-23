---
name: approve-uc
description: Approve a use case (UC) once its open questions are resolved and its content is right. Reprocesses the UC's own live content — the human may have edited it directly while reviewing — then flips its status to `approved` so it's feature material, ready for PRD. Entity promotion and feature-hub refresh are deferred to `/sync-entities`, run separately whenever convenient. Use once a UC is drafted (and, where enrichment runs, enriched) and the human is ready to sign off.
argument-hint: "<UC id, e.g. UC-012>"
---

# Approve UC

Marks a use case approved on the human's explicit call — the point where a reviewed requirement
becomes committed scope. `FR-###` is retired; this skill reads and writes `UC-###` directly under
`01-Requirements/_ucs/`, generating no PRD of its own — the PRD is a separate stage,
`/bigin-generate-prd`, which folds `approved` UCs into their feature's PRD whenever it next runs.

This is the approval gate of the extract → transform → load pipeline. A human reviewing a UC is free
to edit the file directly rather than route every change back through `/bigin-transform-signal` — this
skill's first job is to re-derive the UC's own state from whatever is on disk right now, not trust
whatever a prior run last wrote.

This skill only ever *writes* the UC's own file, so approving several UCs back to back is never
blocked on anything slower than the human's own read-and-decide pace. Entity promotion and feature-hub
refresh — the vault-wide bookkeeping that used to happen inline here — is `/sync-entities`'s job now,
run separately, on its own schedule (§ Entity Data Model). It does, however, *read* a bounded set of
other files — the feature hub(s) and any `BR-###` this UC cites — purely to surface related UCs so the
human reviews this UC's flow with the rest of its neighborhood in view, not in isolation.

> **Artifact Standard:** Outputs:
>> **An approved UC** — `status: approved`, set only after the human confirms, with `version` bumped,
>> `synced: false` so `/sync-entities` knows this UC is waiting on its entity/feature-hub bookkeeping,
>> and a `## Changelog` line if this run corrected anything.

---

## Non-Negotiable Core Rules

* **Never approve on the user's behalf:** approval is a human decision, confirmed against a summary
  they can see.
* **Re-derive, don't trust stale state:** the human may have edited the UC directly while reviewing.
  Re-count `## 5` **Still open** before anything else — a UC with any unresolved `- [ ] Q:` line is
  `needs-clarification`, not approvable, no matter what `status` currently reads
  (§ Open Questions ↔ status consistency).
* **Never fold flow drift into the summary silently:** `## 2`/`## 3` are the two sections
  `/bigin-transform-signal` writes directly, with no human wait (4-sync.md § Part 2) — a UC can reach
  this skill with its flow changed since a human last looked, marked only by a `## Changelog` line
  ending "flagged for ... review" or "reverts from approved, main flow changed". Surface every one of
  those lines since this UC's last approval on its own, before anything else in the summary — that flag
  exists so the human gets a chance to catch a wrong flow, and a summary that buries it defeats the
  point.
* **Entity promotion and feature-hub refresh happen elsewhere:** this skill never *writes*
  `ENTITIES.md`, `01-Requirements/_entities/`, or a feature hub — that's `/sync-entities`, run
  separately (§ Entity Data Model). Setting `synced: false` here is the only handoff needed; don't
  write to those files from this skill even opportunistically.
* **Related-UC context is read-only:** collecting sibling UCs — same feature hub, a shared `BR-###`,
  or another `features:` slug — is only to give the human the full-flow picture before they approve.
  Never open a related UC to edit it, and never write to another UC's file, its hub, or a `BR-###`
  from this skill. If the human decides an edit belongs to one of those related UCs, that edit goes
  back through `/bigin-transform-signal` (its Stage 3 `uc-detector` step already reads this same
  cross-UC context when drafting) — approve-uc stops and waits, it doesn't reach out and make the
  edit itself.
* **No PRD is generated here.** `approved` means the UC is feature material (§ Feature material);
  `/bigin-generate-prd` picks it up on its next run and folds it into
  `02-PRD/PRD-<NNN> <Feature>.md`. Writing PRD content is out of scope for this skill — keep the two
  separate so an approval never silently rewrites a document the sponsor has already read.

---

## Precondition — check this first

Missing `_bigin/conventions/conventions.md` or `_bigin/templates/` → stop, say `/bigin-new-project`
must run first.

Then run `{conventions_reference}` § Workspace version check — one `Grep` of `_bigin/system/project.md`
against the installed plugin's version, compared as semver. Behind → warn and recommend
`/bigin-upgrade-project`; **ahead → stop**, because approving against a rulebook older than the one this
UC's content was written under commits scope under the wrong contract.

`$ARGUMENTS` names a `UC-###` that doesn't exist under `01-Requirements/_ucs/` → say so and stop; don't
guess which file was meant.

With no id given, list every UC not already `approved`/`consolidated`/`removed` as candidates (grouped
by feature) and ask which one.

## Input

Read `01-Requirements/_ucs/UC-<NNN> <Title>.md` for the id in `$ARGUMENTS` — the only file this skill
writes. For related-UC context (step 1 below) it also *reads*, never writes: `primary_feature`'s hub,
each other slug in `features:`, and each `BR-###` in `brs:`. It never reads or writes `ENTITIES.md` or
`01-Requirements/_entities/` — those belong to `/sync-entities`.

## What to do

* **Goal:** convert a reviewed use case into committed scope, ready to hand to whatever comes next
  (design, and the PRD stage), while catching any drift the human's own edit introduced —
  without waiting on, or blocking, the separate entity/feature-hub bookkeeping pass.
* **Action:**
  1. **Reprocess the UC.** Treat the file's current content as authoritative, not whatever a prior run
     last computed:
     * Re-count `## 5` **Still open**. Any unresolved `- [ ] Q:` line → tell the user which question(s)
       are still open and stop; don't ask to approve a UC with an open question
       (§ Open Questions ↔ status consistency's invariant — this holds regardless of what `status`
       currently reads).
       * **Separate "unanswered" from "answered but not folded in".** A line whose `A:` already
         carries an answer is not waiting on the human — it is waiting on a fold-in, because a
         reviewing BA is expected to type answers straight into the file (§ Answering a question) and
         the content only changes when `/bigin-transform-signal` Stage 1 harvests them. Still stop,
         but say which it is: name the answered-not-applied lines and point at "process UC-###" (the
         `bigin-ba` agent's process-the-UC pass, or `/bigin-run`) rather than reporting them back as
         questions the human still owes an answer to. Never fold the answer in from here, and never
         tick the box to clear the count.
     * Find this UC's last human touchpoint: scan `## Changelog` bottom-to-top for the most recent line
       that documents an approval (or, with none yet, treat the `1.0` creation line as the start).
       Collect every line strictly after it — nothing a human has confirmed since — and pull out the
       ones ending "flagged for ... review" or naming a "main flow changed" revert. Those are exactly
       the lines `/bigin-transform-signal` Stage 4 Part 2 writes whenever it direct-writes a `## 2`/
       `## 3` change (4-sync.md § Part 2); this is the flow drift step 2 leads with.
     * Check `## 4`'s rule mirror against each cited `BR-###`'s current statement and enforcement
       point. `## 4` is a read-only mirror (§ Use Case) — if a human edit left it drifted from the BR
       file, refresh the mirror to match; never invent a rule that isn't already in a `BR-###` file.
     * **Say nothing about enrichment.** It's a feature-level pass now (`/enrich-feature`, § Reconciliation
       notes), not a UC-level gate — `enriched` is permanently unreachable as a UC status and
       `draft → approved` is the only live path. Asking "enrichment hasn't run — proceed anyway?" would
       fire on every approval forever for a status this UC will never reach, and a question whose only
       possible answer is "yes" trains the human to click past the summary this whole step exists to
       make them read.
     * **Collect related UCs, read-only.** Read `primary_feature`'s hub `## Use Cases` / `uc:` list
       for sibling ids on the same feature. For each id in `brs:`, read that `BR-###` file's `uc: []`
       to find every other UC the same rule governs. If `features:` names more than one slug, read
       each additional feature's hub `uc:` list too. For every related id found this way (excluding
       this UC itself), open just enough to note `title` + `status` — not a full reprocess of someone
       else's file. Skip anything already `consolidated` or `removed`; they're not live review context.
  2. **Show a short summary.** Lead with the flow drift collected in step 1: quote each flagged
     Changelog line since the last approval, in the order it happened, naming the `INT-###`/source
     behind it — this is what changed in `## 2`/`## 3` that no human has confirmed yet, shown before
     anything else so the human is reviewing the flow itself, not a paraphrase of it. Follow with the
     goal, main-flow step count, and any drift this run corrected in `## 4`. Then list the related UCs
     from step 1 (grouped as same-feature / shared-BR / cross-feature, each with title + status) so the
     human can judge this UC's flow against its neighborhood, not in isolation — then ask whether the
     flow still reads right and the user intends to approve.
     * **If the human says a step or flow now looks wrong:** stop — don't approve. Point at the
       specific `S#`/`A#`/`E#` row in `## 2`/`## 3` that needs a hand edit, or say it belongs back
       through `/bigin-transform-signal` for a proper fold-in, then pick this back up once it's fixed.
       Approving a flow the human just flagged as wrong defeats the reason this summary exists.
     * **If the human flags an inconsistency with a related UC instead:** stop — don't approve, and
       don't edit that other UC from here. Name the related UC and what looks inconsistent, then say
       the fix belongs to `/bigin-transform-signal` (whose `uc-detector` step already reads this same
       cross-UC context when drafting), and pick this back up once it's resolved.
  3. **On confirmation:** set `status: approved` on the UC, bump `version`, set `synced: false`, and
     add one `## Changelog` line noting the approval and anything this run corrected.
  4. **Confirm and point to next.** Tell the user the UC is ready for PRD — `/bigin-generate-prd`
     folds it into its feature's PRD on its next run (worth running once a sitting of approvals ends,
     not after each one), and `/bigin-generate-design` can run off it now, since design waits on
     neither approval nor `/sync-entities`. Epics/stories are still cut by hand
     (§ Reconciliation notes). If this UC's
     `entities: []` isn't empty, mention `/sync-entities` is still pending for it — that is what writes
     each referenced entity up as its **data dictionary** (every field the vault knows for that
     business object, enum values spelled out, § Entity Data Model) and catches up `ENTITIES.md` and
     the feature hub. Run it now, or leave it queued and run it later; nothing here depends on it.
