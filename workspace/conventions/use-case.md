# Conventions — the Use Case

What a `UC-###` is, what its sections hold, how it traces back to the signal that caused it, and
the summary block that keeps it scannable.

**Read by** `/bigin-transform-signal` and its `uc-router` / `uc-applier` / `uc-splitter` workers,
`/restructure-uc`, `/approve-uc`, and `/bigin-generate-prd` (for § Traceability chain).

## Use Case

`01-Requirements/_ucs/UC-<NNN> <Title>.md` (`type: use-case`, instantiate from
`_bigin/templates/use-case.md`) is **the** requirement artifact and the unit a human reviews and
approves. One use case is one user goal: an actor, a trigger, the flow that delivers the goal, the
branches that can happen instead, the rules that govern it, and the questions still open about it —
in one document.

It replaced `FR-###`, which was one file per testable statement. That was faithful to the signal and
unreviewable: a client reading "the system must capture the vendor's tax ID" cannot tell whether the
workflow they care about holds together. Use-Case 2.0 puts it directly — a use case is *the context
for a set of related requirements*, and the set of all use cases is the system's functional
requirements. The requirements didn't go anywhere; they acquired the context that makes them
approvable.

**Structure** (the numbered sections are the reviewable document; the rest is machinery):

| Section | Holds |
|---|---|
| `## 1. Context & Metadata` | Primary/secondary actors, business need, trigger, pre-conditions, success **and failure** post-conditions |
| `## 2. Main Success Scenario` | The happy path as a step table: `Step` (an `S#` id) · `Actor Action` · `System Response & Validation` |
| `## 3. Alternative & Exception Flows` | Optional. `A#` alternatives and `E#` exceptions, each with a branch-point `S#`, a condition stated as a detected fact, and an ending |
| `## 4. Business Rules & Compliance Constraints` | A **read-only mirror** of `BR-###` files: id, short statement, and the enforcement point (which `S#` the rule bites at) |
| `## 5. Open Questions & Decision Log` | The canonical `- [ ] Q:` list for what is still open, plus a decision-log table of settled items with speaker context |
| `## 6. Special Requirements & Related Information` | Optional. Workflow-scoped non-functional constraints, priority, frequency, performance target |
| `## Discussion` · `## Changelog` | The staging gate and history |

**Goal level.** `level:` is `user-goal` (the default — real work, one sitting, 3–9 main-flow steps,
passing Cockburn's *boss test*), `summary` (several user goals composed, only ever to group UCs that
already exist), or `subfunction` (a step sequence several UCs share, written once). A "use case" that
is a single validation is a step inside someone else's goal, or a `BR-###`.

**Step ids are permanent.** An `S#`/`A#`/`E#` is minted in mint order and never reused, renumbered, or
deleted; **row order is the flow order**, so a step inserted between `S4` and `S5` gets the next unused
id and sits in the third row. Non-sequential ids are correct. Positional numbering was rejected because
a step number is cited from at least four places — an extension's branch point, a rule's enforcement
point, a Signal Log `Destination`, and later a story or prototype screen — and renumbering would
invalidate all of them silently. That is the same failure the retired `SCN-###` register had with
`(step N of M)`. A removed step keeps its row and id, marked removed with the reason, so every citation
still resolves.

**A use case may span features.** `features: []` lists every slug it touches, and `primary_feature:`
names the one that **owns the file** — the feature whose actor holds the goal. Ownership is a
write-ownership fact, not importance: only that feature's `/bigin-transform-signal` subagent writes the
file, because Stage 3 fans out per feature and a shared UC would otherwise have concurrent writers. A
change reported from a participating feature is applied by the orchestrator in Stage 4
(`_bigin/stages/transform/3-lane-uc.md` § Ownership). Every participating hub carries the same
`## Use Cases` pointer.

**A feature may carry several use cases** — one per genuinely distinct user goal. This is the deliberate
break from the retired one-FR-per-feature norm: four goals means four UCs, and that is not
fragmentation. What a feature must never carry is two use cases for the same goal.

**Rules stay outside.** `## 4` is a mirror; `BR-###` under `01-Requirements/_brs/` is the source, citing
`uc: []`. BABOK's *Use Cases and Scenarios* technique is explicit that rules are captured separately so
a rule change does not force a use-case change — and one rule routinely governs several workflows, so
no single one of them can own it. The one fact the mirror adds is the enforcement point.

**Updated many times, never re-forked.** New signals keep arriving for the life of a feature; each one
edits the UC in place (version bump + `## Changelog`, hard rule 7 — approval doesn't freeze it), staged
through `## Discussion` and folded in after the human gate. A use case filled only as far as pass 2 is
not defective: Cockburn's own template guidance is to fill it in several passes, and Use-Case 2.0 starts
a narrative as a bulleted outline before it becomes a table.

**What it replaced:** `FR-###` (retired, frozen, `absorbed_by:`) and `SCN-###` (retired — a
cross-feature UC is a business scenario that also carries actors, branches, rules, and a review gate).
Unchanged: `BR-###`, `EN-###`, `PP-###`, and design directives, which still bypass the UC entirely.

The reasoning behind each of these choices, with sources, is in this plugin's
`skills/bigin-transform-signal/references/use-case-standard.md` — read it before changing the template,
not during a run.

## Traceability chain

`/bigin-generate-prd` branches on the UC's `primary_feature:`
slug looked up in `01-Requirements/FEATURES.md` — the feature's `Status` there decides which of two
valid chains applies. `/approve-uc` itself doesn't branch on this: it approves the UC regardless of
which chain the feature will take, and stops there (`feature-hub.md` § Feature material):

- **Full** — feature `proposed` / `committed` / `not-built` (new scope):
  `INT → UC/BR → PRD → EP → US → UX`.
- **Lightweight CR** — feature already `built` (a change/fix/improvement on something shipped):
  `INT → UC/BR → US → UX`, skipping PRD and EP. The US cites the UC directly in `sources` instead
  of an EP, and the UC's `links` points at the US id(s) instead of a PRD id.

  A UC spanning several features whose `Status` values disagree takes the chain of its
  `primary_feature` — the feature that owns the goal — and the disagreement is worth naming in the
  report rather than resolving silently per participating feature.

  Cutting the epics and stories is where Use-Case 2.0's **slices** belong: a slice is one or more of a
  UC's flows taken together as a work item of clear value, basic flow first, then the alternative and
  exception flows. `/bigin-transform-signal` never slices anything — this is guidance for
  the epic/story stage (not built — epics and stories are cut by hand from approved UCs), if it is ever built.
- **Design** — a presentation-only signal, at any feature status: `INT → design directive → UX`,
  skipping UC, PRD, EP, and US entirely. A statement about look, layout, tone, copy voice,
  interaction feel, or an accessibility affordance produces **no functional scope**, so there is
  nothing for a PRD section to carry and nothing for a story to decompose. It becomes a directive
  in one of two places — a `DESIGN-PRINCIPLES.md` row when it's durable and cross-cutting, or a row
  in its feature hub's own `## Design Directives` section when it's scoped to one feature — and
  `/bigin-generate-design` reads both directly. The directive carries no id of its own; its
  traceability runs through the originating Signal Log row's `Destination` cell.

  The chain is chosen by a strict test, not by the client's phrasing: **if a tester could write a
  pass/fail assertion for it that never mentions appearance, it is UC or BR, not a design
  directive** — "ask for confirmation before deleting" adds a step to a flow and takes the Full or
  CR chain, however visual the request sounded. An ambiguous signal takes the UC chain, because an
  over-routed step is caught at the human gate while an under-routed directive skips the gate.
  `_bigin/stages/transform/3-lane-design.md` and `_bigin/stages/transform/3-routing.md` hold the
  boundary test and the destination rules.

**Partly live.** The **PRD stage distinguishes the two chains**: `/bigin-generate-prd` reads the
`FEATURES.md` row's `Status` and skips a `built` feature, because the CR chain has no PRD in it —
writing one anyway is how a chain quietly changes. It stamps `chain:` with which one applied. What is
still **Planned** is the CR chain's *destination*: nothing cuts the `US-###` a CR is supposed to land
in, so a CR against a shipped feature today ends at its reviewed UC plus its design, and the story is
cut by hand. The **Design chain is live**: `/bigin-transform-signal` files directives to both
destinations, and `/bigin-generate-design` reads both — `DESIGN-PRINCIPLES.md` and each hub's
`## Design Directives` — plus the UC itself, and writes the `UX-###` the chain ends at. It runs off
`UC-###` directly and needs no PRD, so a design-only feature and a feature whose PRD isn't written
yet both reach `UX` normally. See § Reconciliation notes for the stages still on the old layout.

Every link in the chosen chain must resolve; if one can't be established, add an Open Question
instead of guessing.

The feature slug is the horizontal anchor across the chain: every slug in a UC's `features:` must
exist as a row in `01-Requirements/FEATURES.md`. New intake about a mapped feature updates the
relevant use case **in place, at any status** (hard rule 7, `intake.md` § Feedback handling) — approval doesn't
freeze it, and neither does the feature shipping — never as an unrelated parallel UC for the same goal.

A cross-feature flow is **not** a fork of this chain and no longer an overlay artifact of its own: it
is one `UC-###` listing every participating slug in `features:`, running the chain of its
`primary_feature`. The `SCN-###` register that used to annotate how several per-feature chains
composed is retired (`registers.md` § Business Scenarios (retired)).

## Summary block (use case only — scannability)

Reading a long UC cold means scrolling past open questions, business rules, and prose just to find
out what the note is about. The UC template carries a collapsed summary right after frontmatter,
before `## 1. Context & Metadata`, so a reader gets the gist in one glance without opening the whole
document:

```md
> [!summary]- Summary
> 2-3 sentences here.
```

It's a **synthesis, never new content** — same contract as any diagram/visual aid a skill adds: it
illustrates what the note already states, it doesn't add to it. **Retired in practice**: nothing
writes it any more — it was `/enrich-feature`'s under that skill's old per-UC design, and
enrichment is feature-scoped now and never touches a UC (§ Reconciliation notes). Leave the block
blank, or omit it entirely on a new UC.

**Write it for a client/PO skimming the note, not for an auditor tracing artifact lineage.**
2-3 short sentences, plain business language:

1. **Source + what changed** — where this came from (INT id, or "a change request against
   UC-XXX") and the concrete thing being added/changed, in business terms (a field, a rule, a
   capability) — not "3 new flow steps and BR-104".
2. **Why** — the pain point/business reason, in the client's terms (drawn from `## 1`'s Business
   Need / Goal and the `pain_points:` it cites), not a citation of which section it came from.
3. *(only if it changes how the reader should read the UC)* one short clause on what's still
   open — not a restatement of frontmatter status. Omit entirely if there's nothing unusual to
   flag; `status:` and the Open Questions count already show on the note.

**Avoid:** stacking multiple artifact ids in prose (one incidental `UC-XXX` mention is fine; a chain
of `UC-004 … BR-104 … S7` reads like a diff, not a description). Narrating the
pipeline ("per the extraction step", "pending enrichment") — the reader doesn't need to know which
skill wrote this. Hedge-y meta phrasing ("leaving the conflicting parts to a separate UC-022") —
say what *this* UC does; a sibling UC's scope belongs on that UC, not narrated here.

**Before/after** (same UC, real case):

> ❌ *This UC is a change request against the already-approved UC-004 (vendor management),
> expanding the vendor profile/application field set based on the client's `CFEF CRM Flow.pdf`
> reference document. It exists because that document revealed additional fields (Website,
> Customer Tags, W-9 flag, Marketable flag, notes fields), a defined 4-value Reimbursement
> Restrictions dropdown, and a much richer Organization Experience narrative-question set beyond
> what UC-004 originally captured. It adds 4 flow steps and BR-104 (fixing the
> Reimbursement Restrictions value set) as additive detail only, leaving the conflicting parts of
> the same document to a separate UC-022. It still carries 1 open question — whether the new
> narrative questions replace or supplement UC-004's original educational-value field — and is
> `needs-clarification`, pending further elicitation.*

> ✅ *Adds the vendor profile fields the client's `CFEF CRM Flow.pdf` calls for — Website,
> Customer Tags, W-9 and Marketable flags, notes, a 4-value Reimbursement Restrictions list, and
> richer Organization Experience questions — that UC-004's original vendor form didn't capture.
> Open question: whether the new questions replace or add to the existing educational-value
> field.*

Same content, same traceability (still one `UC-004` mention, still names the source document) —
just business-first instead of artifact-first. If a reader wants the artifact-level trace, that's
what `sources`/`absorbs`/the Changelog are for; the summary's job is "what is this, in plain
terms," not "how does this fit the pipeline."

**Intentionally not on INT** — an intake note is raw capture only; even a purely descriptive
summary is a step toward interpretation this vault deliberately keeps out of `/bigin-intake`. An
INT note's "what is this" question is answered instead by its `## Extracted signals` table once
`/extract-signal` fills it, or by opening the note (they're short — that's the point of raw
capture).

Not currently applied to PRD/Epic/Story/feature-hub either — the feature hub already carries a
one-line description under its `# <Feature Name>` heading for the same purpose. Extend the pattern
to other artifact types only if the same scan-cost problem shows up there.
