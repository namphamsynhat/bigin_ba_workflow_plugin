---
name: extract
description: Reads raw intake notes and turns them into signals - one row per requirement, rule, pain point or decision, each with its quote - then files each under a feature and writes an analysis of what the request changes, contradicts and leaves unclear. Use after intake, when the inbox has raw notes, or when the user asks what a ticket or email affects.
argument-hint: "[INT-### | omit for every raw note]"
---

# Extract signals

Turn each raw note into signal rows. Read `${CLAUDE_PLUGIN_ROOT}/reference/rules.md` first
(sections 4 and 5 matter most here).

## Steps

Run `bigin status` to list the raw notes (or take the id in `$ARGUMENTS`). For each note:

1. **Extract.** Give the note to the `signal-extractor` agent, one agent per note. It returns the
   signal rows. For a note with `extracted_through` set, it reads only the blocks after that one.
2. **File each row under a feature.** Read the pages in `01-requirements/features/`.
   - It fits a feature's described scope → that slug.
   - Nothing fits and it is clearly a new capability → propose a name, ask the person, then
     `bigin new feature "<Name>"`. Never create a feature silently.
   - Unsure → `?` and an open question.
3. **Set each row's status:** `new` (ready to draft) · `question` (needs an answer first) ·
   `conflict` (contradicts a use case, a rule or another signal) · `rejected` (the feature is
   `dropped`, or the row is not a requirement at all).
4. **Write the rows** into the note's `## Signals` table. Keep existing row numbers; add new rows below.
   Then run `bigin check <note>`. It warns when a quote is not in the source word for word: fix the
   quote from the source, or remove the row.
5. **Write `## Analysis`**, short, as a BA briefing the team:
   - **Asks:** what the note wants, in two or three sentences
   - **Changes:** each feature, use case and rule it touches, with ids (`bigin trace <feature>` helps)
   - **Conflicts:** each contradiction, both sides quoted
   - **Unclear:** what is missing before this can be built
6. **Write the questions** for every `question` and `conflict` row under `## Open questions` of the
   note. Group rows about one decision into one question. A gap the source does not raise is not asked
   here: draft sorts it later. First run `bigin questions --feature <slug>`: if it is already asked, do not ask it again.
7. **Update the knowledge pages:** add new terms to `GLOSSARY.md`; add `as-is` and `pain` rows to the
   feature page's "How it works today", each with its source.
8. **Close the note:** set `status: extracted`, `extracted_through` to the last block, add a `## Log` line.

Then report per note: rows by status, conflicts, questions. The next step is `/bigin-ba:draft`.

## Withdrawn notes

For a note with `status: withdrawn`: set its `new` and `question` rows to `withdrawn`. For each
`drafted` row, tell the person which use case or rule holds it (`Lands in`) and run
`/bigin-ba:draft` to take it out.

## Rules

- A conflict with an **approved** use case or rule always stops: it becomes a question, never an edit.
- Answers arrive as signals too. When a row answers an open question elsewhere, fill that question's
  `A:` with the quote and its source (`INT-007 #2`). Leave the rest to `/bigin-ba:draft`.
