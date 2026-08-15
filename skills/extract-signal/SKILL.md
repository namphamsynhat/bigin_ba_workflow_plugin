---
name: extract-signal
description: This skill should be used when the ask is to extract signals, process the intake queue, drain 00-Inbox, or map intake to features. This skill will drain the raw intake queue in 00-Inbox — extract each INT-### note's signals into a flat raw record on the note, audit that record against the source in both directions, then anchor every signal to a FEATURES.md slug and file it onto that feature's Signal Log grouped by functional theme. A signal that can't be anchored raises a written question on the note instead of a guess, parking it needs-clarification until a human supplies the slug. Never drafts or edits a UC — that's a later step.
argument-hint: "[resume]"
disallowed-tools: AskUserQuestion
---

# Extract Signal

Drains the raw intake queue `/bigin-intake` fills in `00-Inbox`: per eligible `INT-###` note, extract signals into its `## Extracted signals` table, audit that table against the source in both directions, then anchor each signal to a feature and file it onto that feature's hub.

This is the Extract stage of the extract → transform → load pipeline. An unanchorable signal becomes a written question, never a guess.

> **Artifact Standard:** Outputs two deliberately different tables:
>> **The raw record** — the note's `## Extracted signals`: one flat row per signal, arrival order, never grouped. Every later stage reads this instead of the source; `/bigin-transform-signal` never re-opens `## Raw`.
>> **The working register** — the hub's `## Signal Log`: the same signals grouped by functional theme, one row per theme (§ Themed hub rows). Row counts between the two won't match, and shouldn't.

---

## Non-Negotiable Core Rules

* **Recall is the point:** a wrong row is caught in review, a missing one is invisible forever. A signal that never lands in the table is a requirement that never existed, and nothing downstream can detect it. Every rule below follows from that asymmetry.
* **No guessed anchors:** a signal matching no `{requirements_file}` slug becomes a question on the note, never the slug that looked closest (§ The feature-mapping loop).
* **No new feature rows:** a signal revealing a genuinely new feature raises the question and stops. A slug is permanent and everything downstream anchors to it — a human's call, and this skill has no `AskUserQuestion` to make it any other way.
* **Never touches a UC or BR:** only a hub's Signal Log plus the vault-wide registers a signal populates directly. Folding a filed signal into a requirement is a later step.
* **Extractor blind to themes:** the extraction subagent is never told about themes, hubs, or consolidation. One that knows its rows will be grouped downstream starts pre-grouping them here, and the raw record is the one place where that is unrecoverable.
* **Audit before filing:** nothing reaches a hub until the source audit is clean — a bad row is corrected in the table, not surgically removed from a themed hub row later.
* **Sequential within a batch:** two notes can anchor to the same feature, and parallel edits to one hub file race.
* **Resume = re-run:** the vault is the only state; every run rescans `{inbox_dir}` fresh.

---

## Paths

| Variable | Target path | Description |
| :--- | :--- | :--- |
| `{inbox_dir}` | `00-Inbox` | Intake notes — skip `_attachments/` when scanning |
| `{requirements_file}` | `01-Requirements/FEATURES.md` | The slug registry; a signal can only anchor to a slug listed here |
| `{hub_dir}` | `01-Requirements/_features/<slug>.md` | One Feature Hub per slug |
| `{uc_dir}` | `01-Requirements/_ucs` | Read-only here — scanned for open questions (§ Step 1) |
| `{conventions_reference}` | `_bigin/conventions/conventions.md` | The rulebook: ID scheme, frontmatter schema, artifact conventions |
| `{extraction_rules}` | `_bigin/stages/extract/2-extraction.md` | Signal catalog, segmentation, `Why` discipline — the **extraction** subagent's only rulebook |
| `{filing_rules}` | `_bigin/stages/extract/3-filing.md` | Anchoring, hub schema, themed consolidation, registers, questions, status — the **filing** subagent's only rulebook |
| `{conventions_file}` | `.claude/bigin-ba-workflow-plugin.local.md` | Optional project overrides. A plugin setting, not project data, hence `.claude/` |
| `{pain_points_file}` | `01-Requirements/PAIN-POINTS.md` | Canonical `PP-###` register; each hub mirrors its own rows from here |
| `{entities_file}` | `01-Requirements/ENTITIES.md` | Candidate `EN-###` rows; no hub mirror |
| `{design_principles_file}` | `01-Requirements/DESIGN-PRINCIPLES.md` | Durable cross-cutting constraints; no hub mirror |
| `{template_*}` | `_bigin/templates/*` | Scaffolds (`feature-hub`, `pain-points-register`, `entities-register`, `design-principles-register`) |

All paths are project-relative, materialized by `/bigin-new-project`. Confirm `{extraction_rules}`,
`{filing_rules}`, and `{conventions_reference}` exist before building the queue — if any is missing,
stop and say `/bigin-new-project` must run first. A subagent that can't read its rules doesn't fail
loudly; it improvises and reports success.

## Execution order

| # | Step | Runs in |
|---|---|---|
| 1 | **Build the queue** — collect eligible notes plus the open questions they might answer | orchestrator |
| 2 | **Process the queue** — extract → audit → file, one note at a time, batches of 5 | three subagents per note |
| 3 | **Verify the filing** — check the batch's own claims against the hubs | one subagent per batch |
| 4 | **Report** — coverage, audit, filings, what's parked | orchestrator |

## Step 1 — Build the queue

* **Goal:** establish which notes are eligible this run, and what open questions their signals could answer.
* **Action:** Scan `{inbox_dir}` for `INT-###` notes and read each frontmatter:

  | Frontmatter state | Verdict |
  |---|---|
  | `kind: info` | Skip — operational/admin capture, never refined into signals |
  | `status: raw` | Eligible, fresh run |
  | `status: needs-clarification`, **≥ 1** `- [ ] Q:` box newly checked | Eligible as a **partial fold-in** — harvest the answered questions, leave the rest parked |
  | `status: needs-clarification`, nothing newly answered | Still waiting on a human |
  | Any other `status` (`in-review`, `consumed`, …) | Already processed, skip |

  Then scan `{uc_dir}` and `{inbox_dir}` once for every unchecked `- [ ] Q:` line — on a use case that
  list is its `## 5` **Still open** section — and pass it to each extraction subagent. **≤ 40 questions:**
  pass the full list. **> 40:** scope to `{inbox_dir}`'s questions plus `{uc_dir}` questions for features
  in the note's `declared_features`.

  Empty queue: say so and stop. Otherwise report the full list and continue.
* **Rules:**
  - **Partial fold-in beats waiting.** Holding for every box strands the answered questions behind the slowest one on the page.
  - **The question list is what makes `answer` typing possible.** Without it, a statement resolving someone else's question lands as a generic requirement or is dropped as restated context.

## Step 2 — Process the queue

* **Goal:** turn each note's `## Raw` into an audited raw record, then file it onto the right hubs.
* **Action:** Batches of **5**, reporting after each (§ Step 4) before the next. Within a batch, notes run
  sequentially. Each note runs three subagents in fixed order, each fresh (`Agent`, `general-purpose`,
  foreground) — never reuse a prior note's subagent, which grows its context instead of resetting it.
  Prompts are in **`references/agent-dispatch.md`**; use them verbatim rather than re-deriving their shape.

  | # | Subagent | Model | Reads | Writes |
  |---|---|---|---|---|
  | 2a | Extract | session default, or `sonnet` | the note's `## Raw`, `{extraction_rules}` | one flat row per discrete signal into `## Extracted signals` — `#`/`Type`/`Signal`/`Why`/`Source`, leaving `Feature`/`Status`/`Notes` blank |
  | 2b | Source audit | `sonnet` | `## Raw` first, the table second | a two-direction gap report the orchestrator repairs the table from |
  | 2c | File | `haiku` | the finished table, `{filing_rules}`, `{requirements_file}` — **never `## Raw`** | `Feature`/`Status`/`Notes`, themed hub rows, register mirrors, questions, the note's `status` |

* **Rules:**
  - **2a segments the source first** and reports rows per segment. A single pass over a long transcript captures each topic's throughline and drops the one-line asides inside it; segmenting makes that loss visible instead of silent. A segment with zero rows is a claim, not a gap in the report.
  - **2b runs in both directions.** *Source → rows (recall):* read `## Raw` only — `grep -n` the section's line range and `Read` that range, so the existing table stays out of context — and independently list every discrete claim with a quote, **written before the table is opened**. An agent that reads the table first confirms it instead of auditing it. *Rows → source (fidelity):* then open the table and report both a row with no locatable quote and a claim with no row.
  - **The orchestrator repairs, never the auditor.** Diff the two lists, append gap rows from the audit's own quotes (no re-reading the source), correct or downgrade unsupported rows. The table ends as the **union of two independent passes** — that union is where the recall gain comes from. Procedure: `references/agent-dispatch.md` § Repairing the table.
  - **2c sets `status` last,** only after confirming every hub write is on disk. A flip to `in-review` drops the note from every future scan, so an unwritten row would vanish silently.

## Step 3 — Verify the filing

* **Goal:** check the batch's own claims before it is reported as done.
* **Action:** One `Agent` (`haiku`, `general-purpose`, foreground) per batch. Per note and per slug reported, confirm: `{hub_dir}`'s `## Signal Log` cites that `INT-###`; **every anchored row number in the note's table appears in exactly one hub row's `Source` cite** — none missing, none cited twice; the note's `status` matches its `## Open Questions` state.
* **Rules:**
  - **Row counts are not the check.** A themed row covers several note rows by design, so counting hub rows against note rows flags every correct consolidation and misses the one thing that actually goes wrong — a signal dropped inside a merge.
  - **Any mismatch is blocking.** Dispatch one targeted repair subagent to file the uncited row(s) from the already-extracted table onto the correct hub (no re-extraction), then re-check that note. A note reporting success while missing its hub row is stranded, not done.

## Step 4 — Report

```text
processed: N notes
coverage: INT-###: M segments, N rows (segments with 0 rows: <list, or none>)
          field tables: <N fields → N rows, or none>
audit: INT-###: N claims found in source, N gaps appended, N rows narrowed, N downgraded to question
signals filed: total — per feature, e.g. <slug>: N signals in M themed rows (Signal Log rows #a-#b)
parked — awaiting an answer: INT-### (N question(s) unanswered)
parked — awaiting a feature mapping: INT-### (signal(s) unresolved — human writes the slug into the A: line)
verification: clean | repaired (list what)
remaining in queue: N — re-run this skill to continue
```

The `coverage` and `audit` lines are the point of the report, not decoration: they are the only place
under-extraction is ever visible. A run whose audit appended gaps was a run that would otherwise have
lost those requirements — say so plainly rather than folding it into "clean".

## Themed hub rows

A hub row answers "what did this note tell us about this feature?", not "what was signal #4?". The
signals a note contributes to one feature are filed **grouped by functional theme** — one row per
theme, carrying every member's detail as its own clause.

The test for a theme is *would a drafter write these into one requirement statement?* Adjacency isn't
a theme; sharing a slug isn't a theme; a theme of one is normal and needs no forcing.

```text
note INT-014 ## Extracted signals — the raw record, still three flat rows:
  #3 requirement  age is computed from date of birth
  #5 decision     the cut-off is 1 September
  #7 constraint   under-18s need guardian consent

hub enrolment-eligibility ## Signal Log — one themed row:
| # | Signal | Type | Source | Status | Destination | Notes |
| 7 | **Age eligibility** — age is computed from date of birth; the cut-off is 1 September; under-18s need guardian consent | requirement + constraint + decision | INT-014 #3, #5, #7 — Jane Doe 2026-08-05 | new | | |
```

The `Source` cite's row numbers are the traceability that replaces one-row-per-signal, and Step 3
verifies every anchored note row appears in exactly one of them.

Four things never merge — full rules in `{filing_rules}` § Consolidating into themed hub rows:

- **Different notes or runs.** The log is append-only; a continuing theme cites the older row as `Notes: extends #<n>`.
- **Different `Status`.** Only `new` rows consolidate.
- **Presentation vs. behavioural.** Different lanes, and the design lane skips the approval gate.
- **Contradicting signals.** That's a `conflict`, not a merge.

Over-merging is the failure mode to watch. A row that reads like one ask but hides four is worse than
a long log — the detail a drafter needs is still on the page but no longer legible as separate
obligations.

## The feature-mapping loop

A signal matching no `{requirements_file}` slug becomes a question on the `INT` note (owner: team,
tagged `needs-review`), and the note flips to `needs-clarification`. Wording depends on why the match
failed (`{filing_rules}` § Anchoring a signal to a feature):

- **Ambiguous among existing slugs:** the question asks which one.
- **Nothing fits:** the question ships with a **drafted slug and one-line scope** — a proposal to confirm or edit, not a blank line to fill.

A human resolves it by writing the slug into the `A:` line — minting a `proposed` row first if the
scope is genuinely new — and ticking the box. The next run folds the note in and anchors it properly.
No separate command, no re-extraction of what was already correct.

## Additional resources

Paths and templates are in § Paths. **`references/agent-dispatch.md`** holds the four subagent prompts
(extraction, source audit, filing, batch verification), the table-repair procedure the orchestrator
runs on an audit finding, and the hub-repair procedure for a Step 3 mismatch.
