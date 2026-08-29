# Stage 3 — Capabilities, flows, rules, information: §§ 5-8

```text
runs: per feature (orchestrator inline, or one worker per feature)
in:   each folded UC in FULL (§ 1-§ 6) · every BR-### in its brs: · every EN-### in its entities:
out:  §§ 5-8 of {prd_dir}/PRD-<NNN> <Feature>.md
never: editing a UC, a BR, or an entity (P4) · a technical sentence (P1) · a folded
       non-approved UC (P2) · a step, branch, rule, or field no artifact states (P3)
```

This is the stage the whole document exists for. §§ 1-4 frame it and § 9 illustrates it; § 6 is what
a business reader actually checks.

## The translation rule

A UC is written for a BA. A PRD is written for a business owner. The difference is not formatting:

```text
UC step  (S4)  | Parent submits the enrolment | System validates the student is not already
                                                enrolled in the term, writes the enrolment record,
                                                and emails the parent a confirmation
PRD § 6        | The parent submits the enrolment. The school confirms the student is not already
                 enrolled for that term, records the place, and confirms by email.   (S4)
```

Same facts, one voice. What changed: the actor/system column split collapses into a sentence the
business speaks; "writes the enrolment record" becomes "records the place". What did **not** change:
the validation, the record, the notification. Dropping any of the three is how a flow silently loses
scope.

**P1's test, applied here:** if a sentence names an endpoint, a table, a payload, a status code, a
framework, or a field type, it is a UC's System Response leaking through untranslated.

## § 5 Business Capabilities

One row per folded UC. This is the capability contract — a capability absent here will not be
designed, decomposed, or built.

| Cell | Fill from |
|---|---|
| `#` | sequential in this PRD, `C1`, `C2` — permanent once written, never renumbered |
| `Capability` | the UC's `title:`, which is already an active verb phrase. Keep the client's noun |
| `Actor` | § 1 `Primary Actor` |
| `Value to the business` | § 1 `Business Need / Goal`, one clause |
| `UC` | `UC-<NNN>` |
| `Flow` | a link to the § 6 block: `§ 6 <Capability name>` |

Order by how the business experiences the feature — the flow a user meets first, first. Id order is
minting order and means nothing to a reader.

## § 6 Business Flows

One block per folded UC.

**The four framing lines** come from § 1: `Trigger`, `Pre-conditions`, `Post-conditions (success)`,
`Post-conditions (failure)`. Translate each; never skip the failure line because it looks
redundant — it is the line that tells a sponsor whether an abandoned enrolment leaves a half-made
booking behind, and it is the most commonly empty cell on the UC template.

**The step table** — one row per `S#` row in the UC's § 2, in row order (which is flow order; the
ids are not sequential and must not be re-ordered into sequence,
`core.md` § ID scheme):

```text
What happens   one sentence, business voice, carrying the actor's intent AND what the business
               gets from the system. Cite the S# at the end of the cell or in the Step column
Actor          the actor named in that step, not the feature's primary actor by default
Screen         from § 9's inventory, once Stage 4 has built it — the screen the actor is on for
               this step. "—" when no design covers it. NEVER a screen name you invented (P6)
```

Filling `Screen` before § 9 exists is the ordering trap here. Two valid orders: write § 6 with
`Screen` as `—` and fill the column in Stage 4, or read the UX spec's `Serves` column (which cites
`S#` ids directly) at Stage 4 and backfill. Either way § 6's steps come from the UC, never from the
screens — a screen inventory is not a flow, and specc'ing the flow from it inverts the pipeline.

**The branch table** comes from the UC's § 3, one row per `A#`/`E#`:

```text
Situation                 the § 3 condition as a DETECTED BUSINESS FACT ("the card is declined"),
                          never as a question ("is the card valid?")
What the business does    the flow's steps, condensed to one sentence
How it ends               "rejoins the main flow", a different success, or the failure and what the
                          actor is left with
Ref                       A#/E#
```

**A UC with no § 3 gets no branch table.** Omit it. An invented failure path becomes scope the client
never asked for, and it looks exactly like a real one.

## § 7 Business Rules & Policies

A mirror of the `BR-###` files in each folded UC's `brs:` — read the BR file for the statement, and
the UC's § 4 for `Enforced at`. Never write a rule from the UC's mirror alone; the BR file is the
source (`core.md` § ID scheme).

```text
Applies at              the § 4 Enforced at value, in words + the id in brackets:
                        "when the parent submits the enrolment (S4)"
                        "before the flow can start (pre-condition)"
Consequence if broken   what the business does about it — from the E# flow that handles it, or the
                        BR's own statement. Unstated → "not stated"
```

Two findings to report rather than absorb:

- a `BR-###` in a folded UC's `brs:` whose § 4 `Enforced at` cell is blank → the rule is either
  misfiled or a step is missing. Report it; do not guess the step.
- a rule referenced by a UC this PRD folds but whose statement contradicts another folded rule →
  report as a conflict for `/bigin-transform-signal`, and raise it in § 11. The PRD never reconciles
  two rules by choosing one.

## § 8 Business Information

One row per `EN-###` in the folded UCs' `entities:` lists, read from `{entity_dir}`.

```text
Information                the entity, in the client's word for it
Why the business keeps it  the business reason, from the entity doc or the UC step that creates it
Key facts held             the handful a stakeholder would name out loud, in their words:
                           "who the student is, which term, what was paid"
                           NOT the field list, NOT types, NOT keys, NOT cardinality  (P1)
Who owns it                the role accountable for it being correct
```

An entity still `proposed` in `{entities_file}` with no promoted `EN-###` file yet is listed with its
id as `—` and a note that it is not promoted; `/sync-entities` promotes it. Do not describe fields
from the register row's name alone.

**Skip § 8 entirely, with one line saying so, when no folded UC lists an entity.** An empty table
reads as "this feature holds no information", which is a claim, not an absence.
