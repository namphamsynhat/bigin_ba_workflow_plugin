---
name: bigin-transform-signal
description: Turn signals extract-signal has already filed onto a Feature Hub's Signal Log (Status new/held) into drafted or updated Functional Requirements (FR) and Business Rules (BR), keep cross-feature Entities (EN) and Business Scenarios (SCN) in sync, and hold every FR/BR change at a written, resumable human-review gate before folding it in. This is the Transform stage of the extract → transform → load pipeline. Use after /extract-signal has filed signals, or when asked to derive FRs/BRs, process the signal backlog, or check whether a feature's staged FR/BR changes have been answered.
argument-hint: "[feature slug, or omit for all pending, or resume]"
disable-model-invocation: true
---

# Bigin Transform Signal

Transforms raw signals (`Status: new`/`held`) on a Feature Hub’s `## Signal Log` into drafted/updated Functional Requirements (FRs) and Business Rules (BRs), while synchronizing cross-feature Entities (ENs) and Business Scenarios (SCNs). Every change goes through a written, resumable human-review gate before integration.

> **Rulebook Reference:** Read `{conventions_reference}` (`references/conventions.md`) before running. This skill provides the execution procedure; `conventions.md` defines the underlying standards (Feedback handling, Feature Hub, and Resumable unattended apply).

---

## Operating Modes & Gates

* **Written Gate (Default/Unattended):** Stages proposals into `## Discussion` and adds `- [ ] Q: ... A:` items to `## Open Questions`. Runs asynchronously across single or multiple features without blocking.
* **Interactive Path:** If a human answers a question inline during conversation, fold it in immediately without creating a written round-trip.
* **Execution Sequence:** On any run/rerun, **Pass 2 (Fold-In)** executes *first* to process newly answered items, followed by **Pass 1 (Stage/Raise)** for new or held signals.

---

## File & Directory Paths

| Variable | Target Path | Description |
| :--- | :--- | :--- |
| `{conventions_reference}` | `references/conventions.md` | Core rulebook & standards |
| `{hub_dir}` | `01-Requirements/_features/<slug>.md` | Feature Hub directory |
| `{requirements_file}` | `01-Requirements/FEATURES.md` | Feature slug registry |
| `{fr_dir}` | `01-Requirements/_frs/FR-<NNN> <Title>.md` | Functional Requirements |
| `{br_dir}` | `01-Requirements/_brs/BR-<NNN> <Title>.md` | Business Rules (defines `fr: []` citations) |
| `{entities_file}` | `01-Requirements/ENTITIES.md` | Proposed entities register |
| `{entity_dir}` | `01-Requirements/_entities/EN-<NNN> <Entity>.md` | Promoted entity specs |
| `{scenarios_file}` | `01-Requirements/SCENARIOS.md` | Cross-feature scenario register (`SCN-###`) |
| `{template_*}` | `skills/bigin-transform-signal/template/*` | Scaffolds (`fr`, `br`, `entity`, `scenario-register`) |

---
## Paths

- `{conventions_reference}`: `references/conventions.md` (plugin root) — the ID scheme, frontmatter
  schema, and artifact conventions this skill implements.
- `{hub_dir}`: `01-Requirements/_features` — one hub per feature slug, `{hub_dir}/<slug>.md`.
- `{requirements_file}`: `01-Requirements/FEATURES.md` — the slug registry.
- `{fr_dir}`: `01-Requirements/_frs` — one file per `FR-<NNN> <Title>.md`.
- `{br_dir}`: `01-Requirements/_brs` — one file per `BR-<NNN> <Title>.md`, always its own file,
  `fr: []` citing the FR(s) it constrains (`[]` if feature-level, not yet tied to one FR).
- `{entities_file}`: `01-Requirements/ENTITIES.md` — `proposed` rows `extract-signal` filed;
  `{entity_dir}`: `01-Requirements/_entities` — promoted `EN-<NNN> <Entity>.md` docs.
- `{scenarios_file}`: `01-Requirements/SCENARIOS.md` — the single `SCN-###` register (one row per
  cross-feature flow, not one file per scenario).
- `{template_fr}` / `{template_br}` / `{template_entity}` / `{template_scenarios}`:
  `skills/bigin-transform-signal/template/{fr,br,entity,scenario-register}.md`.

## Pass 1 — Classify, draft, stage, and raise

Scan every `{hub_dir}/<slug>.md` (or just the one named in `$ARGUMENTS`). Collect Signal Log rows
whose `Status` is `new` or `held` — `held` rows are re-checked every run, since an FR that didn't
exist last time might exist now (a `new`/`held` signal against an existing FR always moves to
`staged`, never rests at `held`, regardless of that FR's own status — hard rule 7). If the combined
worklist is empty, say so and stop.

For each row:

1. **Classify** per `conventions.md` § Signal → artifact mapping: a testable/actionable statement
   → a new/updated `FR-###`; a conditional/policy constraint, feature-level or anchored to one FR,
   → a new/updated `BR-###` (its own file, `fr: []` citing the FR(s) it constrains); a data
   field/entity description → `ENTITIES.md`'s `proposed` row (`extract-signal` already wrote this
   — § Cross-feature sync below is where this skill promotes it); narrative context/reason →
   `## Business goal`/`## Problem & Pain Points` on the FR. Pain-point rows may already exist from
   `extract-signal` too — this pass mirrors them onto the FR, it doesn't recreate them.
2. **New vs. update.** Read the feature hub's `fr:`/`br:` list and the artifact itself before
   deciding "new" — an extension or correction of what's already there is an update to that
   FR/BR, never a duplicate. Create `{fr_dir}/FR-<NNN> <Title>.md` / `{br_dir}/BR-<NNN>
   <Title>.md` from `{template_fr}`/`{template_br}` only when nothing on this feature covers it
   yet. Next id: `Grep` (never a bash `grep`/`awk` pipeline — conventions.md § ID scheme) the
   relevant folder (`{fr_dir}` or `{br_dir}` — each is its own independent sequence) for the
   highest existing number and increment.
3. **Stage.** Write the proposed content into the artifact's `## Discussion` (never straight into
   `## Functional requirements` or the BR's own rule statement), citing the `INT-###` the Signal
   Log row traces to. For an FR, copy that INT note's `attachments:` onto the FR's own
   `attachments:` frontmatter if not already listed. Flip the Signal Log row to `staged`.
4. **Raise, if it needs a decision.** Wording that's genuinely ambiguous, or a signal that
   conflicts with an existing row (§ Feature Hub's conflict handling — cite the row number(s) in
   `Notes`, `Status: conflict`), gets a `- [ ] Q: ... A:` line on the artifact's own
   `## Open Questions` — written per `conventions.md` § Open Questions wording (self-contained,
   plain business language for `owner: client`, one concrete question). If nothing needs a
   decision — the wording is a clean, unambiguous fold candidate — skip straight to folding it in
   now instead of manufacturing a question just to have one.
5. **Set status from the count, last.** Re-count unchecked `## Open Questions` boxes on the
   artifact *after* every write above: `> 0` → `status: needs-clarification`; `0` →
   `status: in-review` (conventions.md § Open Questions ↔ status consistency — never decide this
   earlier in the step and leave it stale).
6. A row that's genuinely unclear even to classify stays `held`, with a note on the hub's
   `## Open Questions / Gates` — never force a classification.

## Pass 2 — Resumable fold-in

Run this first on every invocation, before Pass 1 — it's what makes a rerun useful, and it's what
turns a previously-staged, now-answered FR/BR into something ready for `/enrich-feature`. For every
FR/BR this skill has ever staged a change on (scan `{fr_dir}`/`{br_dir}` for one with a `staged`
Signal Log row pointing at it, or just the artifacts for the feature in `$ARGUMENTS`):

1. **Dedup-check before writing anything.** Does the artifact's `## Changelog` already cite this
   fold-in's `INT-###`, or does the `## Open Questions` line already read as resolved rather than
   merely ticked? If yes, this is a retry of an already-completed apply — do nothing to it, skip
   to step 3.
2. **Genuinely unanswered** (the `A:` line is still blank) → leave it, not eligible yet. Otherwise,
   compose the *entire* change — fold the `## Discussion` entry into `## Functional requirements`
   (FR) or the rule statement (BR), bump `version`, append `## Changelog` — and write the file
   once, atomically. Before that write lands nothing has changed; a kill mid-run leaves it exactly
   where a future run can safely retry.
3. **Reconcile mirrors, unconditionally, every run.** Flip the hub's Signal Log row to `applied` if
   the artifact now shows the fold-in; tick the source INT note's own `## Open Questions` copy if
   the FR/BR's copy is already resolved. Setting an already-correct field again is a no-op, not a
   duplicate — never skip this step just because step 1 said "already done."
4. Re-count the artifact's `## Open Questions` and set `status` last, same rule as Pass 1 step 5.

## Cross-feature sync (Entity + Business Scenario)

Detected inside Pass 1 step 1, applied alongside the FR/BR write — this is the newer half of this
skill and the lighter one; expect it to grow as real cross-feature cases show up.

- **Entity.** A signal defines/extends a field on an `ENTITIES.md` row that an FR/BR now
  references. Promote it: create `{entity_dir}/EN-<NNN> <Entity>.md` from `{template_entity}` if
  it doesn't exist yet, or extend it if it does. A field-level business rule discovered here is
  still its own `{br_dir}` file, never a subsection of the entity doc (conventions.md § Entity
  Data Model) — it cites the entity's fields it governs in its own body. Add/refresh the entity's
  line on every referencing feature's hub `## Entities` section (`- EN-### <Name> (<status>)`).
- **Business Scenario.** A signal describes an end-to-end flow that genuinely crosses feature
  boundaries — a human would narrate it as one story, not "this feature also calls that API."
  Create/update the `SCN-###` row in `{scenarios_file}` (from `{template_scenarios}` if the file
  doesn't exist yet — next id: `Grep` `{scenarios_file}` for the highest `SCN-###`), and add a
  one-line pointer (`- SCN-### <name> (step N of M)`) to every participating feature's hub
  `## Business Scenarios` section.

Most signals touch neither. Don't manufacture a scenario or promote an entity speculatively — both
stay `proposed`/absent until a signal genuinely needs them.

## Report

```text
Pass 2 (fold-in): <N> FR/BR resolved this run — <slug>: FR-### now in-review, ready for /enrich-feature
Pass 1 (stage/raise): <N> FR created, <N> updated, <N> BR created, <N> BR updated — <slug>: FR-### / BR-### (staged, needs-clarification | staged, in-review)
cross-feature: <N> entity promotion(s), <N> scenario(s) touched — or "none this run"
held — no FR/BR yet: <slug> (<N> signal(s)), human decision needed
remaining unanswered: <slug>: FR-###/BR-### — N open question(s), owner client|team
```

## Agent involvement

No subagent dispatch, at least for this first version. `extract-signal` dispatches a fresh `haiku`
subagent per note because that stage is high-volume, mechanical extraction against a tight rule
set. Drafting an FR/BR is the opposite: low volume per run, and genuinely judgment-heavy — deciding
new-vs-update, wording a self-contained question, spotting a cross-feature scenario. The written
gate (§ above) already makes this safe to run unattended across many features without a subagent's
help; the reason to skip one isn't throughput, it's that there's no mechanical, high-volume inner
loop here to offload. Do the classification and drafting directly, the way `/enrich-feature` and
`/approve-fr` already do their judgment calls inline.

Revisit this only if a single run's worklist grows large enough that per-feature batching clearly
helps — `extract-signal`'s `references/agent-dispatch.md` is the template to copy if that becomes
worth it, but don't add it speculatively.

## Additional resources

- **`references/conventions.md`** (plugin root) — the rulebook: ID scheme and numbering, the
  Status vocabulary this skill owns (`held`/`staged`/`applied`/`superseded`), the exact
  `## Open Questions` wording rules, the resumable-apply checkpoint discipline, and § Feedback
  handling's in-place-edit rule (hard rule 7 — approval doesn't freeze an FR).
- **`template/fr.md`** / **`template/br.md`** — scaffolds for a new FR/BR document.
- **`template/entity.md`** — scaffold for promoting an `ENTITIES.md` proposed row into a full
  `EN-###` doc.
- **`template/scenario-register.md`** — scaffold for `01-Requirements/SCENARIOS.md`, created the
  first time a signal needs it.
