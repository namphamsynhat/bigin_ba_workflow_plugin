---
id: {{id}}
type: story
title: {{title}}
status: draft
version: 1
approved_version:
feature: {{feature}}
epic: {{epic}}
priority: P1
built_from: []
jira: []
delta_of:
updated: {{date}}
---

# {{id}} {{title}}

**As a** <role>, **I want** <capability>, **so that** <business value>.

- **Slice of:** <!-- e.g. UC-003 S1–S4, the main path -->

## Summary

<!-- What a developer reads first. At most 120 words, as short bullets: what the user can do after
this story, what is new on screen, what must not happen. No ids. The details below are the full text. -->

## Flow

| Step | The user | The system |
|------|----------|------------|

## Screens

<!-- Screen names from the design, with a link to the prototype file. -->

## Rules

<!-- The full text of every rule this story must obey, so the developer needs no other file. -->

## Acceptance criteria

<!-- One scenario per rule and per error path. Tag each with its step and rule. -->

```gherkin
Scenario: AC1 — <name> [S1] [BR-###]
  Given <a business situation>
  When <the user does something>
  Then <a result the user or the business can see>
```

## Out of scope

## Assumptions

<!-- Lines no client request asked for, with the reason. Review these first.
- A1: <statement> — why: <reason> (AC2) (owner: team) -->

## Open questions

## For the developer

- Put `{{id}}@<version>` in the pull request title.
- Name each test after its criterion, e.g. `{{id}} AC1 — <name>`.
- If this story does not answer something, stop and ask. Do not guess.

## Changelog

- v1 ({{date}}) — created
