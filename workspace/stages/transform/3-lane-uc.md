# UC lane — drafting and updating a Use Case

Handles signals routed to **UC** and to **Context** (`3-routing.md` § The lane table). Read
`3-routing.md` § Which UC — new or update first; this guide assumes that lookup has been made.

A `UC-###` is the vault's requirement artifact and its review unit: one user goal, its flow, its
branches, the rules that govern it, and its open questions in one reviewable document. It replaced
the retired per-statement `FR-###`. Why it looks the way it does:
`references/use-case-standard.md` in this skill's plugin directory — not needed for a run.

## Ownership — who may write this file

**Only `primary_feature`'s subagent writes a UC file.** A UC may span features (`features: []`), and
Stage 3 fans out one subagent per feature, so a shared UC has as many potential writers as it has
slugs. That is the same race the shared registers have, and it gets the same answer.

| The UC you need to change… | Do |
| :--- | :--- |
| has `primary_feature:` = the slug you were dispatched for | Write it normally. |
| is owned by **another** slug | **Write nothing.** Report it as a `cross_feature_uc_change` candidate (`3-lane-entity.md` § What a subagent reports has the report shape) and let Stage 4 apply it sequentially. |
| doesn't exist yet, and the goal plainly belongs to another slug's actor | Report it the same way. Never mint a UC on someone else's behalf. |

`primary_feature` is the feature whose actor holds the goal. It is a write-ownership fact, not a
claim that the other features matter less — every participating hub gets the same `## Use Cases`
pointer in Stage 4.

## Granularity — one UC per user goal

Cockburn's levels, and the reason `level:` is a frontmatter field rather than a private judgement:

| `level` | What it is | Use it when |
| :--- | :--- | :--- |
| `user-goal` | Real work, one sitting, passes the *boss test*. 3–9 main-flow steps. | **The default.** Nearly every UC. |
| `summary` | Several user goals composed into a business process. | Only to group UCs that already exist. Never as the first UC on a feature. |
| `subfunction` | A step sequence several UCs share, written once. | Only when two existing UCs would otherwise repeat it verbatim. |

Two failure shapes to watch, both cheap to fix now and expensive later:

- **A flow past ~12 steps** is a summary-level UC wearing a user-goal label. Raise a question
  proposing the split; do not split it unilaterally — where the seam falls is a business call.
- **A "UC" that is one validation** ("Validate a tax ID") is a step inside someone else's goal, or a
  `BR-###`. Route it there instead of minting a UC nobody would sit down to perform.

## Creating a new UC

Only when no existing UC covers this goal. Instantiate `{template_uc}` as
`{uc_dir}/UC-<NNN> <Title>.md`, id from a `Grep` scan of `{uc_dir}` for the highest existing number
(its own independent sequence; use the `Grep` tool, never a Bash `grep`/`awk` pipeline —
`conventions.md` § ID scheme explains why a denied pipeline silently reuses an id).

| Field | Value |
| :--- | :--- |
| `id` / `title` | `UC-<NNN>` and the goal as a **short active verb phrase** — "Enrol a student", never "Enrolment" or "Student enrolment screen". Same title as the filename |
| `status` | `draft`, always. Stage 5 may move it to `needs-clarification`; nothing here writes anything else |
| `version` | `1.0` |
| `level` | `user-goal` unless § Granularity says otherwise |
| `scope` | The system under design, black-box — usually the product name |
| `primary_feature` | The slug you were dispatched for |
| `features` | `[<primary_feature>]`, plus any other slug a stated step lands in |
| `sources` | The `INT-###` this signal traces to |
| `attachments` | Every path from the source INT note's own `attachments:` — copied, not summarized |
| `owner` / `updated` | `team`, today |

Leave `links:`, `brs:`, `entities:`, `pain_points:`, `absorbs:` empty unless this run fills them.
Leave the `> [!summary]-` block blank — `/enrich-feature` writes it.

Then add the id to the hub's `uc:` frontmatter list and a pointer row to its `## Use Cases` section.

**Never write into `## 1`–`## 6` on creation.** A new UC is created with its numbered sections empty
and its first content staged in `## Discussion`, like every later change. The gate applies to the
first step as much as the hundredth — a UC whose initial content bypassed review is indistinguishable
afterwards from one that passed it.

## Adopting an existing FR

A feature migrated from the pre-UC model has `FR-###` files and no UC. The first signal that touches
such a feature adopts them rather than starting from nothing:

1. Create the UC as above, with `absorbs: [FR-###, …]` listing every FR on this feature.
2. Stage the FR's existing `## Functional requirements` lines into the UC's `## Discussion` as
   proposed steps — `- **FR-### adoption** (staged <date>): FR-012.3 "<line>" → proposed: new step
   after S<n>: <actor action> | <system response>`. They pass the gate like any other content; an
   already-approved FR line is not exempt, because turning a statement into a positioned flow step
   is a real interpretation a human should confirm.
3. Set each adopted FR's frontmatter `absorbed_by: UC-###` and append a `## Changelog` line saying
   so. **Change nothing else about it** — do not edit its body, do not set `removed` (human-gated,
   hard rule 4). It is frozen history from here on, and its id keeps resolving.
4. Point every `BR-###` whose `fr:` cites an adopted FR at the UC as well, by adding the UC id to its
   `uc:` list. Leave `fr:` in place — it is the traceability record of what the rule constrained.

Report the adoption explicitly; it is the one case where one signal produces a large diff.

## Staging a change — new or update, same procedure

Append one entry per pending signal to `## Discussion`, naming its destination so Stage 1 can fold it
in without re-deriving anything:

```
- **<INT-###>** (staged <YYYY-MM-DD>): <the signal, tightly paraphrased or quoted> → proposed:
  <destination>: <the exact final text>
```

| Destination phrasing | For |
| :--- | :--- |
| `new step after S4:` | A step added mid-flow — Stage 1 mints the next unused `S#` and places the row after `S4` |
| `S6 becomes:` | A step's wording or validation changes |
| `S6 is removed because <reason>` | A step that no longer applies — the row keeps its id, marked removed |
| `new flow E2:` / `A1 becomes:` | An exception or alternative path |
| `§ 1 Trigger becomes:` | Any `## 1` metadata line |
| `§ 4: add BR-014, enforced at S5` | The rule mirror — the `BR-###` file itself is the BR lane's job |
| `§ 6: <text>` | A special requirement / NFR scoped to this workflow |

Rules that keep a staged entry foldable:

- **Final text, not an instruction.** "add a rule about approvals" cannot be folded by a later run.
- **One entry per signal**, even when three signals produce three adjacent steps. Signals resolve at
  different times and a merged entry cannot be half-folded.
- **Cite the `INT-###`** — Stage 1's dedup-check reads it out of `## Changelog` to recognize a
  completed apply.
- **Copy the note's `attachments:`** onto the UC's own if not already listed.
- Flip the Signal Log row to `Status: staged`, `Destination: UC-###` (add the target when it is
  specific and already exists — `UC-012 S6`).

## Writing a step

The craft rules that make a flow reviewable. Every one of these is a real drift a drafted flow shows:

- **One step, one action** by one actor — an interaction, a validation, or a state change.
- **Actor intent, never UI gesture.** "Parent provides the student's details", not "Parent types into
  the name field and clicks Next". Gestures are design decisions, and they belong to
  `/prototype-design`, which is downstream of this document and free to choose differently.
- **The System column is not optional.** What is validated, what is recorded, what the actor sees
  next. Most missing validation in a flow is missing because nobody wrote it opposite the action.
- **Never invent a validation, a field, a threshold, or a notification** the source didn't state. A
  plausible-looking system response is the single easiest way to launder a guess into approved scope.
  Missing → a question, or write the step with the gap named.
- **Step ids are permanent.** Assign in mint order, never reuse, renumber, or delete. Row order is
  flow order, so non-sequential ids in the table are expected and correct.

A step whose System column would have to say "depends" is two steps or a branch — put the branch in
`## 3`.

## Writing an alternative or exception flow

- `A#` for a different route to a valid outcome, `E#` for a failure the system must handle. Numbered
  per UC in mint order, permanently.
- **Branch point is an `S#` id**, never a position ("at the third step").
- **Condition is a detected fact**, never a question: "The uploaded roster is missing a required
  column:" not "Is the roster valid?" A question has no truth value, so nobody can tell when the
  branch applies.
- **Every flow ends** — rejoins the main flow at an `S#`, reaches a different success, or fails. A
  flow with no ending is unfinished, and an `E#` that fails must be consistent with `## 1`'s failure
  post-condition. If it isn't, that inconsistency is the question worth raising.
- **Only stated branches.** An invented failure path is scope the client never asked for, and it
  reaches a prototype looking exactly like a real one.

## The `## 4` mirror

`## 4` is a read-only mirror of `{br_dir}` (BABOK: rules are captured separately so a rule change
doesn't force a use-case change). This lane never writes a rule statement here — the BR lane
(`3-lane-br.md`) owns the file, and this table is refreshed from it.

What this lane does write is the **enforcement point**: which `S#` the rule bites at, because that is
a fact about the rule *in this workflow* and exists nowhere else. `pre-condition` / `post-condition`
are valid values when the rule constrains state rather than a step.

A rule the UC lists but no step enforces is either a missing step or a misfiled rule. Raise it as a
question — never leave the cell blank and never invent the step that would justify it.

## The Context sub-lane

Two destinations, neither gated — they add provenance, not requirement content:

**`## 1` Business Need / Goal** — the client's stated why, in the client's own terms. Write only what
was said. A `decision`-type signal has no `Why` by design
(`_bigin/stages/extract/2-extraction.md` § The `Why` field); inventing one for it launders a guess
into the record.

**`pain_points:` frontmatter** — add the `PP-###` id. Ids only: the statement lives in
`{pain_points_file}` and is already mirrored on the hub, and a third copy here would be a third thing
to keep in sync. Never mint a `PP-###` here — a pain point with no register row is an extraction gap
to report, not one to fill silently.

## Questions, and moving one to the decision log

Raise a question on `## 5` **only when a decision is genuinely needed** — the wording is ambiguous
enough that two readers would build different things, or the signal conflicts with existing content.
A clean, unambiguous statement gets staged, not questioned; manufacturing a question adds a human
round-trip to something that needed none.

```
- [ ] Q: <one concrete question, self-contained> (owner: client|team) (ref: <INT-###>)
      A:
```

- **Self-contained** — readable by someone who has not seen the signal, the hub, or this run.
- **Plain business language for `owner: client`** — no `signal`, `slug`, `UC`, `staged`, or any other
  vault vocabulary. `owner: team` may use ids, always paired with what they say.
- **One question per line**; three or more options get `(a)/(b)/(c)`.
- **One question, two places is a bug.** If the source INT note already asks this, Gate 1 in
  `2-qualification.md` should have parked the signal `held` before it reached this lane.

When a question resolves, Stage 1 folds in the answer and **moves the line into the decision log
table** — topic, who raised it and what they said, what was decided, the date. The checkbox list
holds only what is still open, which is what keeps the status invariant countable.

## Conflict with existing content

Two statements that cannot both hold. Never pick a winner — recency settles a supersession
(`2-qualification.md` § 4c); it does not settle a disagreement between two people's requirements.

1. Flip the new Signal Log row to `Status: conflict`, `Notes: conflicts with #<n>`.
2. Raise one question on the UC naming **both** sides in plain language, and the `S#`/flow each
   affects, so the reader can decide without opening the hub.
3. **Stage nothing for this signal** — a conflicting proposal in `## Discussion` becomes foldable the
   moment the box is ticked, regardless of which side the answer picked.

## What this lane never does

- Write into `## 1`–`## 6` directly. That is Stage 1's fold-in, after the gate.
- Write a UC owned by another `primary_feature` (§ Ownership), or touch another feature's hub.
- Write a rule statement into `## 4`, or any `BR-###` file content beyond adding this UC to its `uc:`
  list.
- Renumber, reuse, or delete an `S#`, an `A#`, or an `E#`.
- Write `status: approved`, `removed`, `enriched`, or `consolidated` — approval and removal are
  human-gated (hard rule 4); the other two belong to their own skills.
- Write `## Domain Concerns` or the summary block — `/enrich-feature` owns both.
- Edit an `FR-###`'s body, or set it `removed`. An absorbed FR is frozen history (§ Adopting an
  existing FR).
