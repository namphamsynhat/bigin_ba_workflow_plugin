# Stage 2 — Qualification: the four gates

A signal on a hub's `## Signal Log` is a *claim that a client said something*. Four things must hold
before it becomes requirement content.

```text
reads:  per row, the intake note's frontmatter + ## Extracted signals + ## Open Questions
never:  ## Raw, a transcript, or an attachment
        → that material belongs to extraction; re-reading it here explodes context and duplicates
          a rule _bigin/stages/extract/2-extraction.md already owns

for row in worklist:                       # every Status: new or held
    gate 1 blocked-on-answer  → fail: park, stop
    gate 2 source-materialized → fail: park, stop
    gate 3 fidelity            → fail: park, stop  (or repair and continue)
    gate 4 dedup               → fail: mark, stop
    all pass → stays `new`, moves to Stage 3
```

Each gate has exactly one outcome per case — write that outcome, never improvise a new one. A failed
row is **parked, not deleted**; the next run re-checks it, which is why `held` rows are always
re-collected.

## Gate 1 — Blocked on an answer

The intake note is where a missing rationale or an ambiguous scope is being chased. A signal whose
question is still open can't be drafted from — the answer may change what it says.

```text
FAIL if the note's ## Open Questions has an unchecked "- [ ] Q:" referencing this row's number
     or subject matter
FAIL if the note's ## Extracted signals row is Type: requirement/feedback with Why: not stated
     and no checked answer supplies the reason

→ Status: held
  Notes:  awaiting <INT-###> — <the question in five words>
```

- **Never re-raise the question.** It exists on the note, owned by a human. A second copy of the same
  ask is a bug (`conventions.md` § One question, two places).
- **Never re-derive the missing `Why`** from the raw source — a `Why` reconstructed at transform time
  is a guess wearing a citation.

A `requirement`/`feedback` signal that is genuinely fine without a stated reason **does not exist**.
Extraction filing one with `Why: not stated` and *no* companion question is an extraction self-check
failure → park `held`, `Notes: <INT-###> missing why, no question raised — re-run /extract-signal`,
and name it in the report.

## Gate 2 — Source materialized

A signal extracted from a half-present source is a signal extracted from part of the story.

```text
FAIL if frontmatter `attachments:` lists a vault-relative path not on disk
FAIL if ## Raw cites a URL or document whose content was never pulled into the note or
     00-Inbox/_attachments/<INT-###>/
FAIL if source: email and the thread is unresolved — the newest message is an outbound ask
     with no reply captured

→ Status: held
  Notes:  source incomplete — <what is missing>; re-run /bigin-intake then /extract-signal
```

**Do not pull the missing source here.** Pulling it is cheap; acting on it is not. New content means
new signals, and only `/extract-signal` can extract them — a transform-side pull produces a richer note
that nothing re-reads, so the added material is silently lost while the note now *looks* complete.

When a reply lands, extraction handles it as a fold-in run: the reply becomes an `answer` row and the
question closes. Transform sees an ordinary qualified signal next run — there is no reply-handling
logic in this skill.

## Gate 3 — Fidelity

The hub row is a **themed consolidation** of one or more note rows; its `Source` cite names which
(`INT-014 #3, #5, #7 — Jane Doe 2026-08-05`) and its `Signal` cell carries one clause per cited row.
This gate checks the consolidation is faithful and the trail followable. It does **not** re-verify the
note against the raw source — that is `/extract-signal`'s source audit, quote-anchored in both
directions.

```text
1  consolidation matches — every cited note row # still exists, its claim still represented in a
   Signal clause, and covered by the hub row's Type
   → extraction may have corrected a row in place after filing (Notes: corrected: …), leaving the
     hub stale
   → ROW COUNTS ARE NOT A CHECK: one hub row covering several note rows is the design
2  Source cite is specific — resolves to a real place (timestamp · <sender> <date> · attachment
   filename) and names the note row numbers it consolidates, not "somewhere in the note"
```

| Case | Outcome |
|---|---|
| a cited clause is stale | **Repair that clause from the note** (the note is the source of truth), keep the row `#` and its other clauses, `Notes: refreshed from <INT-###>`, **continue to Gate 4** — a repair, not a block. **Never un-merge a themed row** — that renumbers history and breaks every `#` cited elsewhere. |
| cite missing/unspecific, and the signal would create **new** UC/BR content | `Status: held`, `Notes: unverifiable source cite — re-run /extract-signal verification`. Report it. |
| cite weak, but the signal only adds context to an existing UC | continue; note the weak cite in the UC's `## Discussion` entry |

Hold the strict version **only** for signals about to mint new requirement content. Blanket
re-verification would re-litigate verified work and make an unattended run scale with the whole
backlog rather than with what changed.

## Gate 4 — Dedup

Three cases, three outcomes. Only one touches an existing row; none delete anything.

```text
4a  DUPLICATE — same claim as an earlier row on this hub, adding nothing new
    (a second meeting where the client repeated an ask)
    → Status: applied
      Notes:  duplicate of #<n> — no change
    `applied`, not `superseded`: the claim IS reflected in the artifact, via #n. Keeping the row
    preserves that the client said this twice — real evidence of priority.

4b  ALREADY COVERED — no earlier signal matches, but an existing UC flow or BR already states this
    (common after a fold-in that generalized several signals at once)
    → Status: applied
      Notes:  already covered by UC-### S<n> v<version> — no change
    CITE THE STEP or BR, not just the document. "Somewhere in UC-012" is what a future run cannot
    verify, and 5-status.md check 2 exists to catch it.
    READ THE ARTIFACT FIRST: "covered" means the existing text would already satisfy a tester
    checking this signal — not that the topic is mentioned nearby.

4c  SUPERSESSION — the signal contradicts or refines an earlier row (the client changed their mind,
    or narrowed an ask). NOT a duplicate — an update, routing normally through Stage 3.
    → flip the EARLIER row: Status: superseded, Notes: superseded by #<n>
    → the new row keeps its own # and proceeds to routing
    NEVER rewrite the earlier row's Signal text to match the new position — history is append-only.

    if which row wins is a HUMAN call rather than a chronological one → that's a CONFLICT:
      leave both rows, flip the newer to Status: conflict citing the earlier #, raise a question.
      Recency decides a supersession; it never decides a disagreement between two people.
```

## Status values this stage may write

`held` · `applied` · `superseded` · `conflict` — plus leaving a row at `new` when it passes all four
gates (Stage 3 sets `staged`).

`removed` and `duplicated` are **not** Signal Log values: `removed` belongs to the UC/BR vocabulary and
is human-gated only; `duplicated` doesn't exist anywhere in the vault. A row whose feature is
`status: out-of-scope` is `rejected`, `Notes: out-of-scope — skipped` — which extraction normally
already wrote.

## Report line

```text
qualify: <N> qualified · <N> held (<N> awaiting answer, <N> source incomplete, <N> unverifiable)
         · <N> applied as duplicate/already-covered · <N> superseded · <N> conflict
```

Name the specific `<slug> #<row>` for every `held` and `conflict` — those are what a human must act on.
