---
id: INT-
type: intake
kind: requirement        # requirement | feedback | mixed | info (ops/admin — captured, never processed into signals). The ONLY judgement /intake makes.
title:
status: raw
source: email            # email | meeting | direct
source_ref:              # email: thread subject; meeting: name + date; direct: URL, filename, or "user input YYYY-MM-DD"
source_ids: []           # email: provider's conversation id + message ids (Outlook), or thread id (Spark); meeting: provider's meeting id (Fathom, Spark, or Firefly); direct: URL (for link intakes) — used for re-run dedup. Provider chosen by email_provider/meeting_provider in project.md.
attachments: []          # vault-relative paths to attached files — 00-Inbox/_attachments/<INT-id>/<filename>
participants: []
declared_features: []    # direct intake only: feature slug(s) the USER named at capture (1 or many).
                         # A floor, not a ceiling — /extract-signal anchors these AND still scans every
                         # signal for features beyond them. Empty/absent = /extract-signal anchors from
                         # scratch as normal. Never agent-inferred (that would break capture-only, hard
                         # rule 5): only what the human actually selected or typed goes here.
feature:                 # filled by /extract-signal once known — the RESOLVED single anchor, and the
                         # repair channel a human writes a slug into to close a "which feature?" open
                         # question (conventions.md § Signal → feature mapping). Distinct from
                         # declared_features above: that's the user's up-front declaration, this is the
                         # outcome.
links: []
tags: []                 # add needs-review when sender/invitee isn't a known client contact, or when a signal couldn't be mapped to a feature and needs a human to pick one
updated:
---

## Raw
<!-- verbatim email body / transcript, newest appended at bottom. /intake writes ONLY this section (plus attachments + frontmatter) — capture, never interpret. -->

## Extracted signals
<!-- populated by /extract-signal (step 3), NOT at intake. One ROW per signal, each traced to a message (sender + date), transcript timestamp, or attachment — never prose bullets. -->
<!-- This is the RAW RECORD and it stays flat: arrival order, never merged, never grouped, however many rows describe the same thing. It's what the fidelity check quotes against and what every later stage re-reads to see what was actually said. Grouping happens only on the feature hub, where these rows file as themed Signal Log rows citing their # back here (conventions.md § Feature Hub) — so the two tables' row counts are not meant to match. -->

| # | Type | Signal | Why | Source | Feature | Status | Notes |
|---|------|--------|-----|--------|---------|--------|-------|

<!-- Type: requirement · constraint · decision · feedback · question · answer · concern · problem · pain-point -->
<!-- Why: the client's stated reason, quoted/tightly paraphrased — required for requirement/feedback rows, or "not stated" which spawns a question row. Blank for other types. -->
<!-- Source: transcript timestamp link (meeting) · "<sender> <date>" (email) · attachment filename -->
<!-- Feature: the FEATURES.md slug this signal anchors to (conventions.md § Signal → feature mapping) — "unresolved — candidates: a | b" or "unresolved — none found" if it can't map yet. Never guessed. -->
<!-- Status: new · held · staged · applied · question · conflict · superseded · rejected — same vocabulary as the Feature Hub's Signal Log (conventions.md § Feature Hub), so a signal's state reads the same at both levels. -->
<!-- Notes: staging/destination detail ("staged on FR-001 Discussion"), corrections ("corrected: ..."), cross-refs to other rows, superseded-by, or an open question's ↦ FR-### mirror. -->
<!-- # is assigned once and never renumbered within this note. Corrections edit the row in place; genuinely new signals append as new rows in arrival order. -->

## Open Questions
<!-- written by /extract-signal when a signal needs a human answer (missing rationale, ambiguous feature mapping); the note is parked status: needs-clarification until these are answered. -->
<!-- ANSWER HERE: fill the A: line and tick the box — the next /extract-signal run folds it in and un-flags this note. ↦ FR-### = the question's canonical copy on the FR, written once /bigin-transform-signal has drafted or updated one for this signal (↦ — when no FR exists yet). -->
<!-- - [ ] Q: ... (owner: client|team) ↦ FR-###
       A: -->
