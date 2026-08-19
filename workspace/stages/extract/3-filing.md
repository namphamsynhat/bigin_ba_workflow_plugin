# Filing rules

Rulebook for the `extract-signal` **filing** subagent (2c).

```text
in:   a note whose ## Extracted signals table is COMPLETE and already audited against the source
out:  each row anchored to a feature · filed onto that hub grouped by theme · registers mirrored
      · questions raised · the note's status set
never: ## Raw, a transcript, or an attachment
       → that judgment was made by a stronger model with the source properly segmented,
         and any disagreement here would silently overwrite it
```

`{variable}` resolves in `_bigin/conventions/paths.md`. Read `_bigin/conventions/conventions.md`
§ ID scheme, § Feature Hub, § Signal → feature mapping, § Open Questions wording, § Pain Point Register,
§ Design Principles Register, § Entity Data Model — those sections only. `{conventions_file}`, if
present, overrides anything here.

## Scope

| May write | Never writes |
|---|---|
| the table's `Feature`, `Status`, `Notes`; the note's `## Open Questions`, `status`, `tags` | any `UC-###`/`BR-###` content |
| a hub's `## Signal Log`, `## Pain Points`, `sources`, `updated` | any `EN-###` document, or a hub's `## Entities` / `## Requirement Readiness` / `## Business Scenarios` |
| `{pain_points_file}`, `{entities_file}`, `{design_principles_file}` rows | the `#`, `Type`, `Signal`, or `Why` of any table row — 2-extraction.md owns those |
| a **checked box + `A:` line** on another `INT-###`'s `## Open Questions`, when a row of this note answers it (§ Step 5b) — nothing else on that note | a `{requirements_file}` row **from your own reading** — a new slug is a human's call. Sole exception: a slug the human themselves declared at capture (§ The declared-slug exception) |

`Status` is one of exactly four values:

| Value | When |
|---|---|
| `new` | the default and the vast majority. **Whether the feature already has a UC is irrelevant — don't check.** |
| `question` | the signal *is* an open question, a `concern` needing a call, or a row the audit couldn't support |
| `conflict` | contradicts an existing Signal Log row, or another row in this same note (§ Conflicts) |
| `rejected` | its feature's `{requirements_file}` row is `status: out-of-scope`. `Notes: out-of-scope — skipped` |

`held`, `staged`, `applied`, `superseded` describe a signal's relationship to a use case. This stage has
no relationship to one, so it never writes them.

## Step 1 — Anchor

```text
for row in table:                       # ROW BY ROW, on its own content
    declared_features first             # a floor, not a ceiling — still match every row independently
        declared slug     → settled, never re-questioned
        declared slug with NO {requirements_file} row → ADD a `proposed` row for it (§ below).
                             The one exception to "never mint a scope row" — it holds only because
                             the slug came from a HUMAN at capture, not from any agent's reading.
        declared, unused  → report as a mismatch — never deleted, never justified with a made-up signal
        near-miss of an existing slug (typo, plural, hyphenation) → flag, never silently remap

    match against {requirements_file} on DESCRIBED SCOPE, not shared keywords
        name alone doesn't settle it, and the slug has a hub
            → open {hub_dir}/<slug>.md, read ## Notes / History + ## Signal Log
              (what the feature has actually come to mean beats a one-line registry row)

    feature is status: out-of-scope  → Status: rejected, "out-of-scope — skipped"     # filed and closed
    spans two features               → file to both hubs, Feature names both          # never split the row
                                       → it is then cited once per hub, and that is correct:
                                         "exactly one hub row" is PER ANCHORED FEATURE
    NEVER check whether the feature already has a use case

    no confident match → NEVER GUESS, and the two failures ask different questions:
        >1 plausible existing slug  → Feature: "unresolved — candidates: a | b"
                                      ranked by how much of the signal each scope covers
        nothing fits, reads as new  → Feature: "unresolved — none found"
                                      + draft a slug and scope (§ below), for the question
    → both are Status: question + an ## Open Questions line
    → NEVER a new {requirements_file} row FROM YOUR OWN READING: a slug is permanent and everything
      anchors to it. The declared-slug case above is the only row this stage ever adds, and a human
      typed that slug themselves.
```

### The declared-slug exception, precisely

`conventions.md` § Declared features is the standard; this is the procedure, stated here because this is
the file the filing stage actually reads. It fires **only** for a slug in the note's `declared_features:`
frontmatter — written by `/bigin-intake` from a human's own multi-select at capture, never from any
agent's reading of content.

```text
declared slug has a {requirements_file} row      → ordinary anchoring, nothing to add
declared slug has NO row, and is NOT a near-miss of an existing slug
    → add ONE `proposed` row to {requirements_file}: the slug, a Feature name in the human's own
      wording, status: proposed, Sources citing this INT-###
    → bump {requirements_file}'s version + append its ## Changelog line
    → REPORT IT EXPLICITLY as a scope row you added, and why (declared at capture on INT-###)
declared slug has NO row but LOOKS like a typo/plural/hyphenation variant of one that does
    → add NOTHING. Flag it in the report naming both spellings, and anchor those rows to the
      existing slug ONLY if their described scope actually matches. Otherwise
      "unresolved — candidates: …". Never silently remap a human's spelling to what you think they
      meant: if they did mean a new feature, that erases it.
```

Everything else — an unmatched row, an ambiguous row, a new-scope proposal you drafted yourself — still
goes through the question path. Those are your reading; this one is the human's declaration.

Adjacency is not evidence. The last rows of a long meeting routinely belong to a feature discussed an
hour earlier. If this note raises a new-feature proposal, every later row falling in that proposed scope
anchors to the **same** proposal, not to a nearby existing slug.

### Drafting a new-feature proposal (never writing it)

```text
suggested slug  = kebab-case, 2-4 words, from the SIGNAL'S OWN vocabulary
                  check {requirements_file} for a near-miss first
                  → a near-miss means this is an ambiguity, not new scope
one-line scope  = the boundary a human must confirm ("does this include X, or just Y?")
                  → not the row's Why restated
both go into the question, so the answer can be "yes" or a one-word edit
```

Drafting, not deciding. Neither is ever written to `{requirements_file}`. A human resolves the question
by writing the confirmed slug into the `A:` line and minting the `proposed` row themselves — and is free
to reject the draft and point at an existing feature instead.

## Step 2 — File to the Feature Hub

Additive only. Create from `{template_hub}` if the slug has no hub. Touch only `## Signal Log`,
`## Pain Points`, `sources`, `updated` — everything else belongs to later stages.

```text
group this note's anchored rows per slug BY FUNCTIONAL THEME → append ONE row per theme
```

Test: *would a drafter write these into one requirement statement?* Two independent requirements = two
themes. Adjacency is not a theme; sharing a slug is not a theme; a theme of one is normal.

| Merge | Don't merge |
|---|---|
| one rule/flow/decision from different angles — the calculation, its cut-off, the constraint on it | rows a drafter would write as two independent requirements, however adjacent |
| a requirement and the constraint qualifying *that same* requirement | a constraint governing the whole feature rather than this one rule |
| several field-level details of the same form, screen, or record | two different screens that came up in the same breath |

**Never merge across:**

```text
notes or runs   → the log is append-only; a continuing theme cites the older row: Notes: extends #<n>
Status          → only `new` consolidates; question/conflict/rejected each file alone
the design line → presentation never merges with behavioural (they route down different lanes)
a contradiction → that's a `conflict`, not a theme
```

Columns — `# | Signal | Type | Source | Status | Destination | Notes`:

| Column | Rule |
|---|---|
| `#` | hub-local, one per theme. Permanent, never renumbered or deleted. A signal superseding an earlier row gets a **new** row; update the old row's `Status`/`Notes` to point at it. |
| `Signal` | `**<Theme>** — <detail>; <detail>; <detail>` — every member's claim as its own clause, in note-row order. **Grouping, not summarizing:** no clause compressed away, none claiming more than its note row did. A theme of one is just that row's text, no prefix. |
| `Type` | member types in catalog order, joined ` + ` — `requirement + constraint`. A theme of one keeps its plain value. |
| `Source` | `<INT-###> #<n>, #<n> — <the note row's own cite>`, e.g. `INT-014 #3, #5, #7 — Jane Doe 2026-08-05`. This is the traceability that replaces one-row-per-signal, and it is what verification checks. |
| `Status` | the four values above. A themed row is always `new`. |
| `Destination` | blank. This stage never stages a signal into a use case. |
| `Notes` | `extends #<n>` · the `PP-###`/entity/design ids its members minted · otherwise blank. |

Over-merging is the failure mode to watch: a row that reads like one ask but hides four. The detail is
still on the page but no longer legible as separate obligations.

**Hub frontmatter.** New hub: `feature`, `name` (the `{requirements_file}` Feature column), `status`
(that row's, mirrored once), `sources: [<INT-###>]`, `updated`. Leave `fr`, `code_areas`, `prd`,
`epics`, `stories`, `uiux`, `entities` at template defaults. Existing hub: add this `INT-###` to
`sources` if absent, bump `updated`, touch nothing else.

## Step 3 — Conflicts inside one note

Two people disagreeing in one meeting is the highest-value thing this stage can surface.

```text
scan this note's rows for pairs where one proposes X and another says X won't work or isn't allowed
    # usual shape: a `concern` right after a `requirement`
→ file BOTH rows, Status: conflict, each on its own row, never consolidated
→ Notes: "conflicts with #<n>" on each, pointing at the other
→ raise ONE ## Open Questions line (owner: client) presenting both positions
→ never invent a resolution, never file only the louder side
```

## Step 4 — Registers

**Per signal, always** — consolidation never collapses a register row.

```text
pain-point → FIRST match against existing {pain_points_file} rows
               match    → cite it in the NOTE ROW's Notes ("same as PP-012 — not re-minted")
                          + add this INT-### to its Source
               no match → mint the next PP-### (from {template_pain_points})
                          + mirror into the hub's ## Pain Points, both copies identical
             EITHER WAY the PP-### goes in the note row's Notes
             → a pain-point with no id is unfollowable
             → skipping the match check fills the register with the same complaint restated weekly

entity/field → match {entities_file} first, else a `proposed` row there (never an EN-### document)
               a field table extracted as N rows produces N entity rows, never one summarizing row

durable cross-cutting design/brand/tone/accessibility/content preference
             → a {design_principles_file} row, IN ADDITION to normal Signal Log filing
             → not durable when it's plainly scoped to one feature

commitment   → its own Signal Log row, Status: new, never consolidated (a promise is not a requirement)
               carries "unblocks #<n>" and that row has a question
                 → append "— awaiting: <the commitment>" to the question
```

Cite the minted ids in the themed hub row's `Notes` as well.

## Step 5 — Questions

```text
raise a - [ ] Q: for:  every unresolved anchor · every audit-flagged row · every conflict pair
                       · every "derived from #<n>" row (an inference, not something the client said)
```

```text
- [ ] Q: <what's missing> (owner: client|team) ↦ —
      A:
```

Anchoring uses one of two specific shapes instead of the generic one — a human should tell them apart
at a glance:

```text
ambiguous  → "Which feature does this belong to — `<slug-a>` or `<slug-b>`? (owner: team) ↦ —"
none found → "No existing feature covers this — proposed new feature `<slug>`: "<one-line scope>".
              Confirm this slug/scope, edit it, or point to an existing feature instead. (owner: team) ↦ —"
```

### Step 5b — an answer that resolves a question raised elsewhere

A later note routinely answers a question an earlier note asked. When it does, the answer has to reach
**both** copies of that question, or the earlier note sits parked with an unticked box forever, reading as
still-blocking when it isn't.

```text
a row of this note ANSWERS an open question on a hub, a UC, or another INT note
    (the orchestrator hands you the touched hubs' open questions; a row typed `answer` usually is one)
→ 1  file the row normally, Status: new, on its own hub row
  2  strike the question where it was raised: tick its box and write the resolution on its A: line,
     citing THIS note — "A: <the answer> — resolved by INT-041"
  3  AND tick the ORIGINATING note's own copy of that question, same wording, same citation
     → this is the step that gets skipped, and it is the one that unparks the earlier note
  4  name every note you ticked in your report — you touched a note you were not dispatched on,
     which nothing else would expect

never invent the link: the row must actually ANSWER the question, not merely share its topic
```

Ticking a checkbox and filling an `A:` line on another `INT-###` note is allowed for exactly this reason
and nothing else. A **UC-side** copy of that question is still not yours: report it, and
`/bigin-transform-signal`'s Stage 1 strikes it (`1-foldin.md` § Reconcile mirrors, item 3).

**Missing rationale is ONE batched question, not one per row — and every row gets marked:**

```text
EVERY requirement/feedback row with Why: not stated gets exactly one Notes marker.
Decide per row: would not knowing the reason CHANGE WHAT GETS BUILT?
    # a threshold, an exception, a gate — anything deciding between two designs

yes → Notes: rationale: in question
      AND a short bullet with its # in the ONE batched owner: client question
no  → Notes: rationale: non-blocking
      no question: recorded, re-askable, not blocking. Transform qualifies it and carries the
      gap into the staged UC entry, where the human sees it at the review gate that already
      exists (2-qualification.md § Gate 1, 3-lane-uc.md § Staging a change)

→ a note with 40 checkboxes gets none of them answered
if >~10 rows qualify → the extraction skipped the Why search. Say so instead of raising 40 questions.
```

**The marker is the point, not the question.** Writing it is what makes "this reason is not worth
chasing" a recorded decision instead of an absence a later stage has to interpret. Transform reads
these markers and nothing else to decide whether a `not stated` row blocks
(`2-qualification.md` § Gate 1) — an unmarked row costs it that decision.

- `↦ —` because no UC exists yet; a later stage rewrites it to `↦ UC-###`.
- `owner: client` when only the client can answer (rationale, ambiguous scope). `owner: team` for an
  internal call (which feature, whether it's in scope).
- Keep the ask recognizably the row's own sentence. Plain language, no vault vocabulary (`signal`,
  `slug`, `anchor`) in a client-owned question. `(a)/(b)/(c)` once there are three or more options.
- Tag the note `needs-review`, set `status: needs-clarification`.
- Never re-raise a question already answered elsewhere on the note.

## Step 6 — Before finalizing

```text
GATE: re-open or grep every {hub_dir}/<slug>.md touched this run, confirm it cites this INT-###
      → status: in-review drops the note from every future scan; an unlanded write is then invisible
      → turns running short? finish the pending hub writes first, in order
      → genuinely can't finish? DON'T finalize — report which slugs are done vs pending

then:
  every table row's # appears in EXACTLY ONE hub row's Source cite PER FEATURE IT ANCHORED TO
      # none missing on a hub it anchored to, none twice on the SAME hub
      # a row spanning two features is cited once on EACH — that is § Step 2's dual-anchor rule
      #   working, not a duplicate. "Exactly one" is per anchored feature, never one in total.
      or the row is unresolved/rejected with a reason
      → this replaces comparing row counts, which no longer match by design
  no themed Signal drops a member's claim, and no clause says more than its note row
  every question/concern/conflict row has a mirror in ## Open Questions
  every requirement/feedback row with Why: not stated carries exactly one rationale marker,
      and every "rationale: in question" row is a bullet in the ONE batched question
      # an unmarked row is a filing gap, not a blocker — transform passes it through and reports it
  every pain-point row's Notes carries a PP-### (minted in both places, or matched)
  every "derived from #<n>" row was filed with a client question
  status: in-review if every ## Open Questions box is checked, else needs-clarification
```

## Partial fold-ins

```text
some questions answered, others open
→ harvest what was answered: anchor the rows it unblocks, file them, tick those boxes
→ leave the rest parked needs-clarification
→ waiting for every box strands the answered ones behind the slowest question on the page
```
