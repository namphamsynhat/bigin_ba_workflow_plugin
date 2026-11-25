---
name: draft
description: Turns filed signals into use cases, business rules and data-dictionary entries, or updates existing ones, with every line traced to its source and every gap written as an open question. Use after extract, when signals are waiting, when answers were typed into a file, or when asked to write or update a use case or requirement.
argument-hint: "[feature slug | UC-### | omit for everything waiting]"
---

# Draft requirements

Write what the signals say into use cases and rules. Read `${CLAUDE_PLUGIN_ROOT}/reference/rules.md` first.

## Steps

1. **Find the work.** `bigin status $ARGUMENTS` lists two things: `draft` (signals with status `new`,
   by feature) and `apply` (files with an answer not written into the text yet).
   Work one feature at a time. `bigin trace <feature>` lists its signal rows. Read the feature page
   and its existing use cases and rules first.
2. **Apply the answers.** For each answered question (`A:` filled, no `(applied …)` yet):
   - Write the answer into the text it is about: the file it is in, and every id in its `ref`.
     A "no" removes the proposal. On an intake note, set the signal row to `new` or `rejected`.
   - Then tick the box and add `(applied v<new version>)` to the `A:` line, or `(applied)` when no
     text changed.
   - An answer that brings a new requirement is not applied here: capture it with `/bigin-ba:intake`.
   - A "yes" to a proposal changes no text: mark it `(applied)`. A "no" rewrites the proposed lines.
   - Do not open a new round of questions. What the answer leaves unclear becomes an assumption.
3. **Place each signal:**

   | Signal | Goes to |
   |--------|---------|
   | same actor and same goal as an existing use case | update that use case: a new step, flow or rule |
   | a new goal | `bigin new uc "<Verb phrase>" --feature <slug>` |
   | a condition the system must enforce | `bigin new br "<Title>" --feature <slug>`, then list it in the use case's `## Rules` and `rules:` |
   | a field or a business object | the entity page (`bigin new entity "<Name>"` if new) |
   | type `design` | leave it `new`; `/bigin-ba:design` uses it |

4. **Write** in the style of rules section 6. Write the `## Summary` last, from the finished details. Fill the `Source` column of every step. Add each note id
   to `sources:`. When a fact is missing, sort the gap as rules section 5 says: park it, assume it,
   propose it, or ask. Most gaps are assumptions. Give each open question its `Options:` line. Never leave a step empty because an answer is
   missing when a proposal can fill it. A question goes in one file only: on the use case when it is
   about that use case, on the feature page with `(ref: UC-003, UC-007)` when it is about several.
5. **Changing an existing file:** raise `version`, add a Changelog line with the source, and set an
   `approved` file back to `draft`.
6. **Mark the signals:** set each row to `drafted` and fill `Lands in` (`UC-003 S2`).
7. **Check the set.** For the feature's use cases together, look for: a goal a signal names but no use
   case covers, a step with no failure path, a rule no step applies. Sort each as rules section 5
   says; one that must be asked goes on the feature page. Then run `bigin check` and clear every `same question` warning: keep the
   question in one file and close the other as the warning says.
8. **Get a second reading.** Give each new or changed use case to the `spec-reviewer` agent. Fix what it
   finds, or sort the finding as rules section 5 says.
9. **Report** briefly. Do not paste file content: the person reviews with the card.
   Report: files created and changed, open questions by owner, proposals to confirm, the number
   of assumptions, what was parked, and what is ready for a person to review. The next step is the person's: `/bigin-ba:approve <feature>` reviews the whole feature in one session.

## Rules

- One use case is one actor reaching one goal. If a use case grows a second actor's goal or a second
  trigger, ask the person where to split it. Do not split it yourself.
- A use case says what happens, not how it looks. No screens, buttons or colours.
- A signal that changes an approved use case in a way the client did not clearly decide becomes a
  question first, not an edit.
- If `codebase` is set in `bigin.md`, check how the system behaves today there before asking an
  `owner: dev` question. Cite `file:line`. Never write to the code.
