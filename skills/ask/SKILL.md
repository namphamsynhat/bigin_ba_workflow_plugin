---
name: ask
description: Answers questions from the team's second brain - what the client said, what was decided and why, how a feature works, what a request or ticket changes, what is still open - with the source of every statement. Use when someone asks about the project's requirements, decisions, history, scope, or the impact of a change.
argument-hint: "<question>"
---

# Ask the second brain

Answer from the vault only, and show where each statement comes from.

## Steps

1. **Find it.** Start from `INDEX.md`. Search the vault for the terms in the question and for their
   `Also called` names in `01-requirements/GLOSSARY.md`.
   - "What does X touch / what breaks if X changes" → `bigin trace <id or feature>`
   - "What is open / what are we waiting for" → `bigin questions` and `bigin status`
   - "Why" → the Changelog and the answered questions of the file, then the quote in the intake note
2. **Read the sources**, not only the summaries. For what someone said, read the `## Raw` block.
3. **Answer** in plain words, shortest useful form first. After each statement give its source:
   `(UC-003 S2)`, `(INT-004 #3)`, or a short quote with `(INT-004 SRC-1)`.
4. **Say how firm it is:** approved, draft, an open question, or stale.

## Rules

- If the vault does not say, answer "The vault does not say" and name who could answer. Do not fill
  the gap from general knowledge.
- When two sources disagree, show both with their dates. Do not pick one.
- Read-only. To record something new, use `/bigin-ba:intake`.
