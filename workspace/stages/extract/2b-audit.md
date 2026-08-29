# Source audit rules

Rulebook for the `extract-signal` **source-audit** subagent (`signal-auditor`), and the one home for
the **repair vocabulary** — which `signal-extractor` also follows for its own § Step 6 self-audit.

```text
in:   one note's ## Raw (every ### SRC-n block) and its ## Extracted signals table
out:  a two-direction gap report — GAPS · UNSUPPORTED · CONTRADICTIONS · SUMMARY
      AND those findings applied to the table, by you, before you report
never: re-anchoring · filing · resolving a contradiction · touching status, tags, or Open Questions
```

**You find and you fix.** There is no separate repairer agent: handing a report to a third model that
never saw the source cost a whole dispatch and lost detail at the handoff. Audit blind, then repair
from what you just read.

The table is checked against the raw material twice — once by the extractor that wrote it
(`2-extraction.md` § Step 6), and here, by a reader who has not seen it. This pass is the one that can
still catch what the first one was biased against seeing. Everything downstream reads the table
instead of the source, so a claim neither pass recovers is a requirement that never existed.

`{variable}` resolves in `_bigin/conventions/paths.md`. `{conventions_file}`, if present, overrides
anything here.

## Order is load-bearing

```text
1  write your own list of claims from the source          ← BEFORE opening the table
2  only then read ## Extracted signals, and diff
```

An agent that reads the table first **confirms** it rather than auditing it: every row looks supported
once you know what to look for, and the gaps become invisible because nothing prompts you to look for
them. This ordering is the whole mechanism, not a style preference.

## Step 1 — The independent pass

```text
grep -n "^## \|^### SRC-" <note>        # where ## Raw starts and ends, every ### SRC-n inside it

read ONE BLOCK AT A TIME by line range (offset/limit)
    → a single Read truncates at 2000 lines WITHOUT SAYING SO
    → two blocks in one pass is how a whole attachment gets missed
    a block naming a file path → open that file
    kind == summary → SKIP IT. An AI recap is derived text and can never support a signal.
        note has a summary block and NO transcript block → SAY SO LOUDLY: every row in the
        table is then built on a paraphrase

working through each block SECTION BY SECTION (never one pass over the whole block), list every
discrete attributable claim:
    a requirement · a constraint · a decision · a piece of feedback · an unresolved question ·
    a stated problem or frustration · an answer to something asked earlier · a commitment ·
    EVERY INDIVIDUAL FIELD of a structured table, form spec, or schema

per claim: number it, tag its SRC-n, and quote the supporting text verbatim
```

Be exhaustive. A one-line aside inside a longer topic counts. So does each field of a schema — a field
table is the single highest-loss shape in this pipeline.

## Step 2 — Diff

Now read `## Extracted signals` and compare it against your own list, both directions.

## What counts as UNSUPPORTED

Check **every** `requirement`/`constraint`/`decision`/`feedback` row, and at least half the rest.
"Supported" means you can quote source text stating it.

| Case | What it looks like |
| :--- | :--- |
| **No locatable quote** | the claim reads as a reasonable inference, not something anyone said |
| **Only a summary backs it** | a meeting tool's AI recap is derived text, never support |
| **The quote says less** | a hedge turned into a commitment, one example turned into a general rule, an unstated number, unit, threshold, or timezone |
| **The `Why` is invented** | the cite gives a reason the quote doesn't, including `not stated beyond <paraphrase>` |
| **Inversion** | the quote describes what the CURRENT system does (often as a complaint) and the row states it as a requirement of the NEW one — or the row records current behaviour and drops the ask to change it. Source: *"it doesn't tell me the type, just the school name"* → row: *"the export tracks school type"*. **The most common error on a screen-share transcript: check every requirement row for it.** |
| **Unresolved mechanism stated as settled** | the row asserts *who or what* performs an action ("system does X automatically" / "admin does X") as plain fact, but the surrounding exchange has two or more speakers describing the mechanism in ways that don't reconcile — one says automatic, another says it can't happen unilaterally, a third denies it's "the default" — and the disagreement is never resolved. This is `2-extraction.md` § Special cases' "one mechanism, contradictory framings" landing here anyway: treat a **missing companion `question` row** on such a claim as UNSUPPORTED, exactly like a missing "two wordings" question row on a numeric claim. **Read past the row's own cited timestamp into the surrounding exchange before judging this one** — the contradiction is usually a sentence or two away, not in the cited line. |
| **Bad cite** | the cited timestamp doesn't contain the quoted words |

**Exempt:** rows whose `Why` is `derived from #<n>` **and** whose `Notes` says `inferred — confirm with
client`. These are declared inferences. Instead verify the rows they cite exist, are quotable, and that
the derivation is one step, not a chain.

## Report

```text
A) GAPS (source → rows) — each claim of yours with no matching row:
   GAP <n>: <the claim> | Type: <best type> | quote: "<verbatim>" | Source: <timestamp, or
   sender+date, or attachment section> | Why: <the stated reason, or not stated>

   GIVE THESE IN FULL, even though you are the one who will append them. The gap line is what a
   human reads later to see what the table nearly lost, and it is the only record of the claim in
   your own words — "see repair" there is a lost signal a second time.

B) UNSUPPORTED (rows → source), one line each:
   <#> UNSUPPORTED <which case above> | quote: "<closest real text, or none found>"
   for an overreach or an inversion, also state what the source ACTUALLY supports

C) CONTRADICTIONS — pairs of rows in this table that disagree (one proposes X, another says X won't
   work or isn't allowed):
   CONFLICT #<a> vs #<b>: <one line>

D) SUMMARY: <N> blocks read (<SRC-n list>), <N> claims found, <N> gaps, <N> rows checked,
   <N> unsupported, <N> inversions, <N> conflicts
```

## When the independent pass is owed

This second read of the source is roughly half the cost of the whole extract chain. Since
`2-extraction.md` § Step 6, the extractor audits and repairs its own table on every note, so this
dispatch is no longer the only check — it is the check for the notes where self-auditing is known to
fail. Spend it there and nowhere else.

```text
DISPATCH signal-auditor when ANY holds:
    any source block's kind is `transcript`      # however short — see below
    ## Raw is ~300 lines or more
    more than one source block, and any of them is an attachment or a thread
    2a reported a block it could not read, or `not stated` over 30% of requirement/feedback rows
    2a's self-audit found an inversion or a contradiction   # it found one; assume it missed one
    2a's self-audit repaired more than 5 rows

OTHERWISE the extractor's § Step 6 self-audit stands as the audit. The orchestrator reports it as
"audit: self (<N> lines, <kind>)" — never as a dispatched audit, so a reader can tell which depth ran.
```

**Never skip on a transcript, however short it looks.** The failures this pass exists to catch —
inversion, an unresolved mechanism written as settled, a hedge promoted to a commitment — are all
artifacts of people talking, and none of them are visible without reading the exchange around the
cited line. They are also precisely what the writer of the table is least able to see in their own
work, which is why a fresh reader is the mechanism and not a formality.

**The orchestrator does not audit inline.** Either the extractor's self-audit stands or a fresh agent
is dispatched. Pulling `## Raw` into the orchestrator's context to check it by hand is the one thing
this whole fan-out exists to avoid, and it grows the context that still has to be coherent at the end
of the batch.

---

# Repairing the table — on the audit's findings

Applied by whoever found the finding — `signal-auditor` after its blind pass, or `signal-extractor`
in its own § Step 6 — and always before filing. Nothing has been filed yet, which is why this is a
plain table edit rather than surgery on a themed hub row.

**This table is the one home for the repair vocabulary.** Both agents follow it, so a category means
the same thing and produces the same edit whichever pass caught it.

```text
gap             → append a row after the highest existing #, verbatim from the audit's gap line
                  Notes: "added by source audit" · Feature/Status blank like any new row
overreach       → narrow the Signal (and Why, if flagged) to what the source supports
                  Notes: "corrected: narrowed to source"
inversion       → TWO PARTS, both required:
                  1. Type → decision · rewrite the Signal to name whose system · clear the Why
                     Notes: "corrected: as-is, was filed as requirement"
                  2. if the quote ALSO holds an ask to change it → append a NEW requirement row
                     Notes: "added by source audit"
                  dropping part 2 leaves the client's actual ask unrecorded
bad cite        → replace the timestamp with the block holding the quoted words
                  Notes: "corrected: cite"
no support      → NEVER delete. Notes: "unsupported by source — needs confirmation", and tell 2c to
                  file it Status: question with a plain-language client confirmation question
contradiction   → leave both rows as written; pass the pair to 2c as Status: conflict.
                  Never resolve one here.
```

## Row numbers are permanent, in a repair too

```text
NEVER renumber a row, and never renumber the table to close a gap in the sequence.
    a corrected row keeps its # and gains a `Notes: corrected: …`
    a new row appends after the highest # ever used on this note, including deleted-in-spirit rows
    a row a re-audit supersedes outright: keep it, Notes: "superseded by #<n> (re-audit <date>)"
```

Hub `## Signal Log` rows cite these numbers (`INT-014 #3, #5, #7 — …`) and those cites are the only trail
back from a requirement to what the client said. A renumber silently re-points every one of them at a
different claim — the citation still *resolves*, so nothing errors; it just now attributes a requirement
to something nobody said. `2-qualification.md` Gate 3 check 3 is the downstream detector, and it can only
detect a cite that stopped resolving, never one that resolves to the wrong row.

## Checking your own repairs

You still have the blocks open, so verify in place rather than asking for another pass:

```text
per row you appended or corrected → re-read the quote in its block, confirm the row now says what
                                    the source says and cites the block the words are actually in
```

Do this before you report, and say `verified: <row #s>`. Without it a repair is verified by nothing:
a misquote, or a gap line transcribed loosely, becomes a permanent signal wearing a
`Notes: added by source audit` badge that reads as *more* trustworthy than an ordinary row.

A second dispatched agent for this is not worth its cost — it would re-read the same blocks you have
in front of you, to check work you did thirty seconds ago.

## Report

```text
repaired: <#> <category> — <what changed, one line> (one line each)
appended: <#> — <the signal> (one per gap row added)
verified: <row #s re-checked against their block> (§ Checking your own repairs)
superseded: <#> → #<n> (or "none")
re-audit: scoped to #<list> — clean | <what came back> (or "not needed, ≤ 2 rows touched")
numbering: highest # before <a>, after <b>, none renumbered
```

Count every category in the batch report. A run that appended gap rows would otherwise have silently
lost those requirements, and the count is the only place that is visible.
