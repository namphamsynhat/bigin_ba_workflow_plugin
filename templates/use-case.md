---
id: {{id}}
type: use-case
title: {{title}}
status: draft
version: 1
approved_version:
feature: {{feature}}
sources: []
rules: []
updated: {{date}}
---

# {{id}} {{title}}

- **Actor:** <!-- the role that wants the goal — a role, never a person's name -->
- **Goal:**
- **Trigger:**
- **Before:** <!-- what must already be true -->
- **After:** <!-- what is true once the goal is reached -->

## Summary

<!-- What people read first. 3 to 5 plain sentences, at most 120 words: who does what, what the system
does, and the main thing that can go wrong. No ids. It must say nothing the details below do not say. -->

## Main flow

<!-- One action by one actor per step. Source = the signal behind the step, e.g. INT-004 #3,
"assumed A1" when nobody asked for it (see Assumptions), or "proposed" for a proposal to confirm. Step ids never change; a removed step keeps its id. -->

| Step | Actor does | System does | Source |
|------|------------|-------------|--------|
| S1 | | | |

## Other flows

<!-- ### A1 — <condition> (from S2)   an alternative path
     ### E1 — <what goes wrong> (from S3)   an error path. Same table as the main flow. -->

## Rules

| Rule | Short statement | Applies at |
|------|-----------------|------------|

## Assumptions

<!-- What we will build that no source asked for, with the reason. Confirmed when the file is approved.
- A1: <statement> — why: <reason> (S3) (owner: client) -->

## Open questions

<!-- - [ ] Q: <one decision?> (owner: client)
       Options: a) <our pick> (recommended) · b) <another> · c) <another>
       A: -->

## Changelog

- v1 ({{date}}) — created
