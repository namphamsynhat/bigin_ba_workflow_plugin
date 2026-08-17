# UC lane — drafting and updating a Use Case

```text
in:   signals routed to UC and to Context
out:  a new/updated UC-###, its content STAGED into ## Discussion
never: writing into ## 1-## 6 directly · renumbering an S#/A#/E# · a UC another feature owns
```

Read `3-routing.md` § Which UC — new or update first; this guide assumes that lookup is made.

A `UC-###` is the vault's requirement artifact and its review unit: one user goal, its flow, its
branches, the rules governing it, and its open questions in one reviewable document. It replaced the
retired per-statement `FR-###`. Why it looks this way: `references/use-case-standard.md`.

## Ownership — who may write this file

**Only `primary_feature`'s subagent writes a UC file.** A UC may span features, and Stage 3 fans out one
subagent per feature, so a shared UC has as many potential writers as it has slugs.

| The UC you need to change… | Do |
| :--- | :--- |
| has `primary_feature:` = your dispatched slug | write it normally |
| is owned by **another** slug | **write nothing** — report a `cross_feature_uc_change`; Stage 4 applies it sequentially |
| doesn't exist, and the goal belongs to another slug's actor | same. Never mint a UC on someone else's behalf |

`primary_feature` is the feature whose actor holds the goal — a write-ownership fact, not a claim that
the other features matter less. Every participating hub gets the same `## Use Cases` pointer in Stage 4.

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

## Creating a new UC

Only when no existing UC covers this goal. Instantiate `{template_uc}` as
`{uc_dir}/UC-<NNN> <Title>.md`, id from a `Grep` scan of `{uc_dir}` for the highest number (its own
sequence; use the `Grep` **tool**, never a Bash pipeline — a denied pipeline silently reuses an id).

| Field | Value |
| :--- | :--- |
| `id` / `title` | `UC-<NNN>` and the goal as a **short active verb phrase** — "Enrol a student", never "Enrolment" or "Student enrolment screen". Same as the filename |
| `status` | `draft`, always |
| `version` | `1.0` |
| `level` | `user-goal` unless § Granularity says otherwise |
| `scope` | the system under design, black-box — usually the product name |
| `primary_feature` | the slug you were dispatched for |
| `features` | `[<primary_feature>]`, plus any other slug a **stated** step lands in |
| `sources` | the `INT-###` this signal traces to |
| `attachments` | every path from the source note's own `attachments:` — copied, not summarized |
| `owner` / `updated` | `team`, today |

Leave `links:`, `brs:`, `entities:`, `pain_points:`, `absorbs:` empty unless this run fills them. Leave
the `> [!summary]-` block blank — `/enrich-feature` writes it.

Then add the id to the hub's `uc:` list and a pointer row to its `## Use Cases`.

**Never write into `## 1`–`## 6` on creation.** A new UC is created with its numbered sections empty and
its first content staged in `## Discussion`, like every later change. The gate applies to the first step
as much as the hundredth — a UC whose initial content bypassed review is indistinguishable afterwards
from one that passed it.

## Adopting an existing FR

A feature migrated from the pre-UC model has `FR-###` files and no UC. The first signal touching it
adopts them rather than starting from nothing:

```text
1  create the UC as above, with absorbs: [FR-###, …] listing every FR on this feature
2  stage each FR's ## Functional requirements lines into ## Discussion as proposed steps:
     - **FR-### adoption** (staged <date>): FR-012.3 "<line>" → proposed: new step after S<n>:
       <actor action> | <system response>
   → they pass the gate like any other content. An already-approved FR line is NOT exempt:
     turning a statement into a positioned flow step is a real interpretation
3  set each adopted FR's absorbed_by: UC-### and append a ## Changelog line saying so
   → CHANGE NOTHING ELSE. Do not edit its body, do not set `removed` (human-gated).
     It is frozen history from here on, and its id keeps resolving.
4  point every BR-### whose fr: cites an adopted FR at the UC too, by adding the UC id to its uc:
   → leave fr: in place: it is the record of what the rule constrained
```

Report the adoption explicitly — the one case where one signal produces a large diff.

## Staging a change — new or update, same procedure

```text
- **<INT-###>** (staged <YYYY-MM-DD>): <the signal, tightly paraphrased or quoted> → proposed:
  <destination>: <the exact final text>
```

| Destination phrasing | For | Applied by |
| :--- | :--- | :--- |
| `new step after S4:` | a step added mid-flow — mints the next unused `S#`, placed after `S4` | Stage 4 Part 2, same run |
| `S6 becomes:` | a step's wording or validation changes | Stage 4 Part 2, same run |
| `S6 is removed because <reason>` | a step that no longer applies — the row keeps its id, marked removed | Stage 4 Part 2, same run |
| `new flow E2:` / `A1 becomes:` / `A1 is removed because <reason>` | an exception or alternative path, added, changed, or removed | Stage 4 Part 2, same run |
| `§ 1 Trigger becomes:` | any `## 1` metadata line | Stage 1, later run |
| `§ 4: add BR-014, enforced at S5` | the rule mirror — the `BR-###` file itself is the BR lane's job | Stage 1, later run |
| `§ 6: <text>` | a special requirement / NFR scoped to this workflow | Stage 1, later run |

This lane always **stages**, regardless of which column applies it — never write § 2, § 3, or anything
else directly from here. Only the § 2 and § 3 rows fast-track, and only in Stage 4, after this lane's
run finishes — and only § 2 changes trigger Stage 4's review flag (`4-sync.md` Part 2); a § 3-only
change does not.

- **Final text, not an instruction.** "add a rule about approvals" cannot be folded by a later run.
- **One entry per signal**, even when three signals produce three adjacent steps — signals resolve at
  different times and a merged entry cannot be half-folded.
- **Cite the `INT-###`** — whichever stage applies it reads this out of `## Changelog` to recognize a
  completed apply.
- **Copy the note's `attachments:`** onto the UC's own if not already listed.
- Flip the Signal Log row: `Status: staged`, `Destination: UC-###` (`UC-012 S6` when the target is
  specific and already exists).

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

`## 4` is a **read-only mirror** of `{br_dir}`. This lane never writes a rule statement here — the BR
lane owns the file, and this table is refreshed from it.

What this lane *does* write is the **enforcement point**: which `S#` the rule bites at, because that is
a fact about the rule *in this workflow* and exists nowhere else. `pre-condition` / `post-condition`
are valid when the rule constrains state rather than a step.

A rule the UC lists but no step enforces is either a missing step or a misfiled rule → **raise a
question.** Never leave the cell blank, and never invent the step that would justify it.

## The Context sub-lane

Two destinations, neither gated — they add provenance, not requirement content.

```text
## 1 Business Need / Goal → the client's stated why, IN THE CLIENT'S OWN TERMS, only what was said
    a `decision`-type signal has no Why by design — inventing one launders a guess into the record

pain_points: frontmatter  → the PP-### id. IDS ONLY: the statement lives in {pain_points_file} and is
    already mirrored on the hub; a third copy is a third thing to keep in sync
    NEVER mint a PP-### here — a pain point with no register row is an extraction gap to REPORT
```

## Questions, and moving one to the decision log

Raise on `## 5` **only when a decision is genuinely needed** — the wording is ambiguous enough that two
readers would build different things, or the signal conflicts with existing content. A clean,
unambiguous statement gets staged, not questioned.

```text
- [ ] Q: <one concrete question, self-contained> (owner: client|team) (ref: <INT-###>)
      A:
```

- **Self-contained** — readable by someone who has not seen the signal, the hub, or this run.
- **Plain business language for `owner: client`** — no `signal`, `slug`, `UC`, `staged`, or other vault
  vocabulary. `owner: team` may use ids, always paired with what they say.
- **One question per line**; three or more options get `(a)/(b)/(c)`.
- **One question, two places is a bug.** If the source INT note already asks this, Gate 1 should have
  parked the signal `held` before it reached this lane.

When a question resolves, Stage 1 folds in the answer and **moves the line into the decision log**
table — topic, who raised it and what they said, what was decided, the date. The checkbox list holds
only what is still open, which is what keeps the status invariant countable.

## Conflict with existing content

Two statements that cannot both hold. **Never pick a winner** — recency settles a supersession; it does
not settle a disagreement between two people's requirements.

```text
1  flip the new Signal Log row: Status: conflict, Notes: conflicts with #<n>
2  raise ONE question on the UC naming BOTH sides in plain language, and the S#/flow each affects
3  STAGE NOTHING for this signal
   → a conflicting proposal in ## Discussion becomes foldable the moment the box is ticked,
     regardless of which side the answer picked
```

## What this lane never does

- Write into `## 1`–`## 6` directly — that is Stage 4 Part 2 for a main-flow step or a flow, same
  run, or Stage 1's fold-in for everything else, after the gate. Never this lane.
- Write a UC owned by another `primary_feature`, or touch another feature's hub.
- Write a rule statement into `## 4`, or any `BR-###` content beyond adding this UC to its `uc:` list.
- Renumber, reuse, or delete an `S#`, `A#`, or `E#`.
- Write `status: approved`, `removed`, `enriched`, or `consolidated` — approval and removal are
  human-gated; the other two belong to their own skills.
- Write `## Domain Concerns` or the summary block — `/enrich-feature` owns both.
- Edit an `FR-###`'s body, or set it `removed`. An absorbed FR is frozen history.
