# Conventions — intake and feedback

Where raw material comes from, how a capture is written, how the question loop closes, and how
feedback on an already-built thing is handled.

**Read by** `/bigin-intake`, and by `/extract-signal` only when a note is a fold-in.

## Intake sources

`/bigin-intake` accepts three source types, recorded in the `source:` frontmatter field:

| `source:` | What it is | `source_ref:` | `source_ids:` |
|---|---|---|---|
| `email` | Message or thread from the project's `email_provider` (Outlook MCP, or Spark Desktop via the `spark` CLI) | Thread subject | Conversation id + message id(s) (Outlook) or thread id (Spark) |
| `meeting` | Transcript from the project's `meeting_provider` (Fathom MCP, Spark CLI, or a connected Firefly MCP) — or drop-folder fallback | Meeting name + date | Provider's meeting id |
| `direct` | User-typed description, fetched URL, or local file | URL · filename · "user input YYYY-MM-DD" | URL (link intakes only) |

**Provider config**: `email_provider` and `meeting_provider` in `_bigin/system/project.md`
frontmatter select which tool `/bigin-intake` talks to for each source type (default `outlook` /
`fathom` when unset, for vaults created before this field existed).

**Direct intake** is a first-class path — triggered when the user provides text, a URL, or a file
path along with `/bigin-intake` instead of (or alongside) the automated pull. It creates an INT
note with `source: direct`; all other rules (dedup, `kind:`, `## Raw`, attachment handling) apply
identically.

It is also the **only** path that can carry `declared_features:` — the feature slug(s) the user
named at capture — because it's the only one with a human present when the note is written. Email
and meeting notes are pulled unattended, so they have nobody to ask and always anchor from the
signals in `/extract-signal`. Semantics: `registers.md` § Signal → feature mapping → Declared features.

## Intake capture & the question loop

`/bigin-intake` is **capture-only**: it writes frontmatter, verbatim `## Raw`, attachments, plus two
bookkeeping sections — `## Capture history` (what was fetched, what failed) and `## Referenced but not
captured` (things the source points at but doesn't contain, such as files pasted into meeting chat).
Nothing else. `## Raw` holds source text only: a retry narrative written there is read downstream as if
the client had said it. The only judgement intake makes is the `kind:` filing label.

`## Raw` is a **container of source blocks**, not a body of text — one
`### SRC-<n> · <kind> · <ref>` block per artifact captured, `kind` being
`transcript · summary · email · attachment · webpage · note`, each mirrored as an entry in the
`raw_sources:` frontmatter manifest. `/extract-signal` plans its reads from that manifest and reads
every block on it, so a source with no block is a source nothing downstream will ever see. Three rules
carry the weight: a meeting stores its **full transcript** in its own block and the AI recap in a
separate `summary` block (derived text — navigable, never quotable as a signal or a `Why`); an
attachment gets a block holding its text, or its path when binary; and an append is always a **new**
block, never merged into an existing one.

All interpretation belongs to `/extract-signal`, which fills the note's `## Extracted signals` table
(`_bigin/templates/intake.md`): one row per signal —
`# | Type | Signal | Why | Source | Feature | Status | Notes` — each traced to a message,
timestamp, or attachment.

Every claim is classified **as-is / pain / to-be** before it is typed
(`_bigin/stages/extract/2-extraction.md` § Classify first): a description of the system being replaced
is a `decision`, a named frustration is a `pain-point`, and only a statement about the new system is a
`requirement`. This matters because most client sessions are a walkthrough of the incumbent product, and
an extractor that skips the call records the software being thrown away as the specification for its
replacement.

A `Why` is carried by `requirement`/`feedback` rows only, and is one of three values: the client's stated
reason · `derived from #<n>` (a to-be inferred from as-is + pain rows, flagged for client confirmation) ·
the literal `not stated`. A guessed rationale is never acceptable. `not stated` rows are recorded as
such; the ones whose missing reason would change what gets built are raised together in **one** batched
question rather than one question each — a note carrying dozens of checkboxes gets none of them answered.

`/extract-signal` records that call **on the row**, in `Notes`: `rationale: in question` for a row
carried in the batched question, `rationale: non-blocking` for one deliberately left unasked
(`3-filing.md` § Step 5). `/bigin-transform-signal` reads that marker and nothing else to decide
whether the row blocks (`2-qualification.md` § Gate 1). A `not stated` rationale is **never itself a
blocker**: a non-blocking row qualifies with the gap carried verbatim onto its staged entry, and an
unmarked row qualifies the same way and is reported as a filing gap — never parked. Parking on a
missing reason nobody asked about strands the requirement behind a remedy that cannot clear it.

`Feature` and `Status` make the row's anchor and progress machine-readable — `Status` reuses the same
vocabulary as the Feature Hub's `## Signal Log` (`feature-hub.md` § Feature Hub) so a signal reads the same state at both
levels.

This table is the vault's **raw signal record**, and it stays flat: one row per signal in arrival
order, never merged or grouped, however many rows describe the same thing. It's what the source
audit quotes against and what every later stage re-reads to see what was actually said, so a merge
here destroys evidence. Grouping is the *hub's* job — these rows file onto the Feature Hub as
themed Signal Log rows citing their `#` back here (`feature-hub.md` § Feature Hub).

Questions raised by `/extract-signal` live **only on the source INT note's `## Open Questions`** —
`- [ ] Q: … (owner: client|team) ↦ —` with an `A:` answer line. **There is no UC mirror of an
extract-stage question**, by design: the filing stage never touches a UC (`3-filing.md` § Scope), so a
promised mirror would be a promise nothing keeps — the note would read as having a copy elsewhere while
the UC had nothing. The `↦` field stays `—` until a later stage rewrites it to `↦ UC-###` as a *pointer*,
not a second copy of the question.

A question about UC content is raised on the UC by `/bigin-transform-signal` instead
(`3-lane-uc.md` § Questions), and that one *is* the canonical copy of itself. When both exist for the same
ambiguity, that is the "one question, two places" bug below, not a mirror.

A note left with unanswered questions is parked `status: needs-clarification`: that flag is what surfaces
it for the human to jump in. Three ways to close a question:

- **Answer inline**: fill the `A:` line, tick the box. The next `/extract-signal` pass folds the
  answer in, ticks the UC copy, and flips the note to `in-review`.
- **Answer arrives from the client**: `/bigin-intake` appends the reply to the note and resets it
  `status: raw`, which re-enters the extraction queue; extraction matches the reply to the open
  question as an `[answer]`.
- **Answer arrives inside a *different*, later note**: that note's own extraction produces an `answer`
  row, and filing ticks **both** copies — the question where it was raised, and this note's — citing the
  resolving `INT-###` (`3-filing.md` § Step 5b). Without that fold-back the earlier note sits
  `needs-clarification` forever with an unticked box, reading as blocking when the answer has been on
  record for weeks.

### One question, two places — never two questions

A `question`/`concern` row in `## Extracted signals` and its `## Open Questions` line are **two
views of one question**, not two questions. The row is the extraction ledger entry (what was
found, where, what state it's in); the `## Open Questions` line is the human-facing copy — the
one thing to answer. Three rules keep them one question:

1. **Never re-word the mirror into a second question.** The mirror may add context the human
   needs to answer (which UC it collides with, what's already decided) — but the *ask itself*
   must be recognisably the same sentence as the row's `Signal` cell, not an independently
   composed question. Two separately-drafted phrasings of one ambiguity read as two open items
   to a human, get answered twice, and cannot be paired back up by any tooling: the wordings
   routinely share too few words for text matching to help.
2. **Every `question`/`concern` row gets a mirror**, in the same run that writes the row. A row
   with no mirror is a question the human is never shown — the note reads as "nothing to
   answer" while the ledger says otherwise.
3. **`## Open Questions` is authoritative for reading.** Anything that surfaces questions to a
   human reads that section and stops there when it has items; the signal table is a
   **fallback**, read only when the section is empty (rule 2 was violated). A ticked row in the
   section counts as an item: its ledger twin is answered history, not something to ask again.
   Reading both formats is what double-renders every mirrored question, so don't reintroduce it.

## Feedback handling

Feedback is just intake (`kind: feedback`) — and CR material against a UC can equally well arrive
as an ordinary `kind: requirement` signal from a meeting/email that happens to touch shipped scope.
Either way, `/bigin-transform-signal` applies it to the affected UC/BR **the same way, regardless
of that UC's current status** (hard rule 7 — approval no longer freezes a UC, and neither does
the feature shipping):

- **Update in place, always.** Edit content, bump `version`, log the reason + source `INT-###` in
  `## Changelog`. If the UC was `approved` (or `enriched`/`consolidated`), the same edit also sets
  `status` back to `draft` — un-staging it as feature material (`feature-hub.md` § Feature material) until the
  human re-approves. Interactively,
  this runs as a discussion round in the UC's `## Discussion`: present the proposed change (quoted
  signal + INT id + proposed edit), the human confirms, the answer folds in. Unattended, the
  proposed change is written into the UC's `## Discussion` and its Signal Log row flips to
  `staged` — never auto-applied without a human confirming — and the UC's `status` moves to
  `needs-clarification` so the pending decision surfaces exactly like any other UC awaiting a
  human look.
- **There is no forking to a new `amends:`-linked sibling UC for this case.** The same UC carries
  its whole history in its own `## Changelog` — whether it's still open, already approved, or the
  feature has since shipped. `amends:` frontmatter is reserved for the rare case where a feature's
  scope genuinely splits into a second, independent decision that doesn't belong in the same
  document; confirm that split explicitly with the human before minting a second UC for one slug —
  never reach for it just because the source UC happens to be `approved`.
- **Removing scope.** If a discussion round concludes the UC's scope — or part of it — should come
  out entirely (the client walked it back, it's no longer wanted), a human sets `status: removed`
  with the reason in `## Changelog` (human-gated like `approved`; an agent may raise this as an
  Open Question, never set the status itself). This is not deletion (hard rule 1): the file, its
  id, and its full history stay intact. Cascade the same as any other edit (below) so every
  downstream artifact that traced to it surfaces as needing a human decision, rather than silently
  going stale with no explanation.
- **Reinstating.** A human can later move a `removed` UC back to `draft` if the scope returns —
  logged in `## Changelog` with why. `/bigin-transform-signal` never does this unattended; a
  signal that looks like "bring this back" is an Open Question for the human, the same as any
  judgement call an agent can't make on its own.
- Either way — cascade: set the downstream PRD/epic/story/prototype that trace (via
  `sources`/`links`) to the affected UC back to `draft` too (a changelog entry on each citing
  the INT id and naming the upstream UC change that triggered it), so stale artifacts surface
  until `/approve-uc`/`/bigin-generate-design` re-run.
- Open questions with owner `client` stay listed in the (current) UC's `## Open Questions` for the
  human to raise with the client; answers return through `/bigin-intake` as feedback.
