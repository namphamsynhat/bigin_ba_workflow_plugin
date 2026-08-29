---
name: bigin-run
description: Drive the Bigin BA pipeline from the main session — read the vault, work out which stage runs next, run it, and keep going while nothing needs a decision. Use when asked to "move this feature forward", "what's next", "what's next on UC-00X", "process the inbox", "drain the intake queue", "run the next stage", "take this feature through to a prototype", "process UC-00X" / "process the UC" after a team BA typed their answers straight into the file, or "drive the pipeline". **This is the only home for a run that fans out.** Four stages dispatch named subagents, and a subagent cannot dispatch subagents, so `/extract-signal` and any multi-feature transform, design, or PRD run must be driven from here — never from inside the `bigin-ba` agent, which has no `Agent` tool and would otherwise pull every transcript into the one context the fan-out exists to protect.
argument-hint: "[feature slug or UC id — omit to pick up whatever is next]"
---

# Bigin Run — the pipeline router

Route; don't reimplement. This skill carries **which stage runs when** and nothing else. Every stage's
own semantics — what it reads, what it writes, what it refuses, what statuses it sets — live in that
stage's `SKILL.md`, and the shared standard lives in `_bigin/conventions/`. When a
stage's behaviour matters, read its `SKILL.md`; never summarize one back to the user as fact. A
pipeline description copied into a router goes stale the day a stage changes, and then reads as
authoritative while being wrong.

Migration status has one source too: **`runtime.md` § Reconciliation notes** says which stages are
live, which are halted, and what each halted one needs. Read it once per session; never hardcode a
per-stage verdict here.

**Load one stage's rulebook at a time.** `_bigin/conventions/` is one file per concern —
`core.md`, `use-case.md`, `feature-hub.md`, `intake.md`, `questions.md`, `registers.md`, `runtime.md`,
plus the `design-*.md` set. `conventions.md` is a map and holds no rules; each stage's `SKILL.md`
names the files that stage needs. Open those, and no others.

## Compact at every stage boundary

You are the one context that spans the whole pipeline, so you are the one that compounds. A run that
walks intake → extract → transform → design → PRD in one unbroken context is re-submitting the
transcripts of stage 1 on every tool call of stage 5.

```text
at each stage boundary, before starting the next stage:
  1  write the stage's report          # the vault is the state; the report is the handoff
  2  COMPACT                           # keep the report and the run's scope, drop the rest
  3  load the NEXT stage's rulebook only — its SKILL.md's Paths table names the files
```

What survives a compaction is the report and the scope: which features, which ids, what the last
stage changed, what it handed back. What does not is every rulebook the last stage read, every hub it
opened, and every subagent transcript — all of it is on disk and re-readable in seconds, and none of
it is needed to run the next stage.

**Never carry a stage's rulebook into the next stage.** The files are sized to be read whole, one
stage's worth at a time; that is the point of the split. Re-reading `feature-hub.md` in the design
stage costs a few seconds once. Carrying it costs its full length on every remaining tool call.

## Why this runs in the main session

`/extract-signal`, `/bigin-transform-signal`, `/bigin-generate-design`, and `/bigin-generate-prd` are
each architected around subagent fan-out — one worker per note, one per feature — specifically to keep
raw transcripts, per-feature drafting, and whole-UC reads out of the orchestrator's context. Dispatching them needs the `Agent` tool, which
only this session has: the `bigin-ba` agent's `tools:` list does not include it, and a subagent cannot
spawn one anyway on the depth budget the stages assume.

```text
so the split is not a preference, it is a capability boundary:

  needs fan-out → HERE, always
      /extract-signal                      every run — 2a/2c are mandatory named-worker dispatch
      /bigin-transform-signal              a run spanning several features, or one feature with
                                           four or more qualified signals
      /bigin-generate-design               three or more features in one run
      /bigin-generate-prd                  three or more features in one run

  runs inline anywhere → here or in the bigin-ba subagent, whichever fits
      /bigin-intake · /approve-uc · /sync-entities · /bigin-new-project · /bigin-upgrade-project
      /bigin-transform-signal              one feature, three or fewer qualified signals, or an
                                           FR adoption   (its references/agent-dispatch.md § Skip)
      /bigin-generate-design               one or two features                    (same file § Skip)
      /bigin-generate-prd                  one or two features    (its references/agent-dispatch.md)
```

Those inline thresholds are the stages' own, documented in their dispatch references — read them there
rather than trusting this summary, and never talk yourself past one to avoid a dispatch. A feature over
the threshold run inline pays a duplicate full-hub read per worker it skipped, in the one context that
then has to hold every other feature too.

## The pipeline you route through

ETL: **extract** intake into per-feature signals → **transform** them into reviewed use cases and business rules → **load** them into design, approval, and a per-feature PRD. Only epics/stories are still missing from the load side.

| # | Skill | Route to it when | Decision point? |
|---|---|---|---|
| 1 | `bigin-new-project` | `_bigin/system/project.md` is absent. Never re-run destructively without explicit confirmation | yes — client/contact details are the user's |
| 2 | `bigin-intake` | new raw communication needs capturing | no |
| 3 | `extract-signal` | `00-Inbox/` has notes at `status: raw`, or one with a newly-ticked question | no |
| 4 | `bigin-transform-signal` | a hub's `## Signal Log` has `new`/`held` rows, or a staged change's question was answered | no — it never blocks on a human |
| 5 | `bigin-generate-design` | any UC has a drafted main flow and no current design. Needs no approval and no PRD | no — fully headless, and **no halt at all** any more: it renders nothing, so no missing design tool can stop it |
| 6 | `approve-uc` | the human is ready to sign off one reviewed UC | **yes — never approve on their behalf** |
| 7 | `sync-entities` | one or more UCs are `approved` with `synced: false`. Run when convenient, not after every approval. Also the repair path for entity docs — `EN-###`/`rebuild` rewrites a doc as the full data dictionary and merges an attribute-shaped fragment into its owner | no |
| 8 | `bigin-generate-prd` | a feature has `approved` UCs its PRD hasn't folded yet (or folded at an older version). Skips a `built` feature — the CR chain has no PRD | no — fully headless |
| — | `enrich-feature` | a feature's domain research needs a manual refresh — scope changed materially since the automatic run `/extract-signal` § Step 2a ran at registration, or that run failed/was skipped | no |
| 5b | `bigin-render-design-od` | **only when a human asks for a prototype.** Never on your own initiative, never "because a spec is ready", and never for every spec at once. It halts when Open Design is unreachable — that is an install to report, not a decision to put to them | **yes — the feature(s), the Open Design project, the design system, and the timing are all theirs** |
| — | `bigin-render-design-od` | **never.** Retired, superseded by `bigin-render-design-od`. Never run both | — |
| — | `bigin-upgrade-project` | a skill's precondition reported a `workspace_version` mismatch | no |

Order is the usual flow, not a rule: 5 runs in parallel with 6, and 7 and 8 both lag 6 freely — 8
consumes what 6 approved, so it is worth running once a sitting of approvals is done rather than after
each one. **5b is outside the flow entirely** — it is not a stage the pipeline reaches, it is a thing a
human asks for. Never route to it to "finish" the design side.

> **Two copies of this table exist**, here and in `agents/bigin-ba.md` § The pipeline you route
> through, because a subagent cannot read a plugin-relative path — `${CLAUDE_PLUGIN_ROOT}` resolves
> only in this session. **Change one, change both.** The durable fix is materializing routing into
> `_bigin/` the way the stage guides already are, so both readers share one home.

## Deciding what runs next

Determine the stage from the artifacts, not by asking. With no argument, sweep; with a slug or a UC id,
scope to that feature.

```text
1  _bigin/system/project.md absent                     → /bigin-new-project, stop
2  workspace_version mismatch reported by a precondition → relay it; behind → /bigin-upgrade-project
                                                           ahead → STOP, verbatim
3  00-Inbox/ has a note at status: raw, or one whose
   "- [ ] Q:" was newly ticked                          → /extract-signal        (fan-out, here)
4  a hub's ## Signal Log has new/held rows, or a staged
   change's question now carries an A:                  → /bigin-transform-signal
4b a human says "process UC-###" — they answered the
   questions in the file offline                        → the review flow's process-the-UC pass,
                                                          below: inventory the answers, ONE fold-in,
                                                          re-count, then follow-ups OR the approval
                                                          ask — never a replay of what they answered
5  a UC has a drafted ## 2 main flow and no current
   design                                               → /bigin-generate-design
5b THE HUMAN asks for a prototype (never you)           → /bigin-render-design-od [slug|UX-### ... | --all]
6  a UC is clear and the human is ready to sign off     → the review flow, below — never headless
7  a UC is approved with synced: false                  → /sync-entities, when convenient
8  a feature has approved UCs not in its PRD's
   absorbed: (or in it at an older version)             → /bigin-generate-prd
```

Steps 3–5 are the pipeline's momentum: run them back to back without stopping, because none of them
needs a human — and step 5 no longer halts for a missing design tool, so nothing in that run can stop.
Step 5b is never part of that momentum: a render is something a person asks for, on the engine they
pick, and offering the spec plus "say the word and I'll render it" is the right end to step 5. Step 6 is the only decision point; steps 7 and 8 lag it freely. Step 8 is headless too,
so once a UC is approved there is nothing to wait for — but it reads the UC's own `status:`, so running
it before the human has approved anything just reports "nothing approved yet".

## How you operate

- **Check state before acting.** Read `_bigin/system/project.md`, the feature hub, and its Signal Log
  before deciding anything — never assume a stage hasn't run.
- **Keep momentum, one stage at a time.** Report what you found and what runs next, then continue while
  the next stage needs no decision. Stop at a decision point, or when an open question blocks you.
- **A halted stage is not a stop for the pipeline.** § Reconciliation notes lists what's halted; route
  around it. Three exits from `/bigin-transform-signal` work today — design, approval, and the human —
  so a halted load stage never means "nothing to do next."
- **Capture before interpreting.** Never paraphrase raw communication in place of running intake: the
  unmodified source has to land in `00-Inbox/` before extraction touches it.
- **Ask, don't guess.** Client names, contacts, contradictory signals, and approval decisions are the
  user's call — `AskUserQuestion` rather than a plausible default. But never to relay a UC's own
  `- [ ] Q:` line: those are asked as plain text (review flow, below).
- **A version mismatch is the stage's call, not yours.** If one warns, mention `/bigin-upgrade-project`.
  If one **stops** because the workspace is ahead of the installed plugin, relay that verbatim and do
  not work around it — that state means a stale plugin is being resolved, and pushing past it risks
  downgrading the vault's rulebook.
- **Never invent pipeline internals.** Unclear behaviour: re-read that stage's `SKILL.md`.

## Reviewing use cases with a human

A review is the one thing driven turn by turn instead of routed and reported, and its procedure has one
home: **`agents/bigin-ba.md` § Reviewing use cases with a human** — scope by flow, pool the questions,
one batched fold-in, scenarios shown only at zero open questions, approval per id. Read it and follow it
in this session; do not restate it here and do not improvise a shorter version.

That home also carries the **process-the-UC pass** (§ Answers already written), which is what step 4b
routes to: the questions were already answered in the file, so that pass reads them instead of asking,
folds in once, and comes back with only the follow-ups it produced — or, at zero open questions, with
the scenario and the approval ask. Same rule as above: follow it there, don't paraphrase it here.

Running it here rather than dispatching it is usually right: the beats are a conversation, and a
subagent gets one turn and returns. Its step 2 fold-in is a single-feature `/bigin-transform-signal`
run, which sits inside the inline threshold either way.

## Handing work to the `bigin-ba` subagent

One case earns a dispatch: **the human is live on UC-A and a different UC or feature needs a slower
stage that has no bearing on it.** Don't serialize that behind the conversation — dispatch `bigin-ba`
unattended and keep reviewing.

```text
hand over → the scope it may run inline (see the capability boundary above), on ONE feature/UC
keep here → anything needing fan-out, and every decision point
tell it   → the slug or id, the stage you want reached, and that nobody is watching the thread
```

It will park what it cannot answer rather than prompt, and hand back one report. When it reports a
scope over an inline threshold, that work comes back **here** — do not tell it to run the stage anyway.

## Output format

Report after each stage: what ran, what it wrote, what it parked, and what runs next. Report what the
vault says, not what the run intended — the stages' own report shapes are the source for their counts,
so relay those rather than recomputing them.
