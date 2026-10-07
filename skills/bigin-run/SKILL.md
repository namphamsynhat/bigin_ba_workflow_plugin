---
name: bigin-run
description: Drive the Bigin BA pipeline from the main session — read the vault, work out which stage runs next, run it, and keep going while nothing needs a decision. Use when asked to "move this feature forward", "what's next", "what's next on UC-00X", "process the inbox", "drain the intake queue", "import the mined rules", "run the next stage", "take this feature through to a prototype", "process UC-00X" / "process the UC" after a team BA typed their answers straight into the file, or "drive the pipeline". **This is the only home for a run that fans out.** Extract, multi-feature transform, adjudication, design and stories runs dispatch named workers — through the Workflow tool (workflows/*.js) when available, else one Agent call per task — and a subagent cannot dispatch subagents, so they are driven from here, never from inside the `bigin-ba` agent.
argument-hint: "[feature slug or UC id — omit to pick up whatever is next]"
---

# Bigin Run — the pipeline router

Route; don't reimplement. A stage's semantics live in its `SKILL.md`; bookkeeping lives in the engine
(`${CLAUDE_PLUGIN_ROOT}/bin/bigin`, below `$BIGIN`); fan-out lives in `${CLAUDE_PLUGIN_ROOT}/workflows/`. This
file only decides **what runs next and how it is dispatched**. Stage status (live/halted) has one source:
`runtime.md` § Reconciliation notes.

**Compact at every stage boundary:** write the stage report, compact, load only the next stage's files.
**You never read an agent transcript or prose report** — between steps you read `$BIGIN run summary <run>`
(≤ 20 lines), `$BIGIN ledger list`, `$BIGIN coverage`. Agents reply with one line; the vault is the state.

## Deciding what runs next

With no argument, sweep; with a slug or UC id, scope to it. Determine the stage from the vault, don't ask.

```text
1  no _bigin/system/project.md                         → /bigin-new-project, stop
2  a precondition reports workspace_version behind     → /bigin-upgrade-project (bigin migrate plan/all)
                                          ahead        → STOP, relay verbatim
3  rule cards to import (grounding: codebase|both)     → $BIGIN intake codebase --cards … [--assignment …]
                                                         --unmapped-out _runs/<run>/tasks/unmapped.in.json
                                                         (0 LLM calls; only the unmapped remainder goes to
                                                         one signal-filer task)
4  00-Inbox/ note at status: raw, or a newly ticked
   note question (communication notes only)           → extract   (workflows/extract.js)
5  $BIGIN ledger list shows open sets whose question is
   answered, or hubs have new/held rows               → transform (workflows/transform.js)
5a conflict/held rows in a code-grounded vault         → adjudicate (inside transform; alone:
                                                         workflows/adjudicate.js)
5b "process UC-###" — answers typed in the file        → bigin-ba's process-the-UC pass (cards/ba-drive.md)
6  a UC has a drafted § 2 and no current design        → /bigin-generate-design
6b THE HUMAN asks for a prototype (never you)          → /bigin-render-design-od
7  a UC is clear and the human is ready to sign off    → the review flow (cards/ba-review.md) — never headless
8  approved UCs with synced: false                     → /sync-entities, when convenient
9  approved UCs with no current epic/stories           → /bigin-generate-stories
10 draft stories the human has reviewed               → /approve-story — human-only, like step 7
```

Steps 3–6 are momentum: run them back to back. Step 7 is the only decision point; 8–9 lag it freely.
6b is never momentum — a render is something a person asks for.

## Dispatching a fan-out stage

```text
1  RUN=$($BIGIN run new --stage <extract|transform> --scope <slug|inbox>)
2  Workflow tool available and opted in →
     Workflow(scriptPath: <repo root>/_runs/RUN/workflows/<stage>.js,   ← staged by `run new`; the
              Workflow tool rejects a scriptPath in the plugin cache (outside the working directory)
              args: {run: RUN, vault: <repo root>, plugin_root: ${CLAUDE_PLUGIN_ROOT},
                     features: [slug…] | notes: [INT-…], grounding: <project.md grounding>,
                     max_agents: 6})
     a kill or rate-limit → re-run with resumeFromRunId and the SAME run id: finished tasks are skipped
     (results.jsonl), and every vault write is engine-only and atomic, so there is no half-written file.
   Otherwise (fallback loop, restructure plan § B.5) — same steps, one Agent call each:
     $BIGIN worklist <stage> <scope> --out _runs/RUN/tasks/<task>.in.json
     Agent(<named worker>, prompt = card path + .in.json path + .out.json path)   ← replies ONE line
     $BIGIN ingest <out> --run RUN     → errors go back to the SAME agent once (SendMessage), then park
     $BIGIN apply <out> --run RUN      (transform) · note write-signals / audit-apply · file apply (extract)
     transform: route (uc-router Phase A) → $BIGIN mint route --spec <route.out.json> → resume the same
     uc-router for Phase B → apply → adjudicate (code-grounded) → $BIGIN hub refresh <slug>
     extract: extractor per note → auditor only when audit_owed → filer per note, SERIALLY → lint --full
3  after every task notification: $BIGIN metrics add --run RUN --stage … --task … --agent … --usage "<usage…>"
4  $BIGIN run summary RUN   → the stage report; $BIGIN metrics report --run RUN flags budget overruns
5  $BIGIN lint --full        → the blocking gate at the stage boundary
```

Inline thresholds (one feature with ≤ 3 qualified rows; 1–2 features for design/stories) are the stages' own —
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
Capture before interpreting. `AskUserQuestion` for routing decisions only, never to relay a `- [ ] Q:`.
Never approve on a human's behalf, set `status` by hand, or run the load stages from inside `bigin-ba`.

## Output
Per stage: what ran, what the engine wrote (from `run summary`), what was gated/drifted/parked (from
`ledger list`), coverage, and what runs next.
