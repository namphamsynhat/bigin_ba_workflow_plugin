# Dispatch — the fallback loop (no Workflow tool)

`workflows/transform.js` is the normal path. When the Workflow tool is unavailable, the orchestrator runs
the same steps with `Agent` / `SendMessage`, per feature. `BIN="${CLAUDE_PLUGIN_ROOT}/bin/bigin"`; task
files live under `_runs/$RUN/tasks/`. Subagents cannot resolve `${CLAUDE_PLUGIN_ROOT}` — the orchestrator
runs every `$BIN` command and passes **absolute** card paths.

## Parallelism

Features in parallel, ≤ 4 at a time; within one feature, strictly sequential. Two features may touch the
same cross-feature UC: the engine refuses a write whose file changed on disk since it was read
("changed on disk — re-run"); on that message re-run the same `apply` once — it is idempotent (applied
change-set ids are recorded in the Changelog). Minting is serialized by the engine's id lock.

## Per feature

```text
1  $BIN worklist route <slug> --rows <qualified rows from Stage 2> --out <slug>.route.in.json
2  Agent(bigin-ba-workflow-plugin:uc-router), foreground; keep its id
     prompt: "Card: <abs>/cards/router.md. PHASE A. Input: <vault>/_runs/$RUN/tasks/<slug>.route.in.json.
              Write schema `route` to <…>/<slug>.route.out.json. <override text from
              .claude/bigin-ba-workflow-plugin.local.md, if any>"
3  $BIN ingest <slug>.route.out.json --kind route --run $RUN
     invalid → SendMessage the errors to the same agent once; still invalid → park the feature
4  $BIN mint route --spec <slug>.route.out.json        # writes <slug>.route.out.minted.json
5  SendMessage(same agent): "PHASE B. Minted ids: <contents of the minted file>. Write schema
     `changesets` to <…>/<slug>.changesets.out.json." — resume, never a fresh dispatch: the agent
     already holds the worklist
6  $BIN ingest <slug>.changesets.out.json --kind changesets --run $RUN   (same repair rule)
7  $BIN apply <slug>.changesets.out.json --run $RUN
8  project.md grounding codebase|both, and the hub has conflict/held rows →
     $BIN worklist adjudicate <slug> --out <slug>.adjudicate.in.json
     one Agent(bigin-ba-workflow-plugin:code-adjudicator) per row, card <abs>/cards/adjudicator.md,
     output <slug>.adj-<row>.out.json; P0/security rows get a second, independent judge and apply only
     when both agree; then $BIN ingest … --kind adjudication && $BIN apply <file> --run $RUN
9  $BIN hub refresh <slug>
```

Replies are one line (`OK <path> …` / `BLOCKED <reason>`). Do not ask for, or read, a prose report.

## Coverage, not claims

After each feature: `$BIN run summary $RUN` plus the apply result. Every qualified row must be accounted
for — `applied`, `staged` (gated or drift), `conflict`, `question`, or listed under `unrouted` in the
change-set file with a reason. A qualified row still `new` after apply is **blocking**: re-dispatch it
scoped (`--rows <n>`) or park it `held` with `$BIN hub flip <slug> <n>=held@<why>`.

## Model

Never override an agent's pinned model from the prompt.
