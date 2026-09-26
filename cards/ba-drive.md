# Card — bigin-ba: drive to done · process-the-UC · unattended

## Drive to done (up to approve-uc, never past it)
Before reporting, run every stage your change made runnable whose Decision point is *no* (intake, extract
where allowed, transform). A parked UC never stalls the feature's transform pass; a drifted mirror is a fix
(`bin/bigin mirror br`, `links sync`, `hub refresh`), not a finding. Only four things are handed back:
a stage over threshold (name the `/bigin-run` command) · an out-of-scope load stage (name it, don't run it) ·
a human-reserved write (`approve-uc`, `PP-###` addressed, a `restructure-uc` boundary) · a genuine blocker.

## Process-the-UC pass (answers already typed in the file)
Never replay the asking beat ‹questions.md § Answering a question (the human side of the loop)›.
1. Scope by flow; inventory each `## 5` Still open (plus BR/INT questions its hub rows point at):
   blank `A:` → gate it yourself (`cards/ba-triage.md`); answered → fold in; answered but not settling
   (defers, restates, answers another question) → a follow-up carrying why; two answers colliding →
   re-raise; ticked over a non-answer → name it and ask, never untick. Only two edits allowed: moving an
   answer given elsewhere onto its `A:` line verbatim, and your own labelled answers.
2. Fold in once for the feature: `bigin-transform-signal` (`bin/bigin ledger release` applies gated change
   sets whose question is answered). Over threshold → hand back.
3. Re-count from the files. Relay a drift question with both wordings — only the BA can pick.
4. Come back once: zero open questions → scenario + approval ask, nothing else; otherwise only gated survivors,
   verbatim, grouped by UC. A clear UC is never held behind a parked sibling.
5. Report what their answers bought, what you answered and from where, what remains, what's approvable.

## Unattended (a live review runs elsewhere)
- Never `AskUserQuestion`; park questions as written `- [ ] Q:` lines. A parked item never stops the batch.
- Never run a decision-point stage. A genuine blocker stops you and is reported.
- Gate everything before parking — an avoidable question costs the rest of the day. One report at the end.
- Process-the-UC unattended runs steps 1–3 and stops at the report ‹runtime.md § Resumable unattended apply (checkpoint + idempotent writes)›.

## Edge cases
No `_bigin/system/project.md` or `_bigin/stages/` → `bigin-new-project`, stop. Intake with no clear feature →
let `extract-signal` raise the mapping question. Empty hub `uc:` → transform first. An already-approved UC in
the set is context only. A review answer that changes a different UC → name it, let the fold-in edit it.
