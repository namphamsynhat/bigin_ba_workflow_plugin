---
name: approve
description: Walks a person through reviewing a use case, rule, design or story, or a whole feature in one session - shows a short review card, collects their answers by choice, and records their approval. Only a person can run this.
argument-hint: "<feature slug | UC-### | BR-### | UX-### | EP-### | US-###> [more ids]"
disable-model-invocation: true
---

# Review and approve

Approval is the person's decision. Your job is to make the review short and honest: show what needs a
person, not the whole file. Read `${CLAUDE_PLUGIN_ROOT}/reference/rules.md` first.

A feature slug in `$ARGUMENTS` means one session for the whole feature: every draft file in it.

## 1. Show where things stand

Run `bigin card <feature slug>` (for a single id: `bigin card <id>`). Show its output as it is. It
lists each file, what there is to decide, and every question once.

## 2. Collect the answers, all at once

Ask every open question and proposal of the session before you show any file.

- Use the AskUserQuestion tool, up to 4 questions per call. Use the question's `Options:` as the
  choices, the recommended one first. For a proposal the choices are "Yes, as proposed" and "No".
- Add two choices to every open question: **Working answer** (build with our pick for now; the
  client confirms later) and **Skip** (wait for the client).
- Keep each question word for word. Do not shorten it into something else.

Then write down what they chose, in the file where the question lives, with their name and the date:

| They chose | Do |
|------------|----|
| an option, or their own answer | Fill `A:`. Apply it to the text, raise `version`, add a Changelog line, tick the box, add `(applied v<version>)`. |
| yes to a proposal | Fill `A:`, tick the box, add `(applied)`. No text changes. |
| a working answer | Write it into the text, reword the question as a proposal with `(confirm)`, raise `version`. |
| skip, on an open question | Leave it. The files it holds cannot be approved in this session: say which. |
| skip, on a proposal | Leave it. The file can still be approved; its stories wait. |

One answer on the feature page settles it for every file it names.

## 3. Show the card of each file

For each file that no open question holds, run `bigin card <id>` and show it as it is. The card has
the summary, what changed since the last approval, the assumptions, and the steps that name no
source at all. For those steps only, show the step rows from the file.

- Say plainly what the card leaves out: the steps that name a source note. Offer the full text
  ("say `full` to read all of it") and show the file when asked. Never push the person past it.
- Say that approving confirms every assumption on the card. One they reject → change the text, raise
  `version`, and rewrite the line as `Rejected — …`.
- For a design, give the prototype path to open in a browser.
- If a review of this id exists in `04-clients/reviews/`, show its verdict and blockers.
- For a Jira-sourced use case: if `jira_ready_statuses` is set and the ticket is not in one of them,
  say so.

## 4. Their decision

Ask with AskUserQuestion: approve, change, or hold. In a feature session you may ask about several
files in one call, one question per file.

- **Approve** → `bigin approve <id> --by "<their name>"`. It refuses while an open question holds the
  file. It warns about each unconfirmed proposal: pass the warning on.
- **Change** → small wording fix: edit, raise `version`, show the card again. New information or a
  changed requirement: capture it with `/bigin-ba:intake`, so the source is on record.
- **Hold** → leave it as `draft`.

## After

Say what was approved, what is held and by which question, and what is now possible:
`/bigin-ba:design` after use cases, `/bigin-ba:stories` after a design, `/bigin-ba:handoff` for an MVP.
Approving an epic does not approve its stories: each story is approved by id.
