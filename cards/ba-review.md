# Card — bigin-ba: reviewing use cases with a human

Three beats, always: **questions → scenario → the human's decision**. Never "here's the UC, approve?".
Named a feature → batch the beats across its flow. Single UC, or answers that depend on each other → one UC at a time.

## Scope by flow
- Set = the hub's `uc:` list + `## Use Cases` (owns and participates); skip consolidated/removed ‹use-case.md § Use Case›.
- Order as the flow runs (read each § 1: trigger, pre/post-conditions; a `level: summary` UC leads), not by id.
- Present the set first: id, goal, status, role, open-question count. Asked about one id, still name its neighbours.

## Rules at either batch size
- Show questions verbatim with their `owner`; plain text, numbered; silence = still open. Never `AskUserQuestion`
  to relay a `- [ ] Q:` or to ask about a question ‹questions.md § Open Questions wording (all artifacts)›.
- A gap you spot is written as a `- [ ] Q:` on the UC, then gated (`cards/ba-triage.md`).
- At a feature review, show the hub's open/answered `## Coverage Gaps` rows in the same numbered list.
- Answers go verbatim onto the question's `A:` line (tick only if it truly closes), then ONE
  `bigin-transform-signal` run folds them in (`bin/bigin ledger release` + apply). Never edit § 1–§ 6,
  never set `status` — `bin/bigin status` re-counts.
- A question the human can't answer parks its UC, not the sitting.
- Show a scenario only at zero open questions, from the file: § 1, § 2 table with S# ids, § 3 branches, § 4.
  Lead with any `## Pending changes` block and any Changelog line "flagged for review" since last approval.
- New information (a correction, a missing step) is `bigin-intake`, never a direct edit ‹intake.md § Feedback handling›.
- Approval is per UC and always the human's: `approve-uc` once per named id.

## Feature-wide batched pass
1. Pool every open question across the flow, gate it, ask once — `owner: client` lines in their own block.
2. Record the whole answer set, then fold in once for the feature. Colliding answers: fold what's consistent,
   re-raise the collision as its own question — never pick a winner.
3. Re-count from the files (a fold-in raises new questions and drift questions); gate the new ones; name the
   reviewable set (zero open questions) and what the rest are parked on.
4. Display the reviewable set as one flow, scenario after scenario.
5. One batched verdict (approve / hold / add information) with named ids, then `approve-uc` per id in flow
   order. Anything `approve-uc` surfaces that the human didn't read drops that UC out for an individual confirm.
After approval, name `sync-entities` / design / PRD as available — never run them.
