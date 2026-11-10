# Analysis and withdrawal

Human reference for the `extract-signal` **analysis** subagent (2d, card `cards/analyst.md`) and for withdrawing a
request the client removed (`bigin note withdraw`).

```text
in:   `bigin worklist analyze <INT>` — the FILED note's rows and hub rows, plus the current requirements of every
      feature it anchored to: UC cards (summary, steps, flows, § 4 rules, open questions), BR statements, the
      pending (not yet drafted) rows of those hubs, and the questions already open on the note
out:  an `analysis` JSON (lib/bigin/schema/analysis.json). `bigin note analysis-apply` writes the note's
      engine-owned ## Analysis, adds the questions to ## Open Questions, and holds blocking conflicts
never: ## Raw, a UC or BR file, or any edit to the spec — the analyst reads; transform writes
```

## Why it runs at extract

The team receives a request and has to answer, the same day, three things a business analyst would: what does it
change, what does it contradict, and what is still unclear. Transform answers them only after it has drafted —
too late for the conversation with the client. Analysis answers them right after filing, against the spec as it
stands, so the questions go back to the client while the request is still being discussed. It is not a gate:
nothing waits on it except a row the analyst finds in blocking conflict.

## What the analyst writes

| Field | What | Rule |
|---|---|---|
| `summary` | 2-4 sentences: what is asked and why, in the analyst's words | no new facts — only what the rows say |
| `flow` | the requested to-be flow, one actor action per item | a step the source leaves open is written with `?` and gets a `gap` question |
| `affected` | one entry per UC / BR the request changes, or `new` for a goal no UC covers | `refs` = the steps/flows it lands on; `change` = add · modify · remove · new-goal · rule · review |
| `conflicts` | the request says X, the current requirement says Y, both cannot be true (blocking) or need a check (minor) | `with` names the exact UC step, BR, or pending hub row; ONE decision question naming both sides |
| `questions` | `unclear` (reads two ways against the spec) · `gap` (implementation needs a detail nobody stated) · `impact` (it silently changes something else the client should confirm) | self-contained, one decision each, never a question already open on the note or the UC ‹questions.md § Open Questions wording (all artifacts)› |

### Affected — same goal, not same words

A request changes a UC when the same actor sits down to accomplish the same goal (`3-routing.md` § Which UC — new
or update). A different goal is `new`; a rule shared by several UCs is the BR (`change: rule`) — the engine adds
every UC enforcing it, and every UX spec, epic and story built on the hit UCs, to the section on its own. Name a
UC you only suspect as `change: review` with the reason, never as a modification.

### Conflicts — against the spec, not against taste

Compare each to-be row with the step, flow or rule that already covers the same moment. A conflict is a
contradiction of fact (who acts, what threshold, what order, what is allowed). A request that only adds detail is
not a conflict. An approved UC is the current agreement: contradicting it is always `blocking`. A pending hub row
from another note (not yet drafted) is cited as `<slug> #<row>`. `bigin note analysis-apply` flips the note row
and its hub row to `conflict` for every blocking entry, so transform drafts nothing over the current spec until
the question is answered.

## Withdrawal — a removed request leaves the spec

The client may remove a ticket, or drop a whole feature (too costly, no longer fits the market), after its
requirements were extracted, filed, even applied to a use case. The source of truth must not keep a requirement
nobody asks for, and the team must be able to read why it left. Withdrawal is on exactly one of two things:

| What the client removed | Command | Never |
|---|---|---|
| one **ticket** | `bigin note withdraw INT-###` (a `source: jira` note) | a meeting or email note — it covers many things |
| a whole **feature** | `bigin feature withdraw <slug>` | a feature another live feature still depends on is not torn out: shared use cases and rules stay |

A single point dropped in a meeting ("forget partial payments") is neither: it is a new signal, filed and
superseded by transform like any other change.

### A ticket

```text
bigin note withdraw INT-### --reason "<why>" [--by "<who, where, when>"]
   or a Jira status mapped to the `withdrawn` phase (project.md ## Jira status mapping) on the next sweep
   or, for a deleted ticket the sweep can no longer fetch, the skill runs the command for it

note       status: withdrawn, withdrawn: <date>, withdrawn_reason — ## Withdrawal records what was closed;
           ## Raw and every row stay (history is never deleted)
hub rows   new / held / question / conflict / staged → withdrawn   (staged: its ledger change sets superseded)
           applied → retract: the next /bigin-transform-signal hands it to uc-router, which drafts the change
                     sets that take it back out; `bigin apply` flips the row to withdrawn and writes
                     "retracts withdrawn INT-### (<date>: <reason>)" on the UC's Changelog — an approved UC
                     goes back to draft for re-approval like any other content change
           a row that also cites another note → kept, flagged "partly withdrawn — review"
questions  an open question on a UC/BR raised by this note alone is ticked "Not needed — withdrawn"
```

### A feature

```text
bigin feature withdraw <slug> --reason "<why>" [--by "<who, where, when>"]

FEATURES.md    the row → out-of-scope, Notes "withdrawn <date>: <reason>"; the hub → status out-of-scope,
               withdrawn / withdrawn_reason, a ## Withdrawal record
use cases      owned by the feature (primary_feature) → removed: version bumped, open questions ticked
               "Not needed", the reason on the Changelog — unless another LIVE feature is in its features:,
               then it stays and only this feature's rows are retracted
rules          governed by the feature → removed, unless a use case that stays still enforces them
ledger         change sets from this hub, or onto a removed UC/BR → superseded
Signal Log     new / held / question / conflict / staged → withdrawn; applied into a removed UC/BR →
               withdrawn ("removed with UC-###"); applied into a UC that stays → retract (as for a ticket)
intake notes   rows filed to the feature → withdrawn; the notes stay live for everything else they said
downstream     every UX spec, epic and story built on a removed use case is flagged stale (bigin cascade);
               their own status is never changed — the team decides what to do with work in flight
afterwards     new intake for the slug is rejected at filing ("out-of-scope — skipped"); reinstating is a human
               edit: FEATURES.md back to committed, each removed UC/BR back to draft, with the reason
```

Both commands are the human's decision, run by the human or by the agent on the human's explicit instruction —
never inferred from a thread. `removed` stays human-gated (`core.md` § Status vocabularies): the command is how
the human sets it, with the reason attached.

### Retracting applied content

The route worklist hands a `retract` row with `retract.reason`, `retract.remove_from` (its Destination) and
`retract.still_wanted_by` (live rows on any hub whose Destination overlaps). For each piece of content it put in:

```text
nothing else wants it          → drop_step / drop_flow (reason "removed — <INT> withdrawn: <reason>"),
                                 unmirror_br, or set_rule restoring the rule without its clause
it is merged with live content → replace_step / replace_flow keeping only the live part
another live row still wants it → keep it: a link / append_note change set re-tracing it, so the row closes
always                         → trace the retract row's hub_rows, so `bigin apply` closes it as withdrawn
```

A withdrawn ticket the client reinstates is a new request: capture it again; the old rows stay withdrawn.
