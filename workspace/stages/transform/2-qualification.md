# Qualification — Stage 2's four gates

A signal on a Feature Hub's `## Signal Log` is a *claim that a client said something*. Before it
becomes requirement content, four things must hold: nobody is still waiting on an answer about it,
the source it came from is fully materialized, the row faithfully reflects that source, and it
isn't already covered somewhere. Each gate below has exactly one outcome per case — write that
outcome, never improvise a new one.

Run the gates in order and stop at the first one a row fails. A failed row is parked, not deleted;
the next run re-checks it, which is why `held` rows are always re-collected.

## What this stage reads

Per signal row, open only the intake note's **frontmatter**, **`## Extracted signals`**, and
**`## Open Questions`**. Never open `## Raw`, a transcript, or an attachment here — that material
belongs to extraction, and re-reading it at transform time both explodes context and duplicates a
rule that `_bigin/stages/extract/2-extraction.md` already owns.

## Gate 1 — Blocked on an answer

The intake note is where a missing rationale or an ambiguous scope is being chased. A signal whose
question is still open cannot be drafted from, because the answer may change what it says.

Open the note's `## Open Questions`. The row fails this gate if:

- An unchecked `- [ ] Q:` line references this signal's row number or subject matter, **or**
- The note's `## Extracted signals` row for this signal is `Type: requirement`/`feedback` with
  `Why: not stated`, and no checked answer supplies the reason.

| Outcome | Write |
|---|---|
| Blocked | `Status: held`, `Notes: awaiting <INT-###> — <the question in five words>` |

**Never re-raise the question.** It already exists on the note, owned by a human, and
`conventions.md` § One question, two places is explicit that a second copy of the same ask is a
bug. **Never re-derive the missing `Why` from the raw source** either — a `Why` reconstructed at
transform time is a guess wearing a citation, which is the exact failure `_bigin/stages/extract/2-extraction.md`
§ The `Why` field is written to prevent.

A `requirement`/`feedback` signal that is genuinely fine without a stated reason does not exist:
if extraction filed one with `Why: not stated` and *no* companion question, that is an extraction
self-check failure. Park the row `held`, `Notes: <INT-###> missing why, no question raised —
re-run /extract-signal`, and name it in the report.

## Gate 2 — Source materialized

A signal extracted from a half-present source is a signal extracted from part of the story.

The row fails this gate if any of these hold for its `INT-###`:

- The note's frontmatter `attachments:` lists a vault-relative path that does not exist on disk.
- The note's `## Raw` cites a URL or a document whose content was never pulled into the note or
  into `00-Inbox/_attachments/<INT-###>/`.
- `source: email` and the thread is unresolved — the note records a question sent to the client,
  or its newest message is an outbound ask with no reply captured yet.

| Outcome | Write |
|---|---|
| Source incomplete | `Status: held`, `Notes: source incomplete — <what is missing>; re-run /bigin-intake then /extract-signal` |

**Do not pull the missing source here.** Pulling it is cheap; acting on it is not. New content
means new signals, and only `extract-signal` can extract them — a transform-side pull produces a
richer note that nothing re-reads, so the added material is silently lost while the note now
*looks* complete. Send it back to the stage that owns it.

When an email reply *has* landed, extraction handles it as a fold-in run: the reply becomes a new
`answer` row and the note's question closes. Transform sees the result as an ordinary qualified
signal on the next run — there is no reply-handling logic in this skill.

## Gate 3 — Fidelity

The hub's Signal Log row is a **themed consolidation** of one or more of the note's
`## Extracted signals` rows — its `Source` cite names exactly which (`INT-014 #3, #5, #7 — Jane Doe
2026-08-05`), and its `Signal` cell carries one clause per cited row (`conventions.md` § Feature
Hub). This gate checks that the consolidation is faithful and the trail is followable. It does not
re-verify the note against the raw source — that is `extract-signal`'s source audit, which runs next
to the raw material and checks it quote-anchored in both directions (`/extract-signal` § Step 2b).

Check two things, both cheap:

1. **The consolidation matches.** Every note row `#` the hub row cites still exists, and its claim
   is still represented in the hub row's `Signal` clauses and covered by the hub row's `Type`.
   Extraction may have corrected a row in place after filing it (`Notes: corrected: …`), which
   leaves the hub stale. **Row counts between the two tables are not a check** — one hub row
   covering several note rows is the design, not drift.
2. **The `Source` cite is specific.** It resolves to a real place — a transcript timestamp, a
   `<sender> <date>`, or an attachment filename — and names the note row numbers it consolidates,
   not "somewhere in the note."

| Case | Outcome |
|---|---|
| A cited clause is stale | Repair that clause from the note (**the note is the source of truth**), keep the row `#` and its other clauses untouched, `Notes: refreshed from <INT-###>`. Continue to Gate 4 — this is a repair, not a block. **Never un-merge a themed row into one row per signal** — that renumbers history and breaks every `#` cited elsewhere. |
| `Source` cite is missing or unspecific, and the signal would create **new** FR/BR content | `Status: held`, `Notes: unverifiable source cite — re-run /extract-signal verification`. Report it. |
| `Source` cite is weak but the signal only adds context to an existing FR | Continue, and note the weak cite in the FR's `## Discussion` entry. |

Hold the strict version only for signals about to mint new requirement content. A blanket
re-verification of every row on every run would re-litigate work already verified upstream and
would make an unattended run scale with the whole backlog rather than with what changed.

## Gate 4 — Dedup

Three distinct cases, three distinct outcomes. Only one of them touches an existing row, and none
of them delete anything (hard rule 1).

### 4a — Duplicate of an earlier signal

Same claim as an earlier Signal Log row on this hub, adding no new information — a second meeting
where the client repeated an ask.

```
Status: applied
Notes: duplicate of #<n> — no change
```

`applied` is correct and `superseded` is not: the claim *is* reflected in the artifact, via `#n`.
Keeping the row (rather than dropping it) preserves the traceability that the client said this
twice, which is real evidence of priority.

### 4b — Already covered by the current requirement

No earlier signal matches, but the feature's existing FR or BR text already states this. Common
after a fold-in that generalized several signals at once.

```
Status: applied
Notes: already covered by FR-### v<version> — no change
```

Read the artifact before writing this. "Covered" means the existing text would already satisfy a
tester checking this signal — not that the topic is mentioned nearby.

### 4c — Supersession

The signal contradicts or refines an earlier row: the client changed their mind, or narrowed an
ask. This is **not** a duplicate — it is an update, and it routes normally through Stage 3's FR/BR
lane. Alongside that:

- Flip the **earlier** row to `Status: superseded`, `Notes: superseded by #<n>`.
- The new row keeps its own `#` and proceeds to routing.

Never rewrite the earlier row's `Signal` text to match the new position. History is append-only
(`conventions.md` § Feature Hub) — the old row is the record of what was true before.

If which of two rows wins is genuinely a human call rather than a chronological one, that is a
`conflict`, not a supersession: leave both rows, flip the newer to `Status: conflict` citing the
earlier `#`, and raise a question. Recency decides a supersession; it does not decide a conflict
between two people's stated requirements.

## Status values this stage may write

`held`, `applied`, `superseded`, `conflict` — plus leaving a row at `new` when it passes all four
gates and moves on to Stage 3 (which sets `staged`).

`removed` and `duplicated` are **not** Signal Log values. `removed` belongs to the FR/BR
vocabulary and is human-gated only (hard rule 4); `duplicated` does not exist anywhere in the
vault. A row whose feature is `status: out-of-scope` in `FEATURES.md` is `rejected`,
`Notes: out-of-scope — skipped`, which extraction normally already wrote.

## Report line

Stage 2 contributes one line per outcome class to the run report, so a human can see what was
blocked without opening a hub:

```text
qualify: <N> qualified · <N> held (<N> awaiting answer, <N> source incomplete, <N> unverifiable)
         · <N> applied as duplicate/already-covered · <N> superseded · <N> conflict
```

Name the specific `<slug> #<row>` for every `held` and `conflict` row — those are the ones a human
has to act on.
