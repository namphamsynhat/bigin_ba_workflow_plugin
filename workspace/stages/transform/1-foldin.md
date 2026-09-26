# Stage 1 — Release, re-entry, orphan answers

```text
runs: orchestrator, FIRST, every invocation
in:   the ledger (01-Requirements/_ledger/*.jsonl) · conflict/question rows whose question is answered
      · answered questions no row points at
out:  answered gated change sets applied · re-entered rows back to `new` · mirrors reconciled
never: status — Stage 5 re-counts it
```

Stage 1 before Stage 2 is what makes a rerun useful: it harvests answers a human wrote since the last
run before anything new is drafted. `BIN="${CLAUDE_PLUGIN_ROOT}/bin/bigin"`.

## Legacy vaults first

```text
any UC/BR ## Discussion still holding `- **INT-###** (staged …)` entries (v1.8.x)?
    → $BIN migrate discussion-to-ledger       # snapshots the vault, converts each entry to change sets:
                                              # mechanical ones (§ 2/§ 3/§ 4 mirror) apply now, prose ones
                                              # tied to an open question on the same hub row go to the
                                              # ledger gated on it, the rest apply now
    → entries it reports as `unparsed` stay in ## Discussion: route them through Stage 3 as ordinary
      rows (their hub row is still `staged`), or leave them for a human — never hand-apply them
```

## Release the ledger

```text
$BIN ledger release
    per open change set: its gate question ticked with a filled A: (or already in the decision log)
      → applied through the same engine path as any change set; the settled question moves to the
        UC's Decision log; the ledger entry becomes `released`; the hub row flips to `applied`
    answer reads as a refusal ("no", "reject", "out of scope", …) → `needs-judgement`, NOT applied
    still unanswered → waits
```

**Needs-judgement.** `$BIN worklist release all --out _runs/$RUN/tasks/release.in.json` lists each one with
its question, answer, and change set. The orchestrator (or one `uc-router` dispatch for many) decides per
item — `apply` (the answer does support it), `supersede` (the answer contradicts it), or `revise` (a
corrected change set) — writes `{"kind":"verdicts","verdicts":[…]}` and runs
`$BIN ledger release --verdicts <file>`. A superseded set leaves its hub row `staged`; flip it with
`$BIN hub flip <slug> <n>=superseded@<the decision>` or re-enter it (§ Re-entry) when the answer is new
content.

## The human may have edited the section first

A reviewer is invited to edit a UC directly while reviewing it, so text a change set expects to replace
can be gone. The engine enforces the rule on every apply, including a release:

```text
anchor sha still matches            → apply
current text already IS the proposal → counts as applied (a hand-applied change); nothing written twice
anchor text materially changed       → DRIFT: not applied, never overwritten; ONE question on the
                                       artifact naming both wordings; the hub row stays `staged`
```

A drift question is an ordinary open question: when answered, Stage 3 drafts from the answer (the row is
still `staged` with the drift noted; re-enter it per § Re-entry).

## Re-entry — an answered `conflict` or `question` row

A `conflict` row stages nothing by design; a `question` row never had a lane. Neither is in the ledger
nor `new`/`held`, so without this step an answered requirement is stranded forever.

```text
scan in-scope hubs for Status conflict | question; find the question each raised (Notes/Destination
point at it: a UC § 5, a BR's Open Questions, the hub's Gates, or the source INT note)
A: blank  → leave it
A: filled → $BIN hub flip <slug> <n>=new@"re-entered <date>: <question> answered on <artifact> — <A: ≤10 words>"
            losing side of a conflict → $BIN hub flip <slug> <m>=superseded@"superseded by the decision on #<n>"
            a third option neither row proposed → both old rows superseded; the re-entered row carries it
            settle the question (§ Orphan answers, first case)
```

Stage 2 collects the re-entered row this same run and Stage 3 drafts it **from the decision**, never by
re-staging whichever side lost. An answer that resolves nothing leaves the row `conflict`, unticked —
report it. Report every re-entry: it is the one case where a row's status moves backwards.

## Orphan answers — an answered question no row points at

A `## 4` inconsistency question, a drift question, or a gap question a reviewer wrote onto a UC has no
row behind it. Find filled `A:` lines with `Grep {uc_dir} {br_dir} "^\s*A: \S"` not already accounted
for above, and read what each decides:

```text
confirms what the artifact says / needs no new content
    → an `answer_question` change set (anchor = the question text, text = the decision) through
      $BIN apply: the line moves to the UC's Decision log (a BR: ticked with its A:), version bump,
      Changelog line
adds content the artifact lacks (a step, branch, rule, trigger)
    → NOT drafted here — there is no signal to trace it to. Leave it open; report it as needing
      /bigin-intake (capture it as a note citing the UC and question)
settles nothing (restates, defers, asks anew)
    → leave it unchecked; report it as answered-but-unresolved, saying why
```

A ticked box over the second or third kind is a mis-tick: report it, never untick silently.

## Reconcile mirrors — every run

```text
$BIN links sync            # brs:/uc:/features:/sources: and the FEATURES.md UC column
$BIN hub sweep             # staged → applied where nothing pending (Discussion or ledger) cites the row
$BIN hub refresh <slugs>   # every in-scope hub AND every hub a touched cross-feature UC names
```

All three are idempotent. One mirror stays manual: when an artifact's question is resolved and the same
question sits on the source `INT` note's `## Open Questions`, tick the note's copy with the answer (and
"resolved by INT-###" when the answer arrived on a later note) — one question, two places.

## Hand-off

Report: `ledger: N released · N superseded · N need judgement · N waiting`, `re-entered: <slug> #<n> — <the
decision>` per row, `orphan answer: UC-### — <question> → settled | needs /bigin-intake | unresolved`,
`drift: <artifact> <ref>` per drift question.

## Failure modes

- **Hand-applying a pending change** instead of answering its question and releasing — it lands without
  a Changelog trace and is applied a second time by the next release.
- **Skipping § Re-entry because nothing is in the ledger** — a hub can carry a dozen answered
  `conflict`/`question` rows and zero ledger entries.
- **Applying a refusal answer** — needs-judgement exists because "No" is an answer that kills the change.
- **Ticking a box to make the count zero** — an answer that doesn't resolve the question stays unchecked.
- **Setting `status` here** — Stage 5 re-counts.
