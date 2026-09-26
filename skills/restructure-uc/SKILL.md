---
name: restructure-uc
description: Split a Use Case that has outgrown one user goal into two or more use cases, once a human has judged the seam — live, while reviewing a UC, or by answering a `/bigin-transform-signal` Stage 3 granularity question (`3-lane-uc.md` § Recognizing drift). Moves existing `S#`/`A#`/`E#` content to its new home (the source's originals become `Dropped — moved to UC-###`, never renumbered) through engine change sets, repoints every affected `BR-###`, and refreshes every touched feature hub. Assumes the split reorganizes signals already on file — it never invents a new intake note for the reorganization itself, only for a genuinely new decision the human explicitly names. Use when a UC mixes more than one primary actor or trigger, when `/bigin-transform-signal` has raised (and a human has answered) a granularity question, or when asked to "split this UC", "restructure UC-###", or "this use case isn't created well, break it apart".
argument-hint: "<UC id, e.g. UC-011> [proposed split, e.g. \"spend channels into 3 UCs, switch into its own\"]"
---

# Restructure UC

A `UC-###` grows by accretion — `/bigin-transform-signal` runs unattended, and each run's honest read of
"does this signal update the existing goal" can be wrong in a way that only becomes visible several runs
later, once the UC covers a Parent's spend goal, an Admin's override goal, and the wallet's own
record-keeping, all under one title. This skill is the deliberate, human-gated repair for that drift —
distinct from `/bigin-transform-signal`, which only ever *proposes* a split (`3-lane-uc.md` § Recognizing
drift) and never executes one.

This skill assumes the split is a **reorganization of signals already captured and already cited** on
the source UC and its feature hub(s) — not a new client statement. It never creates a `00-Inbox/INT-###`
note on its own initiative. If the restructuring is driven by something genuinely new the human just
said — not "this UC mixes two goals" but "actually, here's a third thing the client told us" — that is a
`/bigin-intake` capture in its own right, done first, separately; this skill takes its resulting
`INT-###` id as an input the same way it takes everything else, never inventing one to fill the gap.

> **Artifact Standard:** Outputs:
>> **The source UC**, narrowed, `## 2`/`## 3` rows marked `Dropped — moved to UC-###` where
>> content left, retitled if its remaining scope no longer matches its old title, flagged for
>> `/approve-uc` review.
>> **One or more destination UCs**, new or existing, each `status: draft` if newly created (or
>> re-recounted if existing), carrying the moved content and its original citations, also flagged for
>> review.
>> **Every affected `BR-###`**, `uc:` repointed to whichever destination(s) actually enforce it now.
>> **Every touched feature hub**, refreshed by the engine — `bin/bigin hub refresh` (`uc:` pointers,
>> `## Use Cases`, `## Requirement Readiness`, the add-only `## Open Questions / Gates` mirror) and
>> `bin/bigin links sync` (`brs:`/`uc:`/`features:`/`sources:` and `01-Requirements/FEATURES.md`'s UC
>> column). No agent edits a hub's derived tables.

---

## Non-Negotiable Core Rules

* **Never decide the split boundary without the human.** A UC "feeling" over-scoped is this skill's
  reason to *ask*, never its reason to *act*. Where the seam falls — which steps go where, what each new
  UC is called, who its primary actor is — is confirmed with the human before any file is touched, even
  when the request already states a boundary (§ Resolving the plan, below, still restates it back).
* **No new intake by default.** The ordinary trigger is "the pipeline already filed these signals, it
  just organized them under the wrong UC boundary" — reuse every citation the source UC and its
  destination content already carry. Only create or reference a fresh `INT-###` when the human
  explicitly says a new statement — not a reorganization — is driving the split, and even then, take the
  id as given rather than minting the intake note from inside this skill.
* **Permanent ids, always.** A source `S#`/`A#`/`E#` that moves becomes `Dropped — moved to UC-###`
  (a `drop_step` / `drop_flow` change set), in place, never renumbered or deleted. A destination that is a brand-new UC gets its own fresh `S#`/`A#`/`E#`
  sequence starting at 1 — it is not required to preserve the source's old numbers.
* **`uc-splitter` drafts, the engine writes.** Since v1.10.0 `uc-splitter` writes nothing in the vault:
  it turns the settled plan into one `changesets` JSON (`drop_step`/`drop_flow` on the source, `create_uc`
  with a `key` or `new_step_after`/`new_flow` on each destination, `mirror_br` for every rule that follows,
  `link` for `sources:`/`features:`). `bin/bigin apply` mints any new UC id under the id lock, applies every
  set with one write per artifact, flags each UC whose § 2 changed for review, and refreshes the hubs it
  touched. Nobody greps for the highest id by hand any more.
* **Feature hubs and `FEATURES.md` are the engine's.** `bigin apply` already runs `links sync` and
  `hub refresh` for every hub it touched; run `bin/bigin hub refresh <slug> …` again only if a hub was
  touched outside the apply. Never edit `## Use Cases`, `## Requirement Readiness`, `## Open Questions /
  Gates`, `uc:` or `FEATURES.md`'s UC column by hand.
* **Verify before reporting done.** Run `bin/bigin lint --full` once after the apply, and resolve every
  finding the restructuring itself caused (a citation that stops resolving once its content moves to a new
  `sources:` list, a § 4 row on the source for a rule that no longer applies there) before telling the
  human it's done — a clean restructuring that leaves lint findings behind just
  relocates the review burden instead of closing it.

---

## Precondition — check this first

Missing `_bigin/conventions/core.md` or `_bigin/templates/` → stop, say `/bigin-new-project` must
run first.

`$ARGUMENTS` names a `UC-###` that doesn't exist under `01-Requirements/_ucs/` → say so and stop.

With no id given: check for a UC carrying an answered Stage 3 granularity question first (a `## 5`
`- [ ] Q:` proposing a split, now ticked with an `A:`) — offer that one. Otherwise ask which UC needs
restructuring; don't guess.

## Input

Read the named `UC-###` in full — `## 1` through `## 6`, every `S#`/`A#`/`E#` including any already
`removed`, its `## Discussion`, and its `## Changelog`. Read `primary_feature`'s hub and every other slug
in `features:`, and every `BR-###` in `brs:` — the same related-artifact context `/approve-uc` collects,
for the same reason: no restructuring decision should be made blind to the UC's existing neighborhood.

## What to do

1. **Confirm the smell, don't assume it.** State back, in one or two sentences, which of the UC's steps
   read as belonging to more than one actor or trigger — the same check `3-lane-uc.md` § Recognizing
   drift describes. If the human's own request already names the boundary, restate it as understood
   rather than skip this step; a paraphrase the human can correct is cheap, a wrong split is not.

2. **Resolve the plan.** For each piece of the UC that's splitting off. determine:
   - **Destination**: a brand-new UC (title + primary actor + `primary_feature`) or an existing UC
     absorbing the content — ask if genuinely unclear which fits better, don't default to "always new".
   - **Which `S#`/`A#`/`E#` ids move there**, and whether the moved text carries over verbatim or needs
     rewording now that it stands alone (e.g. a step whose System Response referenced a sibling step
     that isn't moving with it).
   - **Which `BR-###`(s) follow**, and at which of the destination's steps each is now enforced.
   - **Whether this is a pure reorganization** (default — no new intake) or **traces to a new decision**
     the human is stating right now (rare — capture it as a direct-capture `/bigin-intake` note first if
     one doesn't already exist, then treat its `INT-###` id as a normal input alongside everything else).
   Surface anything genuinely ambiguous as a written question rather than guess — the same discipline
   `/bigin-transform-signal` applies to every other drafting decision.

3. **Build the worklist.** `bin/bigin worklist split UC-### --out _runs/<run>/tasks/UC-###.split.in.json`
   (the full UC card: summary, every step/flow with its `sha`, § 4 rows, open questions), and write the
   settled plan from step 2 next to it as `UC-###.plan.json` — destinations (existing id, or `key` +
   title + primary actor + `primary_feature` + `features`), the `S#`/`A#`/`E#` → destination mapping with
   any reworded text, the BR → destination/enforcement mapping, and, only if step 2 found one, the
   `INT-###`/row # a genuinely new decision should cite.

4. **Dispatch `uc-splitter`** with its card (`cards/splitter.md`), the worklist and the plan; it writes
   `_runs/<run>/tasks/UC-###.split.out.json` (schema `changesets`) and replies with one line.
   Then `bin/bigin ingest <out> --kind changesets --run <run>` — on schema errors, resume the same agent
   once with the errors.

5. **Apply.** `bin/bigin apply _runs/<run>/tasks/UC-###.split.out.json --run <run>`. The engine mints each
   `create_uc` id (locked), drops the moved source rows with their reason, lands every destination step,
   flow and mirror, records the change-set ids in each UC's Changelog (re-running is a no-op), and
   refreshes every touched hub and `FEATURES.md`. A `drift` result means the UC was edited after the
   worklist was built — rebuild the worklist and re-dispatch; an `invalid` result names the set to fix.

6. **Verify.** Run `bin/bigin lint --full`. Fix anything the restructuring caused; report anything genuinely
   pre-existing (not caused by this run) without fixing it — a restructuring is not a license to clean up
   every unrelated finding in the vault, only the ones this operation introduced.

7. **Summarize** — every UC touched (source + destinations) and its new `status`, every BR repointed,
   every hub refreshed, and the explicit next step: all touched UCs are `draft`/`needs-clarification`,
   never auto-approved, flagged for `/approve-uc`. (Enrichment is feature-level now — a UC split alone
   never calls for a `/enrich-feature` refresh unless the split itself changed the feature's scope.)

## Additional Resources

- **`_bigin/stages/transform/3-lane-uc.md` § Granularity / § Recognizing drift** — the detection-side
  rule this skill is the execution-side counterpart to; read it for the exact conditions that should
  have raised the split question in the first place.
- **`cards/splitter.md`** — the splitter's whole rulebook (inputs, the change-set shapes, the rules it can
  break, a worked example).
- **`agents/uc-splitter.md`** — the subagent this skill dispatches; JSON out, no vault writes.
