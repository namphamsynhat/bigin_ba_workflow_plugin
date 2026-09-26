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
raw_sources: []          # manifest of ## Raw's blocks, one entry per "### SRC-n" — "SRC-1 · transcript · <ref>".
                         # /extract-signal builds its read plan from this without opening the body.
                         # A source missing here is a source nothing downstream will ever read.
participants: []
declared_features: []    # direct intake only: feature slug(s) the USER named at capture (1 or many).
                         # A floor, not a ceiling — /extract-signal anchors these AND still scans every
                         # signal for features beyond them. Empty/absent = /extract-signal anchors from
                         # scratch as normal. Never agent-inferred (that would break capture-only, hard
                         # rule 5): only what the human actually selected or typed goes here.
feature:                 # filled by /extract-signal once known — the RESOLVED single anchor, and the
                         # repair channel a human writes a slug into to close a "which feature?" open
                         # question (`registers.md` § Signal → feature mapping). Distinct from
                         # declared_features above: that's the user's up-front declaration, this is the
                         # outcome.
links: []
tags: []                 # add needs-review when sender/invitee isn't a known client contact, or when a signal couldn't be mapped to a feature and needs a human to pick one
updated:
---

## Raw
<!-- ALL captured source material, one "### SRC-<n> · <kind> · <ref>" block per source, verbatim. /extract-signal reads this section and nothing else: a source with no block here does not exist downstream. Mirror every block into raw_sources: above. -->
<!-- kind: transcript | email | attachment | webpage | note | summary -->
<!-- A `summary` block (a meeting tool's AI recap) is DERIVED text: navigation only, never quotable as a signal or a Why. Label it as such and capture the real transcript in its own block — a summary is not a substitute for one. -->
<!-- A binary or oversized attachment gets a block holding its PATH instead of its text; the extractor opens the file. Everything else is inlined verbatim. -->
<!-- Append newest content as a NEW block. Never edit, merge, or trim an existing one. -->
<!-- SOURCE CONTENT ONLY. Fetch failures, retries, provider fallbacks, re-filings go in ## Capture history below — never here. Anything written here is read by /extract-signal as if the client said it. -->

### SRC-1 · `<kind>` · `<ref>`

## Capture history
<!-- written by /bigin-intake. One line per capture attempt: date, what was tried, what happened. Keeps ## Raw clean. Delete nothing — a failed attempt is the audit trail for why content is missing. -->
<!-- - YYYY-MM-DD (attempt N) — <what was tried> → <result: captured | FAILED, reason> -->

## Referenced but not captured
<!-- written by /bigin-intake. Things the source POINTS AT but does not contain: files pasted into meeting chat, linked spreadsheets/forms, documents named but not attached. -->
<!-- Why this section exists: meeting-provider APIs return transcript + summary only, never chat. Without this list /extract-signal either invents the missing content or drops it silently, and no human knows to go fetch it. -->
<!-- - <what it is> — <where it was referenced: timestamp / sender+date> — <how to get it> -->

## Extracted signals
<!-- populated by /extract-signal (step 3), NOT at intake. One ROW per signal, each traced to a message (sender + date), transcript timestamp, or attachment — never prose bullets. -->
<!-- This is the RAW RECORD and it stays flat: arrival order, never merged, never grouped, however many rows describe the same thing. It's what the source audit quotes against and what every later stage re-reads to see what was actually said. Grouping happens only on the feature hub, where these rows file as themed Signal Log rows citing their # back here (`feature-hub.md` § Feature Hub) — so the two tables' row counts are not meant to match. -->
<!-- Filled in two passes by /extract-signal: the extraction subagent writes #/Type/Signal/Why/Source and leaves Feature/Status/Notes blank; the filing subagent fills Feature/Status/Notes once it has read FEATURES.md. A row left with both Feature and Status blank is one nobody filed and nobody questioned. -->

| # | Type | Signal | Why | Source | Feature | Status | Notes |
|---|------|--------|-----|--------|---------|--------|-------|

<!-- Type: requirement · constraint · decision · feedback · question · answer · concern · problem · pain-point · commitment -->
<!-- Every claim is classified as-is / pain / to-be BEFORE it is typed: as-is → decision · pain → pain-point/problem · to-be → requirement. See _bigin/stages/extract/2-extraction.md § Classify first. -->
<!-- Why: required for requirement/feedback rows. One of three values: the client's stated reason (quoted/tightly paraphrased) · the literal "not stated" · "derived from #<n>, #<n>" for a to-be nobody said aloud. Blank for every other type. -->
<!-- Source: transcript timestamp link (meeting) · "<sender> <date>" (email) · attachment filename. Cite the timestamp block the quoted words actually appear in. Name a speaker only when who said it matters and is unambiguous — transcript speaker labels merge multiple speakers into one block and cannot be trusted. -->
<!-- Feature: the FEATURES.md slug this signal anchors to (`registers.md` § Signal → feature mapping) — "unresolved — candidates: a / b" or "unresolved — none found" if it can't map yet. Never guessed.
     Separate candidates with " / ", never "|" — a raw pipe inside a table cell splits the row. -->
<!-- Status: new · question · conflict · rejected — the only four values /extract-signal writes (_bigin/stages/extract/3-filing.md § Scope). held/staged/applied/superseded describe a signal's relationship to a use case and are written later, not here. -->
<!-- Notes: staging/destination detail ("staged on UC-001 Discussion"), corrections ("corrected: ..."), cross-refs to other rows, superseded-by, or an open question's ↦ FR-### mirror. -->
<!-- # is assigned once and never renumbered within this note. Corrections edit the row in place; genuinely new signals append as new rows in arrival order. -->

## Open Questions
<!-- written by /extract-signal when a signal needs a human answer (missing rationale, ambiguous feature mapping); the note is parked status: needs-clarification until these are answered. -->
<!-- ANSWER HERE: fill the A: line and tick the box — the next /extract-signal run folds it in and un-flags this note. ↦ UC-### = the question's canonical copy on the use case, written once /bigin-transform-signal has drafted or updated one for this signal (↦ — when no UC exists yet). -->
<!-- - [ ] Q: ... (owner: client|team) ↦ UC-###
       A: -->
