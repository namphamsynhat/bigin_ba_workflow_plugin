# FR lane — drafting and updating a Functional Requirement

Handles signals routed to **FR** and to **Context** (`3-routing.md` § The lane table). Read
`3-routing.md` § New vs. update first — this guide assumes that lookup has already been made.

## Creating a new FR

Only when nothing on the feature covers the subject. Instantiate `{template_fr}` as
`{fr_dir}/FR-<NNN> <Title>.md`, with the id from the `Grep` scan (`3-routing.md` § New vs. update).

Frontmatter to fill on creation:

| Field | Value |
|---|---|
| `id` / `title` | `FR-<NNN>` and a short noun-phrase title — the same title as the filename |
| `status` | `draft`, always. Stage 5 may move it to `needs-clarification`; nothing here writes anything else |
| `version` | `1.0` |
| `feature` | The hub's slug |
| `sources` | The `INT-###` this signal traces to |
| `attachments` | Copied from the source INT note's own `attachments:` — every path, not a summary |
| `owner` / `updated` | `team`, today |

Leave `links:` and `amends:` empty. Leave the `> [!summary]-` block blank — `/enrich-feature`
writes it.

Then add the FR's id to the hub's `fr:` frontmatter list, oldest first.

**Never write into `## Functional requirements` on creation.** A new FR is created *empty* of
requirement lines, with its first content staged in `## Discussion` like any other change. The gate
applies to the first line as much as the hundredth — an FR whose initial content bypassed review is
indistinguishable afterwards from one that passed it.

## Staging a change — new or update, same procedure

Append one entry per pending signal to `## Discussion`, in the format the template defines:

```
- **<INT-###>** (staged <YYYY-MM-DD>): <the signal, tightly paraphrased or quoted> → proposed:
  <the exact FR line this becomes, numbered FR-<NNN>.<n>>
```

Rules that keep a staged entry foldable without re-reading anything:

- **Write the proposed line as final text**, not as a description of what to write. Stage 1's
  fold-in copies it into `## Functional requirements` verbatim; an entry saying "add a rule about
  approvals" cannot be folded by a later run without re-deriving it.
- **One entry per signal**, even when three signals produce three adjacent lines. Signals resolve
  at different times, and a merged entry cannot be half-folded.
- **Cite the `INT-###`**, always — it is what Stage 1's dedup-check reads out of `## Changelog` to
  recognize a completed apply.
- **Copy the note's `attachments:` onto the FR's own `attachments:`** if not already listed. A
  feature's material is incomplete without the documents its requirements were drawn from.
- Flip the Signal Log row to `Status: staged`, `Destination: FR-###`.

For an **update**, the proposed line says what the existing line becomes, naming it:
`FR-012.3 becomes: <new text>`. Deletion is expressed the same way — `FR-012.3 is removed because
<reason>` — never by quietly dropping the line at fold-in time.

## Raising a question — only when a decision is genuinely needed

A question is warranted when the wording is ambiguous enough that two readers would build different
things, or when the signal conflicts with an existing row. It is **not** warranted for a clean,
unambiguous statement — manufacturing a question to have one adds a human round-trip to something
that needed none, and the interactive path exists precisely so a clear signal can be folded
immediately.

Write it on the FR's own `## Open Questions`, following `conventions.md` § Open Questions wording:

```
- [ ] Q: <one concrete question, self-contained> (owner: client|team) (ref: <INT-###>)
      A:
```

- **Self-contained**: readable by someone who has not seen the signal, the hub, or this run.
- **Plain business language for `owner: client`** — no `signal`, `slug`, `FR`, `anchor`, or any
  other vault vocabulary. `owner: team` questions may use it.
- **One question per line.** Three options or more get `(a)/(b)/(c)`.
- **One question, two places is a bug** (`conventions.md` § One question, two places). If the
  source INT note already asks this, do not copy it here — Gate 1 in `2-qualification.md` should have
  parked the signal `held` before it ever reached this lane.

## The Context sub-lane

Two destinations, both on the FR, neither gated — they add provenance, not requirement content.

**`## Business goal`** — the client's stated why, in the client's own terms. Write only what was
actually said. A `decision`-type signal has no `Why` by design (`_bigin/stages/extract/2-extraction.md` § The `Why`
field); routing one here and inventing a rationale for it launders a guess into the record.

**`## Problem & Pain Points`** — a mirror of this FR's rows from
`01-Requirements/PAIN-POINTS.md`, same columns. `extract-signal` already created the `PP-###` row
and the hub's copy; this lane adds the FR's copy and keeps all three identical. Never mint a new
`PP-###` here — if a pain point has no register row, that is an extraction gap to report, not one
to fill silently.

## Conflict with an existing row

Two statements that cannot both hold. Never pick a winner — recency settles a supersession
(`2-qualification.md` § 4c), but it does not settle a disagreement between two stated requirements.

1. Flip the new Signal Log row to `Status: conflict`, `Notes: conflicts with #<n>`.
2. Raise one question on the FR naming **both** sides in plain language, so the reader can choose
   without opening the hub.
3. Stage nothing for this signal — a conflicting proposal in `## Discussion` would be foldable by
   Stage 1 the moment the box is ticked, regardless of which side the answer picked.

## What this lane never does

- Write into `## Functional requirements` directly (that is Stage 1's fold-in, after the gate).
- Write `status: approved`, `removed`, `enriched`, or `consolidated` — approval and removal are
  human-gated (hard rule 4); `enriched`/`consolidated` belong to their own skills.
- Write `status: in-review` or `superseded` on an FR — both retired (`conventions.md`
  § Status vocabularies).
- Write `## Domain Concerns` or the summary block — `/enrich-feature` owns both.
- Touch another feature's FR. A signal that turns out to belong to a different slug is an
  anchoring error: leave it, flag it in the report, and let `/extract-signal` re-anchor it.
