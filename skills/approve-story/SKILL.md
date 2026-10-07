---
name: approve-story
description: Approve one or more user stories (US-###), or a whole epic (EP-###), once a human has reviewed them and their questions are resolved. Re-reads each story's live content — the reviewer may have edited it directly — refuses any story with an open § 8 question or an unticked Definition of Ready, then flips status to approved so it is ready for development. An epic is approved only when every one of its stories is. Use after /bigin-generate-stories, when the human says "approve US-004", "approve the booking stories", or "sign off EP-002".
argument-hint: "<US-### … | EP-###>"
---

# Approve Story

The human gate between written stories and development. It mirrors `/approve-uc`: re-derive from disk, show the
human what they are approving, flip `status` only on their explicit confirmation.

## Non-negotiable rules

* **Never approve on the human's behalf.** Show the summary, then ask; a yes is the only trigger.
* **Re-derive, don't trust.** Re-read each story file now. Count § 8 **Still open** `- [ ] Q:` lines and § 9 Definition
  of Ready boxes from disk.
* **Blocked stories are reported, not approved:** any open § 8 question · any unticked § 9 box · `snapshot:` names a
  folder that does not exist · an `absorbed:` UC whose current version is newer (the UC drifted since the story was
  written → re-run `/bigin-generate-stories` first).
* **Writes only the story and epic files** — `status`, `version` bump, `updated`, a `## Changelog` line. Never a UC,
  hub, snapshot, or another epic. The hub's `## Epics & Stories` status column is refreshed by the next
  `/bigin-generate-stories` run (or `$BIGIN hub refresh <slug>`).

## Procedure

```text
1  resolve      US-### → its file under 03-Epics-Stories/*/ ; EP-### → the epic and every story in stories:
2  check        per story: the four blockers above, from disk
3  summarise    per story, one block: title · priority · slice_of · screens (with snapshot folder)
                · AC count · "drifted" or "current" · blockers
                For an EP: the § 3 story map and § 7 coverage first, then the stories
4  ask          AskUserQuestion: approve the clear stories? (list them; blocked ones are named, not offered)
5  write        per approved story: status: approved, version +0.1, updated: today,
                Changelog "| <v> | <date> | Approved | <human> |"
6  epic         every story in the epic's stories: now approved → offer to approve the epic the same way
7  report       approved · blocked (with reason) · epic status · next: hand to development
```

## Reopening

A human who wants to change an approved story sets it back to `draft` themselves (or asks you to, explicitly). The
next `/bigin-generate-stories` run may then update it. This skill never reopens anything on its own.
