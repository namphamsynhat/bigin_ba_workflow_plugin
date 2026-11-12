---
name: bigin-run
description: "Drive the Bigin BA pipeline from the main session: read the vault, work out which stage is next, run it, and keep going while nothing needs a decision. Use on \"what's next\", \"move this feature forward\", \"process the inbox\", \"import the mined rules\", \"run the next stage\", \"process UC-00X\" after answers were typed into the file, or \"take this feature through to a prototype\". The only home for a run that fans out to worker agents — never run those inside the bigin-ba agent."
argument-hint: "[feature slug or UC id — omit to pick up whatever is next]"
---

# Bigin Run — the pipeline router

Route; don't reimplement. A stage's semantics live in its `SKILL.md`; bookkeeping lives in the engine
(below `bigin` — the shell function `bigin() { python "${CLAUDE_PLUGIN_ROOT}/lib/bigin/cli.py" "$@"; }`, `python3` if no `python` on PATH); fan-out lives in `${CLAUDE_PLUGIN_ROOT}/workflows/`. This
file only decides **what runs next and how it is dispatched**. Stage status (live/halted) has one source:
`runtime.md` § Reconciliation notes.

**Compact at every stage boundary:** write the stage report, compact, load only the next stage's files.
**You never read an agent transcript or prose report** — between steps you read `bigin run summary <run>`
(≤ 20 lines), `bigin ledger list`, `bigin coverage`. Agents reply with one line; the vault is the state.

## Deciding what runs next

With no argument, sweep; with a slug or UC id, scope to it. Determine the stage from the vault, don't ask.

```text
1  no _bigin/system/project.md                         → /bigin-new-project, stop
2  a precondition reports workspace_version behind     → /bigin-upgrade-project (bigin migrate plan/all)
                                          ahead        → STOP, relay verbatim
3  rule cards to import (grounding: codebase|both)     → bigin intake codebase --cards … [--assignment …]
                                                         --unmapped-out _runs/<run>/tasks/unmapped.in.json
                                                         (0 LLM calls; only the unmapped remainder goes to
                                                         one signal-filer task)
3b jira_provider set and the human asked for a sweep
   ("process the inbox", "pull Jira")                 → /bigin-intake jira (fetch only; the engine appends
                                                         just the new comments / description revisions)
3c the human starts a sprint ("new sprint", a ticket
   list or a Jira sprint name)                        → /bigin-intake sprint <name> KEY … (new watch list;
                                                         the old sprint's tickets stop being swept)
                                                         + after every extract while a sprint is set:
                                                         `bigin intake jira-sprint --report` → relay the
                                                         new-feature / update / bug split
3d the human says the client removed a ticket
   (cancelled, a deleted key)                         → bigin note withdraw <INT> --reason "<their words>"
                                                         --by "<who, where, date>"
3e the human says the client dropped a whole feature
   (cost, market fit)                                 → bigin feature withdraw <slug> --reason … --by …
                                                         — relay what it removed, kept and flagged stale;
                                                         then transform (5) retracts the rest
4  00-Inbox/ note at status: raw, or a newly ticked
   note question (communication and jira notes)       → extract   (workflows/extract.js) — ends with the
                                                         Analyze phase: relay each note's ## Analysis
                                                         conflicts and questions to the human
5  bigin ledger list shows open sets whose question is
   answered, or hubs have new/held/retract rows       → transform (workflows/transform.js)
                                                         Jira tickets draft here as soon as they are filed —
                                                         well before Ready for Dev — so the dev team can
                                                         review the flow and ask the PM in Jira
5a conflict/held rows in a code-grounded vault         → adjudicate (inside transform; alone:
                                                         workflows/adjudicate.js)
5b "process UC-###" — answers typed in the file        → bigin-ba's process-the-UC pass (cards/ba-drive.md)
6  a UC has a drafted § 2 and no current design        → STOP, name `/bigin-generate-design` for the BA to type
6b THE HUMAN asks for a prototype (never you)          → /bigin-render-design-od — for a Jira ticket this is
                                                         the quick design the dev team shares with the PM
7  a UC is clear and the human is ready to sign off    → the review flow (cards/ba-review.md) — never headless;
                                                         a UC built from a Jira ticket also needs the ticket
                                                         at Ready for Dev (`bigin intake jira-gate --uc`);
                                                         relay every `READY FOR DEV → approve UC-###` a sweep prints
8  approved UCs with synced: false                     → /sync-entities, when convenient
9  approved UCs with no current epic/stories           → STOP, name `/bigin-generate-stories` for the BA to type
10 draft stories the human has reviewed               → /approve-story — human-only, like step 7
```

Steps 3–5 are momentum: run them back to back. Steps 6, 6b and 9 name skills with `disable-model-invocation: true`
(`/bigin-generate-design`, `/bigin-render-design-od`, `/bigin-generate-stories`): this session cannot call them, so say
which command to type and stop — never try the Skill tool on them. Step 7 is the only decision point; 8–9 lag it freely.
6b is never momentum — a render is something a person asks for.

## Dispatching a fan-out stage

```text
1  RUN=$(bigin run new --stage <extract|transform> --scope <slug|inbox>)
2  Workflow tool available and opted in →
     Workflow(scriptPath: <repo root>/_runs/RUN/workflows/<stage>.js,   ← staged by `run new`; the
              Workflow tool rejects a scriptPath in the plugin cache (outside the working directory)
              args: {run: RUN, vault: <repo root>, plugin_root: ${CLAUDE_PLUGIN_ROOT},
                     features: [slug…] | notes: [INT-…], grounding: <project.md grounding>,
                     max_agents: 6})
     a kill or rate-limit → re-run with resumeFromRunId and the SAME run id: finished tasks are skipped
     (results.jsonl), and every vault write is engine-only and atomic, so there is no half-written file.
   Otherwise — the same steps with one Agent call per judgement task. The loop has ONE home per stage; follow it,
   don't restate it: extract → skills/extract-signal/references/agent-dispatch.md ·
   transform → skills/bigin-transform-signal/references/agent-dispatch.md
3  cost: `bigin ingest --run` already recorded an estimate per agent output; when a task notification carries a
   <usage> block, add the measured figure: bigin metrics add --run RUN --stage … --task … --agent … --usage "<usage…>"
4  bigin run summary RUN   → the stage report; bigin metrics report --run RUN flags budget overruns
5  bigin lint --full        → the blocking gate at the stage boundary
```

Inline thresholds (one feature with ≤ 3 qualified rows; 1–2 features for stories; design always dispatches) are the stages' own —
read them in their dispatch references. Never talk yourself past one to avoid a dispatch.

## Grounding

`project.md grounding:` `communication` (mail/meetings: extractor + auditor), `codebase` (rule cards:
`bigin intake codebase`, adjudication on), or `both`. `conflict_policy: code-first | ask` decides whether code
settles a factual conflict or raises a gated question. `repos/` is read-only for every command and agent.

## Reviewing, and handing work to `bigin-ba`
The review flow and the process-the-UC pass are `bigin-ba`'s cards (`cards/ba-review.md`, `cards/ba-drive.md`,
`cards/ba-triage.md`) — follow them in this session; don't restate them. Dispatch `bigin-ba` unattended only
when the human is live on UC-A and a different UC/feature needs a slower inline-sized stage; anything over a
threshold comes back here.

## Always
Questions a run raised pass the answer-it-yourself gate (`cards/ba-triage.md`, buckets 1–4) before a human
sees them — a headless transform raises them unfiltered; relay only what is genuinely the client's or team's.
Capture before interpreting. `AskUserQuestion` for routing decisions only, never to relay a `- [ ] Q:`.
Never approve on a human's behalf, set `status` by hand, or run the load stages from inside `bigin-ba`.

After a run that leaves client or dev questions open, run `scripts/bigin questions list` and
`scripts/bigin questions pack` (writes `06-Outbox/<date>-<Jira key or owner>.md`, one paste-ready file per
recipient, nothing posted) and tell the BA which packs to paste; once pasted, `scripts/bigin questions sent
<pack>` stamps them so they are not offered twice. A reply that keeps a pack's `[q:xxxxxx]` tag is matched to its
question automatically at intake.

## Output
Per stage: what ran, what the engine wrote (from `run summary`), what was gated/drifted/parked (from
`ledger list`), coverage, and what runs next.

End every run with `scripts/bigin digest --for ba` (what came in, changed, was decided, is waiting, is ready to
approve, is stale downstream, spend). Mention that `--for client` (decided / changed / waiting, ids moved into a
trailing ref) and `--for dev` (approved changes, stale downstream, delta stories, dev questions) render the same
facts for the other two audiences; `--write` saves any of them to `06-Outbox/`. No LLM is involved.
