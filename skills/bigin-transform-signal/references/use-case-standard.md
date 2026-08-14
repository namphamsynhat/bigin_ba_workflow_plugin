# The Use Case artifact — where its shape comes from

Why `UC-###` looks the way it does, and which parts are established practice versus a deliberate
departure for this vault. Read this when changing the UC template or a lane guide — not during a
normal run. The runtime rules live in `_bigin/stages/transform/3-lane-uc.md` and
`_bigin/templates/use-case.md`; this file is the reasoning behind them, so a later change doesn't
quietly undo a decision that was made for a reason.

## The problem this artifact solves

The pre-UC pipeline emitted one `FR-###` per testable statement. That is faithful to the signal and
almost unreviewable: a client reads "the system must capture the vendor's tax ID" and has no way to
tell whether the flow they actually care about works end to end. Approval was being asked for on
fragments, one at a time, with the workflow that connects them living nowhere.

A use case is the standard answer. Use-Case 2.0 states it directly — a use case is *"the context for
a set of related requirements,"* and *"the set of all use cases gives us all the functional
requirements of the system."* The requirements didn't go anywhere; they acquired the context that
makes them reviewable. This is also why the human gate moved onto the UC: the reviewable unit and the
approvable unit should be the same document.

## What the sources actually prescribe

### Cockburn's template (the section list)

`UC-###`'s section order is Cockburn's, adapted. His template (HaT TR96.03a) is: name as a **short
active verb phrase that is the goal**, goal in context, scope, level, preconditions, success end
condition, failed end condition, primary actor, trigger, main success scenario, extensions,
sub-variations, related information (priority, performance target, frequency, superordinate and
subordinate use cases, secondary actors, channels), **open issues**, schedule.

Two things in that list matter more than they look:

- **`OPEN ISSUES` is a first-class section of the original template**, not an invention of this
  vault. Questions belonging to the use case, not to a fragment of it, is the 1998 design.
- **Cockburn explicitly prescribes filling the template in several passes** across the project, and
  names the sequence: identity + actor + level first; trigger and main success scenario next;
  extensions and sub-variations once scope is being checked; open issues and estimates later. A UC
  that is partially filled is not a defective UC — it is a UC at pass 2. This is the direct
  precedent for a UC that gets updated as signals keep arriving.

### Cockburn's step-writing rules

These are the craft rules that make a flow readable, and the ones an agent drifts from first:

- One step is one interaction, one validation, or one state change — and it names its actor.
- **Write actor intent, not UI gesture.** "Parent provides the student's details," never "Parent
  types into the name field and clicks Next." A flow written in gestures is a design decision
  smuggled into a requirement, and it breaks the moment the prototype changes.
- **3–9 steps** at user-goal level. Past that the use case is at summary level and wants splitting.
- **Extensions key to the step they branch from** (`3a`, `3b` for two conditions detected at step 3).
- **State an extension's condition as a detected fact, not a question.** "Card is invalid:" not "Is
  the card valid?" A question has no truth value, so nobody can tell when the branch applies.
- Every extension ends one of three ways: rejoins the main flow, reaches a different success, or
  fails.

### Goal levels — why `level:` exists

Cockburn's levels are Summary, **User goal** ("primary task", his "sea level"), and Subfunction. The
user-goal level passes the *boss test*: it is work your boss would accept as a day's real work, done
in one sitting. Getting this wrong is the most common way a use-case set rots — a mix of "Run the
grant program" and "Validate a tax ID" in one register makes the register unusable, because neither
one is the size a human reviews or a team builds.

`level:` is on the frontmatter so the mistake is visible instead of implicit. Default `user-goal`;
anything else wants a reason.

### BABOK — business rules stay out of the flow

BABOK's *Use Cases and Scenarios* technique is explicit that business rules are captured
**separately**, so that a rule change does not force a change to the use case. Ron Ross's business
rules work (in BABOK's own bibliography) is the same argument from the rules side: a rule is an
independent thing the business owns, not a clause inside one process description.

This is why `## 4` in the template is a **mirror table, not the source**. `BR-###` keeps its own file
under `_brs/`, cites the UCs it governs in `uc: []`, and one rule can constrain three UCs without any
of them owning it. The alternative — UC-scoped rule ids written inline — was considered and rejected:
a rule shared by two workflows gets written twice and drifts, and the drift is invisible because
each copy looks authoritative in its own document.

The mirror carries one thing the BR file cannot: **the enforcement point** — which step of this
flow the rule bites at. That is a fact about the rule *in this workflow*, so it belongs here.

### Use-Case 2.0 — flows, and what a slice is for

Jacobson, Spence and Bittner's Use-Case 2.0 supplies three things this vault uses:

1. **Narrative structure**: a basic flow plus alternative flows, where the network of flows is a map
   of every story the use case contains. This is the same shape as Cockburn's main scenario plus
   extensions, and the two are treated as one convention here.
2. **Progressive detail** — *"the first level defines the bare essentials"*, and a narrative can
   legitimately be a bulleted outline before it is a table. Combined with Cockburn's several-passes
   guidance, this is the licence for `## 2` to start as an outline and grow.
3. **Slices** — *"one or more stories selected from a use case to form a work item that is of clear
   value to the customer."* A slice is the delivery unit, and it is what `EP-###`/`US-###` should be
   cut from downstream: basic flow first, then the alternative and exception flows. This is guidance
   for `/consolidate-prd` when it migrates; this skill does not slice anything.

UC 2.0 also keeps *special requirements that apply to the whole use case and are often
non-functional* attached to the use case. This vault has no NFR artifact at all, so `## 6` is where
"must complete in under three seconds" lands instead of being dropped.

### Wiegers — and why retiring `FR-###` is still safe

Karl Wiegers' position is that use cases alone often lack the detail a developer needs, so software
functional requirements get **derived** from them. Taken literally that argues for keeping `FR-###`
alongside the UC.

The reason this vault doesn't: the derived-detail role is already played by artifacts further down
the chain — the PRD section, then `EP-###`/`US-###`. Keeping `FR-###` as well would mean every signal
is written twice at the same stage of the pipeline, and the human reviews two documents that must
agree. What Wiegers is actually protecting is *addressability*: something specific for a story, a
test, or a defect to cite. That is preserved by giving every flow step a permanent id
(`UC-012 S4`), which is what the next section is about. If a step ever genuinely needs more depth
than a flow row can hold, the honest answer is a `BR-###` (if it's a rule) or a note in `## 6` — not
a resurrected parallel FR.

## Deliberate departures from the sources

Three, each with a reason. Anything else in the template that differs from Cockburn is an error, not
a decision.

### 1. Steps carry permanent `S#` ids, displayed in flow order

Cockburn numbers steps positionally (1, 2, 3), which is right for a document a human retypes and
wrong for one that machines cite. In this vault, a step number is cited from at least four places:
an extension's branch point, the `## 4` mirror's enforcement point, a Signal Log row's
`Destination`, and (later) a story or a prototype screen. Positional numbering means inserting a
step between 4 and 5 silently invalidates every one of those citations.

This is not hypothetical — it is a failure the vault already documents for the retired `SCN-###`
register, where a step inserted mid-flow left `(step 2 of 4)` stale on every participating hub with
nothing to reconcile it.

So: **an `S#` is assigned in mint order and never reused, renumbered, or deleted; row order is the
flow order.** A step inserted between `S4` and `S5` is `S10`, sitting in the third row. A reader sees
non-sequential ids, which is the visible cost, and gets history for free — the same append-only
discipline the Signal Log already teaches. A removed step keeps its id with the removal noted, so a
citation resolves to "removed at v1.4, because…" instead of to nothing.

### 2. Two-column steps (Actor Action | System Response & Validation)

Cockburn writes one column and alternates actor per step. The two-column form pairs them, which
costs a little redundancy and buys the question a single column lets a drafter skip: *and what does
the system do about it?* Most missing validation in a drafted flow is missing because nobody was
forced to write it down opposite the action. Both columns still follow the intent-not-gesture rule.

### 3. Open questions stay as checkboxes; the decision log is separate

The draft format that started this work had open items as an `OPEN-01` table. This vault has a
load-bearing invariant — zero unchecked `- [ ] Q:` lines ⟺ status is not `needs-clarification` —
that `/extract-signal`, `/enrich-feature`, and this skill all enforce by counting checkboxes. A
second question format would either break that count or duplicate every question into two places,
which `conventions.md` § One question, two places exists to prevent.

So `## 5` holds both, doing different jobs: the canonical `- [ ] Q:` list for anything **still open**
(this is what the invariant counts), and a **decision log** table for items already **settled** —
what was asked, who said what, what was decided, when. The speaker context the draft format wanted
is real value; it just belongs on the resolved record rather than in a parallel question queue.

## The consequence that isn't obvious: a UC can span features, so who may write it?

A `UC-###` carries `features: []` and may legitimately span three slugs — that is the point of
moving up from per-feature fragments. But Stage 3 fans out **one subagent per feature**, so a UC
shared by three features has three concurrent writers, which is the same race the vault already
solved for its shared registers.

Hence `primary_feature:`. Exactly one feature owns the UC — the one whose actor holds the goal — and
**only that feature's subagent writes the file**. A signal anchored to a participating feature that
needs to change a UC owned by another feature is *reported* to the orchestrator and applied
sequentially in Stage 4, exactly like an entity promotion. This keeps per-feature parallelism intact
and keeps the write path single-owner.

The corollary: `primary_feature` is a *write-ownership* fact, not a claim that the other features
matter less. Every participating hub gets the same pointer in its `## Use Cases` section.

## What the UC replaced, and what it didn't

| Artifact | Fate |
|---|---|
| `FR-###` | **Retired.** Existing files stay on disk, frozen, carrying `absorbed_by: UC-###`. Flow steps carry the testable detail. |
| `BR-###` | **Kept, unchanged in kind** — its own file, now citing `uc: []`. Mirrored read-only in `## 4`. |
| `SCN-###` | **Retired.** A cross-feature UC is a business scenario that also carries actors, flows, rules, and a gate — strictly more than a register row. Existing rows stay, marked superseded by the UC that absorbed them. |
| `EN-###` | Unchanged. A UC references entities; it does not model them. |
| `PP-###` | Unchanged in the register and on the hub. The UC cites ids in `## 1` rather than carrying a fourth mirror of the same table. |
| Design directives | Unchanged. Presentation-only signals still bypass the UC entirely (`3-lane-design.md`). |

## Sources

- [Cockburn, *Basic Use Case Template*, HaT TR96.03a (1998)](https://www.cs.helsinki.fi/u/mluukkai/ohmas09/usecase.pdf) — the section list, the `OPEN ISSUES` section, and the several-passes staging guidance.
- [Cockburn, *Writing Effective Use Cases* (book draft)](https://kurzy.kpi.fei.tuke.sk/zsi/resources/CockburnBookDraft.pdf) — goal levels, scope, stakeholders and interests.
- [A guide to Cockburn use cases](http://www.binaryphile.com/software-engineering/requirements/use-cases/2026/05/10/cockburn-use-cases-guide.html) — the step-writing and extension-condition rules, restated compactly.
- [IIBA BABOK Guide § 10.47, *Use Cases and Scenarios*](https://www.iiba.org/knowledgehub/business-analysis-body-of-knowledge-babok-guide/10-techniques/10-47-use-cases-and-scenarios/) — business rules captured separately from the use case.
- [BABOK technique summary — Scenarios and Use Cases](https://babokpage.wordpress.com/techniques/scenarios-and-use-cases/) — element list, strengths and limitations.
- [Jacobson, Spence, Bittner, *Use-Case 2.0* (ACM Queue / Ivar Jacobson International)](https://www.ivarjacobson.com/files/use-case_2.0_the_hub.pdf) — narrative structure, progressive levels of detail, slices, special requirements.
- [Wiegers, *The Use Case Technique: An Overview*](http://media.modernanalyst.com/The-Use-Case-Technique-An-Overview-Karl-Weigers-July-2012.pdf) — functional requirements derived from use cases; classifying an input as task, rule, or constraint.
- [Requirements Engineering Magazine, *Functional Requirements and their levels of granularity*](https://re-magazine.ireb.org/articles/functional-requirements-and-their-levels-of-granularity) — granularity levels and decomposition.
