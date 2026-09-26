# UC lane — what a UC change set must contain

```text
in:   signals routed to UC and to Context (from the route worklist)
out:  change sets (schema `changeset`) targeting UC-### — `bigin apply` writes them
never: editing a UC file · renumbering an S#/A#/E# · minting an id · a rule statement in ## 4
```

Read `3-routing.md` § Which UC — new or update first; this guide assumes that lookup is made.

A `UC-###` is the vault's requirement artifact and its review unit: one user goal, its flow, its
branches, the rules governing it, and its open questions in one reviewable document. Why it looks this
way: `references/use-case-standard.md`.

## Ownership — who may write this file

Nobody but the engine writes a UC. A change set may target any UC, including one another feature owns
(a cross-feature step): the engine applies sets one artifact at a time, refuses a write whose file changed
underneath it, and records every applied set's id in the Changelog, so a re-run is a no-op. Trace the set
to **your** hub row (`trace.hub` = your slug); `bigin hub refresh` points every participating hub.

`primary_feature` is the feature whose actor holds the goal — the owner hub, not a claim that the other
features matter less. When a cross-feature flow reveals that a participating feature contributes a step
nobody described, that is a question for that feature's hub — never a step invented from the narration.

## Granularity — one UC per user goal

| `level` | What it is | Use when |
| :--- | :--- | :--- |
| `user-goal` | real work, one sitting, passes the *boss test*. 3–9 main-flow steps | **the default** — nearly every UC |
| `summary` | several user goals composed into a business process | only to group UCs that already exist. Never the first UC on a feature |
| `subfunction` | a step sequence several UCs share, written once | only when two existing UCs would repeat it verbatim |

- **A flow past ~12 steps** is a summary-level UC wearing a user-goal label. Raise a question proposing
  the split; never split unilaterally — where the seam falls is a business call.
- **A "UC" that is one validation** ("Validate a tax ID") is a step inside someone else's goal, or a
  `BR-###`. Route it there rather than minting a UC nobody would sit down to perform.

### Recognizing drift — the smell that matters more than step count

A UC does not need to cross ~12 steps to have outgrown one user goal. Runs that each add "just one more
step" for an *adjacent* goal (a different actor, a different trigger) quietly accumulate two or three
workflows under one id. The leading indicator: **do every `S#`/`A#`/`E#` on this UC still share one
primary actor and one trigger?** Check it every time a new step is about to be added.

**Raising it**: an `add_question` on the UC proposing a concrete boundary — which ids move to which new
(or existing) UC, a suggested title and primary actor for each, which `BR-###` each carries. Never split
unilaterally, and don't keep drafting steps for the drifted-off goal meanwhile: gate those change sets on
the split question.

**Executing it** is `/restructure-uc`'s job (the `uc-splitter` agent emits a split plan as change sets —
`drop_step` on the source, `create_uc`/`new_step_after`/`new_flow` on the targets — and the engine applies
it, repoints BR `uc:` via `bigin links sync`, and refreshes every hub). Never from this lane.

## Creating a new UC

Only when no existing UC covers this goal. Phase A records it as a `new` entry (`key`, `title` — the goal
as a **short active verb phrase**, "Enrol a student", never "Enrolment" — `goal`, `actor`,
`primary_feature`, `features`, `level`, `sources`). `bigin mint route` mints the id under the id lock,
instantiates the lean skeleton (`{template_uc}`: status `draft`, version `1.0`, one guide comment, § 2
placeholder row, § 3 empty), points every hub in `features:`, and updates `{requirements_file}`'s UC column.
Phase B then fills it with change sets targeting the minted id (or `new:<key>`).

A new UC's first content arrives through change sets like every later change — the first
`new_step_after` fills the placeholder `S1`. Leave `links:`, `entities:`, `absorbs:` alone unless a change
set says otherwise; `attachments:` are the source notes' own, copied via a `link` set on `attachments`.

## Adopting an existing FR

A feature migrated from the pre-UC model has `FR-###` files and no UC. The first signal touching it adopts
them: a `new` UC whose change sets carry each FR's functional lines as `new_step_after` sets (trace: the
FR id in `trace.evidence`), plus a `link` set on `absorbs`. Turning a statement into a positioned step is a
real interpretation, so an already-approved FR line is not exempt from review. The FR itself is frozen: its
`absorbed_by:` and one Changelog line are the only edits, made by the orchestrator; a BR whose `fr:` cites an
adopted FR gets the UC through a `link` set on `uc`. Report the adoption explicitly.

## Writing the change set — new or update, same procedure

| Intent | `op` | Must carry |
| :--- | :--- | :--- |
| add a step mid-flow | `new_step_after` | `anchor.ref` (S#, `start`, `end`) + `anchor.sha` from the worklist · `cells` {actor, system} — the engine mints the next unused `S#` |
| change a step | `replace_step` | `anchor` {ref, sha} · `cells` |
| a step no longer applies | `drop_step` | `anchor` · `reason` → `Dropped — <reason>`, id kept |
| add / change / drop a flow | `new_flow` · `replace_flow` · `drop_flow` | `flow` {kind A\|E, name, body} · `anchor` for replace/drop · `reason` for drop |
| any `## 1` line (trigger, actors, pre/post-conditions, Business Need) | `set_field` (replace) · `append_note` (add) | `target.section: "1"`, `target.field`, `text`; `anchor.sha` of the current value when replacing |
| a special requirement | `append_note` | `target.section: "6"`, `text` |
| link a rule | `mirror_br` | `br`, `enforced_at` (§ The `## 4` mirror) |
| a question | `add_question` | `text`, `owner`; the engine appends `(ref: …)` from `trace` |

- **Final text, not an instruction.** "add a rule about approvals" cannot be applied.
- **One change set per intended edit**, even for three adjacent steps from three signals — each carries its
  own trace and lands (or waits) on its own.
- **`trace` is mandatory:** `int`, `note_rows`, `hub`, `hub_rows` (the row's Source cell), `xr` in codebase mode.
  It becomes the Changelog line that proves where the content came from.
- **Gate only what needs a decision:** `gate: {question, owner, blocks: true}` on the set that depends on
  it. A clean, unambiguous statement lands ungated; § 2 changes are flagged for `/approve-uc` review by the
  engine either way.
- **Carry a missing rationale.** When the note row has `Why: not stated`, end the text of the
  most relevant set (or its question) with `— rationale not stated at capture`; never re-derive a `Why`.

## Writing a step

- **One step, one action** by one actor — an interaction, a validation, or a state change.
- **Actor intent, never UI gesture.** "Parent provides the student's details", not "Parent types into
  the name field and clicks Next". Gestures belong to `/bigin-generate-design`, which is downstream and free
  to choose differently.
- **The System column is not optional** — what is validated, what is recorded, what the actor sees
  next. Most missing validation in a flow is missing because nobody wrote it opposite the action.
- **Never invent a validation, field, threshold, or notification** the source didn't state. A
  plausible-looking system response is the single easiest way to launder a guess into approved scope.
  Missing → a question, or write the step with the gap named.
- **Step ids are permanent.** Assign in mint order; never reuse, renumber, or delete. Row order is flow
  order, so non-sequential ids are expected and correct.

A step whose System column would have to say "depends" is two steps or a branch — put the branch in
`## 3`.

## Writing an alternative or exception flow

- `A#` = a different route to a valid outcome · `E#` = a failure the system must handle. Numbered per
  UC in mint order, permanently.
- **Branch point is an `S#` id**, never a position ("at the third step").
- **Condition is a detected fact, never a question:** "The uploaded roster is missing a required
  column:" not "Is the roster valid?" A question has no truth value, so nobody can tell when the branch
  applies.
- **Every flow ends** — rejoins the main flow at an `S#`, reaches a different success, or fails. An
  `E#` that fails must be consistent with `## 1`'s failure post-condition; if it isn't, that
  inconsistency is the question worth raising.
- **Only stated branches.** An invented failure path is scope the client never asked for, and it
  reaches a prototype looking exactly like a real one.

## The `## 4` mirror

`## 4` is a **read-only mirror** of `{br_dir}`: `mirror_br` copies the BR's current statement itself, so
the router never writes rule text into a UC. What the set supplies is the **enforcement point** —
`enforced_at`: the `S#`/`A#`/`E#` the rule bites at in THIS workflow, or `pre-condition` /
`post-condition` when it constrains state. The engine rejects an enforcement point that does not exist
or names a dropped step.

A rule this UC should list but no step enforces is either a missing step or a misfiled rule → an
`add_question`. Never leave the point vague, and never invent the step that would justify it.

## The Context sub-lane

```text
## 1 Business Need / Goal → a `set_field` set, target.section "1", field "Business Need / Goal"
    the client's stated why, IN THE CLIENT'S OWN TERMS, only what was said
    a `decision`-type signal has no Why by design — inventing one launders a guess into the record
pain_points: frontmatter  → a `link` set, field `pain_points`, ids only — the statement lives in
    {pain_points_file} and on the hub. NEVER mint a PP-### here: a pain point with no register row is an
    extraction gap to report
```

## Questions, and moving one to the decision log

Raise one **only when a decision is genuinely needed** — the wording is ambiguous enough that two readers
would build different things, or the signal conflicts with existing content.

- **Self-contained** — readable by someone who has not seen the signal, the hub, or this run.
- **Plain business language for `owner: client`** — no `signal`, `slug`, `UC`, `staged`, or other vault
  vocabulary. `owner: team` may use ids, always paired with what they say.
- **One question per line**; three or more options get `(a)/(b)/(c)`.
- **One question, two places is a bug.** If the source INT note already asks this, Gate 1 should have
  parked the signal `held`.

When the answer arrives, the engine moves the line into the Decision log (`ledger release` for a gate
question; an `answer_question` set for any other) — the Still-open list holds only what is open, which is
what keeps the status invariant countable.

## Conflict with existing content

Two statements that cannot both hold. **Never pick a winner** — recency settles a supersession; it does
not settle a disagreement between two people's requirements.

```text
1  BEFORE writing the question: re-read the existing content's own cited INT-### source past its cited
   line. Existing content is a prior run's *reading* of that source; a prior extraction can have resolved
   a contested exchange into one confident sentence.
     source itself was contested → word the question as a three-(or-more)-way choice naming every framing
     source was clear            → word it as the two-sided conflict
   Report which case this was.
2  emit ONE `add_question` on the UC naming every side in plain language and the S#/flow each affects —
   traced to the INT only (no hub_rows, so the engine does not mark the row applied)
3  list the row under `unrouted` with reason "conflict with #<n>"; the orchestrator runs
   `bigin hub flip <slug> <row>=conflict@conflicts with #<n>`
4  emit NO content change set for this signal
```

**A `conflict` row is parked, not finished.** Stage 1 re-enters it once its question carries a filled
`A:` (`1-foldin.md` § Re-entry), and this lane drafts it **from the decision**. The same applies to a
`question` row raised on the hub.

## What this lane never does

- Edit a UC, BR, or hub file — change sets only, applied by `bigin apply`.
- Write a rule statement into `## 4`, or BR content beyond what the BR lane's sets carry.
- Renumber, reuse, or delete an `S#`, `A#`, or `E#`.
- Mint an id, or write `status` of any value — `approved`/`removed` are human-gated; `enriched` and
  `consolidated` are unreachable; Stage 5's `bigin status` re-counts the rest.
- Write the retired summary block, or edit an `FR-###`'s body.
