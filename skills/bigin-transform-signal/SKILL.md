---
name: bigin-transform-signal
description: This skill is used when after /extract-signal has filed signals, or when asked to derive use cases or requirements, write or update a UC, process the signal backlog, qualify signals, or check whether a feature's pending UC/BR changes have been answered. Transforms new/held signals from a Feature Hub into drafted/updated Use Cases (UC), Business Rules (BR), and Design Directives through the bigin engine — agents emit JSON change sets, `bin/bigin apply` writes every artifact once, gated changes wait in the ledger on a written question — then checks each touched feature's use-case set as a set, recording what nobody has described as a `## Coverage Gaps` row on the hub. Resumable, never blocking on a live human. It never promotes an Entity (EN) doc — /sync-entities is the only skill that promotes one.
argument-hint: "[feature slug, or omit for all pending, or resume <run-id>]"
---

# Bigin Transform Signal

Turn `new`/`held` signals on a Feature Hub's `## Signal Log` into **Use Cases** (UC), **Business Rules**
(BR), and **Design Directives**. **LLM for judgement, the engine for bookkeeping, JSON between them, one
write per artifact:** `uc-router` decides which UC a signal belongs to and writes the final text as change
sets (`lib/bigin/schema/changeset.json`); `"${CLAUDE_PLUGIN_ROOT}/bin/bigin" apply` validates and lands
them, flips the Signal Log rows, syncs links, refreshes hubs, and re-counts status. No agent edits a
UC, BR, or hub file.

**The output is a use case, not a list of fragments.** One `UC-###` = one user goal: actors and trigger
(`## 1`), the flow (`## 2`), branches (`## 3`), a read-only mirror of its rules (`## 4`), open questions +
decision log (`## 5`). A UC may span features and is updated in place. `FR-###` is retired.

Standard: `use-case.md` § Use Case, `feature-hub.md` § Feature Hub, `core.md` § Status vocabularies,
`questions.md`. Procedure: the stage files below. Agents read their **card** (`cards/router.md`,
`cards/adjudicator.md`), never these.

## What "the gate" is

A change set lands **now** unless it carries `gate: {question, blocks: true}` — then the engine appends
it to the ledger (`01-Requirements/_ledger/<slug>.jsonl`), puts the question on the artifact, and renders
the pending text read-only as `## Pending changes`. Nothing gated lands until a human fills that
question's `A:`; `bigin ledger release` (Stage 1 of the next run) applies it.

```text
change set, no gate   → lands this run; the Changelog line (and review flag when § 2 changed) is what
                        tells /approve-uc a human should look — it is NOT pre-reviewed
change set + gate      → waits in the ledger until the question is answered
text reworded by a human since the worklist was built → DRIFT: not applied, one question naming both
                        wordings; identical text → counts as applied
```

`## Discussion` is for human discussion only. Legacy staged entries (v1.8 vaults) are converted once by
`bin/bigin migrate discussion-to-ledger`.

## Setup

```text
BIN="${CLAUDE_PLUGIN_ROOT}/bin/bigin"          # the orchestrator runs it; subagents never do
version-check.md § Workspace version check      # behind → recommend /bigin-upgrade-project; ahead → stop
project.md engine: legacy                      # → this vault is mid-migration: follow the v1.8.x copy of
                                               #   this skill (plugin ≤ 1.8.12) for ONE minor version, then upgrade
legacy staged entries present? (grep {uc_dir}/{br_dir} for `^- \*\*INT-\d+\*\* \(staged`)
                               → $BIN migrate discussion-to-ledger   (snapshots first) — then continue
RUN=$($BIN run new --stage transform --scope <slug|all>)   # or the run id after `resume`
```

Missing `_bigin/conventions/`, `_bigin/stages/`, or `_bigin/templates/` → stop: `/bigin-new-project` first.

## Execution order

```text
scope = $ARGUMENTS slug, else every hub with new/held/conflict/question rows or open ledger entries

1  release   $BIN ledger release · re-entry · orphan answers                  [1-foldin.md]
2  qualify   gate each new/held row; outcomes via $BIN hub flip               [2-qualification.md]
3  route     uc-router Phase A → $BIN mint route → Phase B → change sets      [3-routing.md, 3-lane-*.md]
4  apply     $BIN ingest + apply · adjudicate (code-grounded) · conflict + coverage check
                                                                              [4-sync.md, 4b-coverage.md]
5  status    $BIN status · hub refresh · coverage · lint --full · report      [5-status.md]
```

Stage 1 first harvests answers written since the last run. Load a stage file when you reach it.

## Orchestration — call the Workflow tool

**This skill instructs you to run `workflows/transform.js` through the Workflow tool whenever that tool is
available** (invoking this skill is the opt-in). Stages 3–4 per feature and the close step run inside it:

```text
Workflow(scriptPath: "${CLAUDE_PLUGIN_ROOT}/workflows/transform.js",
         args: {run: $RUN, vault: <vault root>, plugin_root: "${CLAUDE_PLUGIN_ROOT}",
                features: [<in-scope slugs with qualified rows>], grounding: <project.md grounding>,
                max_agents: 6})
```

Stages 1–2 run before it (they are cheap and mostly engine commands); Stage 5 after it. Between steps
read only `$BIN run summary $RUN` (≤ 20 lines) and the workflow's returned JSON — never agent transcripts.

**Fallback — no Workflow tool.** Run the same loop with `Agent` calls, per feature (features in parallel,
≤ 4; within a feature sequential) — `references/agent-dispatch.md`:

```text
$BIN worklist route <slug> --out _runs/$RUN/tasks/<slug>.route.in.json
Agent(uc-router, Phase A) → <slug>.route.out.json ; $BIN ingest … --kind route --run $RUN
$BIN mint route --spec _runs/$RUN/tasks/<slug>.route.out.json        # serial, locked
SendMessage(same uc-router, Phase B) → <slug>.changesets.out.json ; $BIN ingest … --kind changesets
$BIN apply _runs/$RUN/tasks/<slug>.changesets.out.json --run $RUN
grounding codebase|both and conflict/held rows → adjudicate (4-sync.md § Part 3)
$BIN hub refresh <slug>
```

A schema error from `ingest` goes back to the SAME agent once (SendMessage); a second failure parks the
feature in the report. After every task notification: `$BIN metrics add --run $RUN --stage transform
--task <task> --agent <name> --feature <slug> --usage "<the usage block>"`.

## Lanes

| Lane | Change sets | Guide |
|---|---|---|
| UC | `new_step_after`/`replace_step`/`drop_step`, `new_flow`/…, `set_field`/`append_note` on § 1/§ 6, `create_uc` via Phase A `new` | `3-lane-uc.md` |
| BR | `create_br`, `set_rule`, `append_rule_clause`, `mirror_br` on each governed UC | `3-lane-br.md` |
| Design | `add_directive` (hub); durable preferences → `add_principle` | `3-lane-design.md` |
| Entity | citation only (`link` field `entities` once an EN id exists) — never promoted here | `3-routing.md` § Entity |
| Context | `set_field` § 1 Business Need / Goal; `link` field `pain_points` | `3-lane-uc.md` |

## Must not change (whatever the engine does)

- `/approve-uc` is the only way a UC becomes approved; nothing here writes `approved`/`removed`.
- Questions are add-only; a box is ticked only with a filled `A:`; intent questions are never auto-ticked.
- Step/flow ids are never renumbered; a dropped step keeps its id (`Dropped — <reason>`).
- Every change carries `trace` (INT rows, hub rows, XR ids in codebase mode).
- Asymmetries are specified per surface; `repos/` is never written; no secret, credential, e-mail address,
  OTP-bypass value or internal hostname is reproduced.

## Failure modes

- **Drafting from an unqualified signal** — reaches `/approve-uc` looking identical to a sound one.
- **Never asking whether the feature's use cases ADD UP** — every artifact looks right while nothing says
  how the thing they manage is created or retired. Stage 4 Part 4 (`4b-coverage.md`) is the only pass that
  reads the set.
- **Minting a second UC for the same goal**, or re-deciding new-vs-update in Phase B.
- **Hand-editing a UC/BR/hub** instead of emitting a change set — it bypasses drift detection, the
  Changelog trace, and idempotence, and the engine refuses its next write if the file changed under it.
- **Gating what needs no decision, or not gating what does** — a manufactured question parks a ready UC;
  an ungated guess lands unreviewed.
- **Inventing a step, validation, or branch nobody stated** — missing → a question.
- **Writing a rule statement into a UC's `## 4`** — use `mirror_br`; the BR is the source.
- **Deciding a conflict** — recency settles a supersession, never a disagreement.
- **Leaving an answered `conflict`/`question` row where it is** — Stage 1 § Re-entry.
- **Trusting a report instead of the engine's counts** — read `run summary` and the apply result.

## Model

Tiers are pinned in agent frontmatter (`agents/uc-router.md`, `agents/code-adjudicator.md`) and recorded on
each card; never override them from a dispatch prompt. The engine runner steps inside the workflow use
`haiku` — they only execute commands.

## Additional resources

- `references/agent-dispatch.md` — the fallback loop: what each dispatch prompt carries.
- `references/use-case-standard.md` — where the UC's shape comes from. Not needed for a run.
- `workflows/transform.js`, `workflows/adjudicate.js` — the orchestration itself.
