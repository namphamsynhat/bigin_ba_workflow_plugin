---
name: stories
description: Slices approved use cases and their design into an epic and user stories with acceptance criteria, each story complete enough for a developer or a coding agent to build from. Use after use cases (and their design) are approved, when stories are stale, or when asked for epics, user stories, acceptance criteria or a dev hand-off.
argument-hint: "[feature slug | EP-### | omit for every feature waiting]"
---

# Write stories

Cut each approved use case into stories a developer can build in about a day.
Read `${CLAUDE_PLUGIN_ROOT}/reference/rules.md` first.

## Steps

1. **Scope.** `bigin status $ARGUMENTS` lists approved use cases with no story, and stale stories.
   Use only `approved` use cases. Read their rules, entities and the feature's design.
   A use case with a proposal the client has not confirmed gets no story yet: `bigin status` lists it
   under `confirm`, and `bigin check` refuses a story built from it. Name it in your report with
   the proposals it waits for (`bigin questions --kind confirm`).
   No approved design → say so, and ask whether to go on without screens.
2. **Epic.** One epic per feature: `bigin new ep "<Outcome>" --feature <slug>`, or the existing one.
3. **Slice** each use case:
   - The main flow first (P1). Then each alternative flow or group of rules (P2, P3).
   - An error that only shows a message on the same screen is an acceptance criterion, not a story.
   - One story is about one pull request: at most 8 acceptance criteria and 3 screens.
4. **Write each story:** `bigin new us "<What the user gets>" --epic EP-###`. Fill every section:
   - the story sentence and `Slice of`
   - the `## Summary`, written last: what a developer needs before deciding to read the rest
   - the flow, in business words: what the person sees, does and is told
   - the screens, by their design names, with the prototype path
   - the **full text** of each rule, so the story stands alone
   - one Gherkin scenario per rule and per error path, tagged `[S2] [BR-004]`
   - `Out of scope`, and `## Assumptions` for anything no source asked for
   - `built_from: [UC-003@2, UX-001@1]`, and `jira:` with the keys of the source notes
5. **Fill the epic:** the `Stories` table and the `Coverage` table. Every step and flow of every use
   case has a story. No blank rows.
6. **Get a second reading** from the `spec-reviewer` agent on each story.
7. **Report** the epic, its stories and the open questions. A person reviews with
   `/bigin-ba:approve US-###`.

## Rules

- **Never edit an approved story.** When its use case changed, write a new story that holds only the
  difference, and set its `delta_of:` to the approved story's id.
- Requirements and design are read-only here. Sort a gap as rules section 5 says, on the story. Do not
  ask again what the use case or the design already settled or assumed.
- Never post to Jira. To hand over, the person copies the story text.
