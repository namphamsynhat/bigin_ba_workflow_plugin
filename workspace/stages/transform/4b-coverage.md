# Stage 4b — Coverage: does this feature's use-case set add up?

```text
runs: orchestrator, per in-scope feature, immediately after Part 3's conflict check
in:   the feature's whole live UC set (each one's ## 1 and ## 2), its BR-### files, the hub's
      one-line description + its {requirements_file} row, its open PP-### rows, and the entities
      its UCs and BRs cite
out:  one `## Coverage Gaps` row per gap found, on that feature's hub · existing rows re-statused ·
      the open ones mirrored into ## Open Questions / Gates
never: minting a UC · drafting a step, flow, or rule to fill a gap · parking a UC that is otherwise
       ready because something ELSE is missing
```

Part 3 asks whether this feature's requirements **contradict** each other. This asks the other half:
whether they **add up** — whether the actor could actually get this feature's job done with only what
is written down.

A contradiction is visible in the artifacts; a gap is visible only against the business. Nothing on a
hub says "nobody described how a donor gets created", because the missing thing left no trace: no
signal, no row, no question. Four donation use cases can each be individually sound, individually
approved, and together describe a module nobody can use — one that records gifts against donors that
no workflow ever creates, finds, corrects, or retires. **The absence of a signal is not evidence that
the business has no need.** It is usually evidence that the obvious was never said out loud.

That is what this stage is for, and it is the only stage that looks at a feature's use cases *as a
set* rather than one at a time.

## When it runs

Per feature in scope, when **any** of these holds:

```text
a UC on this feature was created this run, or its ## 2 changed      # the usual trigger
the hub has no `## Coverage Gaps` section at all                    # never checked — backfill once
$ARGUMENTS named this slug explicitly                               # a human asked about this feature
```

The first is what keeps the cost proportional: a run that only staged a rule mirror re-checks nothing.
The second is the one-time backfill for a feature whose UCs predate this stage. The third is why an
**empty Stage 2 worklist does not skip this pass** when a slug was named — `/bigin-transform-signal
donor-module` with no new signals is exactly someone asking "is this feature complete?", and the
answer is worth more than "nothing to qualify, stopped".

Skip a feature with **no UC at all** — there is no set to reason about, and its hub's
`## Requirement Readiness` already says so.

## The lens — six tests, in this order

Run every one. Each names a gap only when **both** halves hold: the business plainly needs it, **and**
the record is silent — no UC, no `## Discussion` entry, no BR, no open question, and no signal that
says it lives somewhere else.

| Lens | The test | A gap reads like |
| :--- | :--- | :--- |
| `lifecycle` | For each entity **this feature owns**: is there a use case for every stage the business actually runs — brought into existence · found or listed · corrected · moved through its states · retired or archived — plus **merged/deduped** where real duplicates happen? | four UCs record, certify, and audit donations; **no UC creates a donor**, and nothing says how a duplicate donor is resolved |
| `precondition` | For every `## 1` **Pre-condition** on every UC: which UC — or which explicitly-named external system — makes it true? | "the donor's mailing address is on file" is a pre-condition and no UC ever records one |
| `actor` | For every actor named in any `## 1`, **secondary as well as primary**: does that role hold the goal(s) it needs, or is it only ever acted upon? | finance downloads tax certificates; nothing says who sets up or amends the certificate template |
| `goal` | The feature's own stated purpose — the hub's one-line description, its `{requirements_file}` row, its open `PP-###` rows: does the set deliver it? **An open pain point no UC's `pain_points:` cites is a gap by definition** | PP-007 "staff re-key donations from spreadsheets" and no UC imports anything |
| `data` | For every field, code, status, or record a step or a `BR-###` **reads**: does some UC ever **write** it? | BR-017 designates a gift's calendar year; no UC sets or corrects that year |
| `rule` | For every `BR-###` on this feature: is it mirrored in some UC's `## 4` with a real enforcement point? A rule with no workflow has nothing to bite in | BR-041 restricts certificate access; no UC covers granting or revoking it |

**The guard that keeps this honest.** Not every silence is a gap:

```text
NOT a gap:
  an entity ANOTHER feature owns          → its lifecycle is that feature's coverage question
  reference/config data the client said is set up once, elsewhere, or imported
  a stage the client explicitly ruled out ("we never delete a donor") — that is a stated answer
  something already sitting as an open question, a `held` signal, or a `## Discussion` entry
  a stage a UC covers under a different name — read ## 2 and ## 3, never the title alone
STILL a gap:
  a stage nobody has mentioned in either direction. Silence is the finding.
```

**Rank, and say what you held back.** Order new gaps by how much of the feature they block — one
missing create is worth more than five missing archive paths. A pass that would raise more than five
new rows on one feature raises the top five and **reports the number it held back**; the rest re-derive
on the next pass, because this stage reads the vault fresh every time and keeps no state of its own.

## What it writes

One row on the hub's `## Coverage Gaps`, appended — creating the section from `{template_hub}` if the
hub predates it (§ Adopting an existing Feature Hub):

```text
| # | Gap | Lens | Raised | Status | Notes |
| 3 | Nothing describes how a donor record is created, or who may create one. | lifecycle | 2026-08-21 · UC-012 | open | blocks UC-012, UC-013, UC-014 |
```

- **`#` is permanent**, append-only, never renumbered or deleted — same discipline as the Signal Log
  and `## Design Directives`.
- **`Gap` is one sentence of plain business language, and it is a question a client can answer.** No
  slug, no lane, no `staged`, no vault vocabulary — this line gets read out loud in the next client
  call. State what is unaccounted for; **never propose the answer.** "Nothing describes how a donor
  record is created" — not "donors should be created by an admin".
- **`Lens`** is the column of the table above that found it — it tells a reader why anyone thinks this
  is missing.
- **`Raised`** is the date plus what exposed it: the UC whose pre-condition dangled, the `BR-###` with
  no enforcement point, the `PP-###` nothing cites.
- **`Status`**: `open` (nobody has answered) · `answered` (a human said what should happen; it still
  needs to arrive as intake before it can become content) · `covered` (a UC now covers it — cite the
  id in `Notes`) · `rejected` (explicitly out of scope — cite who decided, in `Notes`).
- **`Notes`** carries the UC ids it blocks, the id that closed it, or the decision that killed it.

Then, in the same pass:

```text
re-status every EXISTING row before appending a new one:
    a UC now covers it            → `covered`, Notes: covered by UC-###
    a human answered it on the hub → `answered` — leave it for /bigin-intake to capture as a signal
    still silent                  → leave it `open`. Do NOT re-raise it as a second row
mirror every `open` and `answered` row into `## Open Questions / Gates`, same sentence
append one `## Changelog` line: coverage pass, N new gap(s), N closed
```

An `answered` row is **not** content and never becomes content here. The answer is new raw material:
it goes through `/bigin-intake` → `/extract-signal` → this skill, like everything else. Drafting a step
from an answer typed onto a hub is how unsourced scope enters the vault.

## What this stage never does

- **Never mint a UC, and never draft the missing flow.** A gap is a finding, not a work order. The
  content comes from the answer, through intake, like every other requirement.
- **Never park, revert, or question a UC because a *different* thing is missing.** UC-012 "Record a
  donation" is approvable on its own merits even while nobody has said how a donor gets created — a
  coverage gap is feature-level, and pushing it onto a UC's `## 5` parks an artifact that was ready.
  This is precisely why gaps get their own register instead of borrowing the question mechanism.
- **Never raise a gap as a `- [ ] Q:`** on a UC or a BR, and never write one onto an intake note.
- **Never write a Signal Log row.** No signal was received; inventing one to carry a gap breaks the
  one thing that table guarantees — that every row traces to something somebody said.
- **Never flip a row to `covered` on the strength of a `## Discussion` entry.** Staged is not written.
- **Never touch another feature's hub.** A gap that turns out to belong to another feature is raised on
  **that** feature's hub, by that feature's own pass — name it in the report instead.

## Adopting an existing Feature Hub

A hub created before this stage existed has no `## Coverage Gaps` section. This is **self-healing and
needs no migration**: the first coverage pass to touch that hub inserts the section from
`{template_hub}`, immediately after `## Use Cases`, and fills it. Until then the hub simply carries no
gaps, which reads correctly as "never checked" rather than "checked, nothing found" — because the
backfill trigger in § When it runs treats a missing section as a reason to run.

Insert the heading and the table header only. Do **not** reorder, reformat, or re-derive any other
section of the hub while you are in there.

## Report line

```text
coverage: <slug> — <N> new gap(s) (<lens>, <lens>), <N> closed, <N> held back for the next pass
          <slug> — clean
```

`clean` is a real and common result, and worth printing: it is the difference between "the set adds up"
and "nobody looked".

## Failure modes

- **Inventing the answer instead of naming the gap.** "Donors are created by an admin during
  onboarding" is a guess with a plausible shape, and once it is on the hub the next reader treats it as
  something the client said. Name what is missing; stop there.
- **Treating silence as consent.** The opposite failure, and the one this stage exists for: no signal
  ever arrived saying "we create donors", so nothing in the vault looks wrong.
- **Parking a ready UC over a feature-level gap.** Turns a finding into a stalled approval.
- **Re-raising a gap that already has a row.** The register grows, the mirror doubles, and the human
  reads the same missing thing three times and trusts the section less each time.
- **Demanding CRUD for every entity.** Reference data, an entity another feature owns, and a stage the
  client ruled out are all accounted for — the lens needs the business need *and* the silence.
- **Running the lifecycle test off the entity register alone.** An entity's stages live in the UCs'
  `## 2` steps; a `proposed` row in `{entities_file}` says a thing exists, not which of its stages
  anybody described.
- **Skipping the pass because the run "only" updated a UC.** A new step is exactly how a
  pre-condition nothing satisfies gets introduced.
- **Letting a per-feature Stage 3 subagent do this.** It sees one feature's signals, not its whole UC
  set, and it holds an `Edit` tool over files this pass must only read. This runs in the orchestrator,
  after every subagent has reported, like the rest of Stage 4.
