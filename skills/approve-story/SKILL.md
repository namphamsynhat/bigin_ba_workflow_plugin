---
name: approve-story
description: "Approve user stories (US-###) or a whole epic (EP-###) after human review: re-reads live content, refuses any story with an open § 8 question or an unticked Definition of Ready, then sets status approved. Use on \"approve US-004\", \"approve the booking stories\", \"sign off EP-002\"."
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
* **Writes only the story and epic files** — `status`, `version` bump, `updated`, a `## Changelog` line, and on
  the hand-off step the engine-rendered `_cards.md`, `_build/`, `_estimate.md` and `_jira.md`. Never a UC,
  hub, snapshot, or another epic. The hub's `## Epics & Stories` status column is refreshed by the next
  `/bigin-generate-stories` run (or `bigin hub refresh <slug>`).

## Procedure

```text
1  resolve      US-### → its file under 03-Epics-Stories/*/ ; EP-### → the epic and every story in stories:
2  check        per story: the four blockers above, from disk
3  summarise    run `scripts/bigin card <US-###|EP-###>` and show its card stack — one card per screen /
                back-end process: Before → After with its intake cite, rules, out of scope, open questions,
                acceptance titles. Review BY EXCEPTION: put the "AI assumed" lines first and ask the human
                to confirm or kill each one; the engine already checked coverage, AC tags and business
                language, so do not re-check those. Then per story one line: title · priority · "drifted"
                or "current" · blockers. For an EP: the § 3 story map first.
                A confirmed assumption → a § 8 **Decisions** line; a killed one or a new question → a § 8
                `- [ ] Q:` (blocks approval) or a direct intake note when it changes the requirement.
4  ask          AskUserQuestion: approve the clear stories? (list them; blocked ones are named, not offered)
5  write        per approved story: status: approved, version +0.1, updated: today,
                Changelog "| <v> | <date> | Approved | <human> |"
6  epic         every story in the epic's stories: now approved → offer to approve the epic the same way
7  report       approved · blocked (with reason) · epic status · next: hand to development
8  hand-off     (offer, never automatic) for the approved stories:
                · `scripts/bigin card <EP-###> --write` — the cards for the 15-minute BA + Dev + QC walkthrough
                · `scripts/bigin card <US-###|EP-###> --for agent --write` — one build pack per story in
                  `_build/`, the file the dev gives their coding agent (stamped US-###@version)
                · `scripts/bigin card <EP-###> --estimate` — the estimate sheet the dev fills (keeps their lines)
                · `scripts/bigin card <EP-###|US-###> --for jira --write` — `_jira.md`, paste-ready text
                  per story (summary + description = cards + AC). A human copies it into Jira.
                  NEVER create or edit Jira issues yourself.
```

## Estimate check (when the dev returns `_estimate.md`)

Read the sheet against the cards, row by row. A task line under a key with no matching card row means the dev
misread the scope or their AI added scope; a card row with no task means scope was missed. Raise both with the
dev as a scope question first. Only when the BA still finds the total too high does the dev lead review it.

## Reopening

A human who wants to change an approved story sets it back to `draft` themselves (or asks you to, explicitly). The
next `/bigin-generate-stories` run may then update it. This skill never reopens anything on its own.
