---
name: bigin-upgrade-project
description: Compare a materialized project's current rulebook/templates against the plugin version now installed (halting rather than downgrading if the workspace turns out to be newer than the installed plugin), run whatever documented migration procedures apply to what changed, refresh the materialized workspace and the repo-root `CLAUDE.md`'s plugin-owned section, and stamp the project onto the new version. Use after upgrading the plugin, whenever `_bigin/system/project.md`'s `workspace_version` is behind `${CLAUDE_PLUGIN_ROOT}`'s version — instead of guessing whether re-running `/bigin-new-project` alone moved old content forward. Also the way a `CLAUDE.md` instruction change (a new non-negotiable, a routing-rule fix) reaches an already-materialized project without a full `/bigin-new-project` re-run. Built to need no changes itself the next time an artifact type retires, a template gains a section, or a template's frontmatter gains a key: it discovers what to do from "## Adopting an existing <thing>" sections in the stage guides and from template diffs — section headers and frontmatter keys alike — rather than hardcoding any one migration.
argument-hint: "[check]"
disable-model-invocation: true
---

# Bigin Upgrade Project

Answers one question a version bump alone can't: **did upgrading the plugin actually move this
project's own content forward, or only the rulebook?** `/bigin-new-project` refreshes
`_bigin/conventions/`, `_bigin/stages/`, and `_bigin/templates/` on every re-run — but those are the
plugin's own files. A project's *content* (its features, its `01-Requirements/` artifacts) only
moves onto a new artifact model when something runs the migration procedure that change shipped
with, and nothing does that automatically today. This skill is that something.

> **Artifact Standard:** Outputs:
>> **Migrated artifacts** — for every retirement *and every template drift* the diff finds with a
>> documented adoption procedure: new artifacts minted, retired ones stamped as absorbed, added
>> frontmatter keys stamped onto the instance that lacks them, content **staged** for human review,
>> never auto-approved.
>> **A drift report** — template or convention changes the diff finds with **no** documented
>> procedure: named explicitly, changed nothing, left for a human to decide how to handle.
>> **An updated `workspace_version`** in `_bigin/system/project.md`, so the next run's diff starts
>> from where this one left off.
>> **A regenerated `CLAUDE.md`** — the repo-root project agent's delimited section, recomposed from
>> the plugin's current `references/claude-md.md` every run, so an instruction change there reaches
>> this project the same version bump that shipped it.

---

## Non-Negotiable Core Rules

* **Discover migrations, never hardcode one.** The only artifact-specific knowledge this skill is
  allowed to contain is *how to find* a migration procedure (§§ 2–3) — never the procedure itself. A
  procedure lives in the stage guide that introduced the new artifact type, section, or field, as its
  own `## Adopting an existing <thing>` section, where `<thing>` is an ID prefix (`FR`) or the name of
  the artifact a template templates (`project config`, `UX spec`, `Feature Hub`). Baking FR→UC logic,
  or a named frontmatter key, or any future pair directly into this skill defeats the reason it
  exists: it must still work, unmodified, the next time a type retires or a template grows a field.
* **Drift discovered but never run is worse than drift never detected.** § 2 naming a change *and* the
  file that documents its adoption, while § 4 runs nothing, produces a report whose every line is true
  and whose overall message is false: the reader sees a named procedure next to a named file and
  concludes the project is migrated. Every § 3 match is therefore an obligation on § 4 —
  either it ran, or the report says in that same row that it did not and why. There is no third state,
  and "detected, procedure exists" is not a terminal status.
* **No documented procedure → report, never improvise.** A retirement or template change with
  nothing named after it in § 3's scan is drift to name in § 7's report, not a migration to attempt
  from first principles. A best-effort guess at how content should transform is exactly the failure mode
  every other skill in this plugin halts rather than risks (`_bigin/conventions/core.md`
  hard rule: never invent a validation, field, or structure the source didn't state).
* **Stage, never approve.** Every migration this skill runs ends in `draft`-status content and
  `## Discussion` entries, the same human gate as any other UC/BR change
  (`core.md` § Status vocabularies, hard rule 4). This skill mints and
  stages; it never sets `approved`, `enriched`, or `consolidated`, and never folds a `## Discussion`
  entry into `## 1`–`## 6` itself.
* **Idempotent by construction.** Re-running this skill against an already-upgraded project is a
  no-op: nothing here re-migrates a marker that's already stamped, re-mints a UC that already
  `absorbs:` the old id, or re-copies a workspace file already at the target version.
* **`check` mode never writes, and never asks.** `$ARGUMENTS: check` runs §§ 1–3 and produces the
  report a live run would, then stops — no file in `_bigin/` or `01-Requirements/` changes, and no
  question is put to the human that a live run would have to put to them again anyway (§ 4).

---

## Precondition

Requires `_bigin/system/project.md` to exist. Missing → say `/bigin-new-project` must run first
(there is no `workspace_version` to compare from) and stop.

## 1. Read both versions

* **Goal:** establish "current project workflow" and "new version workflow" as two comparable
  snapshots before anything is overwritten.
* **Action:**
  - **Current** — read `_bigin/system/project.md`'s `workspace_version`, and the *currently
    materialized* `core.md` § ID scheme table, plus two things per
    `_bigin/templates/*.md`: its section headers (`Grep '^## '` per file) and its **frontmatter keys**
    (the `^[a-z_]+:` lines above the closing `---`, key names only — values are per-project content,
    not template shape). This is what the project was actually built against — read it **before** § 5
    overwrites it.
  - **New** — read `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`'s `version`, and the same three
    things from `${CLAUDE_PLUGIN_ROOT}/workspace/conventions/core.md` and
    `${CLAUDE_PLUGIN_ROOT}/workspace/templates/*.md`.
* **Rules:**
  - **Compare the two versions as SEMVER, component by component, numerically — never as strings.**
    `"1.10.0"` sorts *before* `"1.6.5"` lexically, so a string comparison reports an upgrade as a
    downgrade at exactly the version where it starts to matter. Then branch on the ordering, three ways:

    ```text
    workspace == plugin  → report "already current" and STOP at § 1. Nothing downstream runs —
                           this is what makes re-running the skill after every session cheap.
    workspace <  plugin  → the ordinary upgrade. Continue to § 2.
    workspace >  plugin  → HALT. Report a DOWNGRADE HAZARD and change nothing.
    ```

  - **The workspace being AHEAD of the plugin is a halt, not a no-op, and not something to "fix" by
    running anyway.** Every step below assumes `${CLAUDE_PLUGIN_ROOT}` holds the *newer* rulebook. If it
    holds an older one, § 2 diffs backwards (reading real additions as retirements), § 5 copies the
    **older** conventions/stages/templates over the newer materialized ones, and § 6 stamps
    `workspace_version` *down*. After that there is nothing left to reconcile from: the only record of
    which rulebook the project's content was built against is the field that just got overwritten.

    ```text
    on workspace > plugin, report and stop:
      workspace_version <a> is NEWER than the installed plugin <b>
      resolved ${CLAUDE_PLUGIN_ROOT}: <the path>
      → almost always a STALE PLUGIN CACHE being resolved instead of the current install.
        Check which install is being resolved, and prune stale cached copies of this plugin.
      → nothing was changed. Re-run once ${CLAUDE_PLUGIN_ROOT} resolves to the newer plugin.
    ```

    A stale cache is not hypothetical: a cached snapshot can be several minor versions behind and
    missing whole skills, while its copy of a skill that *does* exist carries a contract the current
    rulebook explicitly forbids. Copying that over a correct workspace is the single most destructive
    thing any skill in this plugin can do.

  - **`workspace_version` absent or unparseable** → report it and stop. An old project predating the
    field has no comparable baseline, and § 2's diff has nothing to diff *from*; treat it as
    `/bigin-new-project` needing to run to establish one, not as "assume it's old".
  - Use the `Grep` **tool** for every scan in this skill, never a shell pipeline — a silently denied
    pipeline under an unattended run reads as "nothing changed" instead of "the scan didn't happen"
    (same reasoning as the ID-scan rule in `_bigin/conventions/core.md`).

## 2. Diff the two snapshots

* **Goal:** turn "the rulebook changed" into a concrete list of what this project needs done.
* **Action:**
  1. **ID scheme retirements.** Row-by-row, prefix by prefix: a row **Implemented** in the current
     snapshot and **Retired** in the new one is a migration candidate. Note the prefix and, from the
     new row's "replaced by" text, the prefix that replaces it (e.g. `FR` → `UC`).
  2. **ID scheme additions.** A prefix present in the new snapshot with no row at all in the current
     one is new capability, not a migration — note it in § 7's report, nothing to run.
  3. **Template drift**, on two axes, for every template present in both snapshots:
     - **(a) Sections.** Diff its `^## ` section headers. A changed, added, or removed section is
       drift — this skill never rewrites an existing artifact's structure to match a new template on
       its own; that transform isn't safe to assume.
     - **(b) Frontmatter keys.** Diff the key names § 1 captured. A key **added**, **removed**, or
       **renamed** (one key gone and one arrived in the same template, same run) is drift of exactly
       the same standing as a new section — and arguably louder, because the pipeline *parses*
       frontmatter: every skill downstream branches on those keys, so a template key no instance
       carries is a branch reading absent where the rulebook now expects a value. A new `^## ` header
       is prose a reader can skip; a missing key is a default silently taken.

     Either axis firing is drift to carry into § 3. Neither axis is a licence to rewrite an artifact
     here — § 2 only *names* what changed.
* **Rules:**
  - **Diff frontmatter keys with the `Grep` tool, same discipline as every other scan in this skill
    (§ 1's last rule) — never a shell pipeline.** A denied `sed`/`awk` on a frontmatter block returns
    empty, empty diffs to nothing, and nothing reports as "no keys changed" — the one failure mode
    where the skill claims the template is unchanged precisely because it never looked.
  - **A key added to a template is drift; a key the project's own instance merely lacks is the same
    condition, not a lesser one.** The two are indistinguishable by construction: a template gains a
    new key, and every instance materialized before that moment lacks it. So don't try to separate
    "the template changed" from "this project predates the change" — they are one finding, and **the
    adoption section decides what to do about it**, not this skill. This skill's whole contribution is
    noticing the key is new and routing to whoever documented it.
  - **A retirement is only a migration candidate if the project actually has content in the old
    prefix's folder.** A vault with an empty `_frs/` (or none at all) has nothing to migrate — don't
    report it as a pending item.
  - **Compare by prefix, not by section title wording.** Section titles get copyedited across
    versions without meaning anything changed; the ID scheme table's Status column is the signal.

## 3. Discover the migration procedure for each change

* **Goal:** find the documented, runnable procedure for **every** § 2 finding — the ID-prefix
  retirements of § 2.1 *and* the template drift of § 2.3, in one pass — or confirm there isn't one.
* **Action:** `Grep` `${CLAUDE_PLUGIN_ROOT}/workspace/stages/` (the **new** version's stage guides,
  not the currently materialized ones) for `^## Adopting an existing ` — bare, once, no `<thing>`
  appended — and take the hit list as the **inventory of every adoption procedure this plugin version
  ships**. Then match each § 2 finding against that inventory:

  ```text
  a § 2.1 retirement       → match on the retiring ID prefix        e.g. `## Adopting an existing FR`
  a § 2.3 drifted template → match on the name of the artifact it templates, as that inventory
                             spells it — `project.md` is the project config, `ux-spec.md` the UX
                             spec, `feature-hub.md` the Feature Hub
  ```

  Match against what the inventory actually contains; never compose the heading you expect and grep
  for that. A guessed name misses by a word (`config` vs. `project config`) and reports "no procedure"
  for a procedure sitting in the file. A match names: which file owns the procedure, and — read the
  section itself — what marker it stamps to tell an already-migrated instance from one still pending
  (a field on the artifact for a retirement, today FR's `absorbed_by:`; the added key's own presence
  for a config migration).
* **Rules:**
  - **No match, for either kind → that finding moves to the drift report (§ 7) instead of § 4.** Don't
    invent a procedure by analogy to one that does exist (e.g. don't reuse FR's adoption steps for a
    differently-shaped retirement just because both are "old files becoming new files", and don't
    stamp a new frontmatter key with a value nobody documented a source for).
  - **Read the matched section fresh every run.** Its own steps are the spec; this skill's job is
    routing to it, not memorizing a copy that can drift from the source. This is why the grep is for
    the bare heading: the inventory is discovered, so a procedure added next version is found by a
    skill that was never edited to know about it.
  - **A match is a commitment, not a citation.** Every finding that matches here is handed to § 4 and
    accounted for in § 7's report as run, or as explicitly not-run-and-why. Naming the owning file and
    stopping there is the failure mode the Core Rules call out by name.

## 4. Run each discovered migration

Skip this section entirely in `check` mode — report what *would* run instead (§ 7), and **ask the user
nothing**: see the last rule below.

* **Goal:** apply every procedure § 3 matched — whatever kind of finding it came from — across every
  affected instance, without touching anything the procedure doesn't name.
* **Action:** For **every § 3 match**, not only the retirements, first read the matched section and
  sort it by shape, because the two shapes are dispatched differently:

  ```text
  many instances  (a § 2.1 retirement: a folder of FRs, every UX spec, every hub)
      → per-group subagent dispatch, below
  one instance    (a § 2.3 config/single-file migration: `_bigin/system/project.md` gaining a key)
      → the ORCHESTRATOR runs it inline, below. Never dispatched
  ```

  **Many-instance (retirement) migrations:**
  1. Scan the old prefix's folder for instances missing the marker field § 3 identified — those are
     pending; skip anything already marked (idempotency).
  2. Group pending instances the way the procedure expects (§ Adopting an existing FR groups by
     `feature:` — follow whatever grouping the matched procedure itself specifies).
  3. **Dispatch one subagent per group**, pinned to `sonnet` — same write-ownership discipline
     `/bigin-transform-signal` uses for the same reason (one legitimate writer per destination
     artifact). This is applying a procedure someone else already wrote against a named set of files,
     not deciding anything, so it does not need the session default tier. Give the subagent the pending
     instances and one instruction: **run the matched section's steps, exactly, and nothing beyond
     them.**
  4. Refresh whatever mirrors the matched procedure names as its own maintenance contract (e.g. a
     feature hub's `## Use Cases` / `uc:` for the FR→UC case) — read that from the procedure, not
     assumed.

  **Single-instance (config) migrations — run inline, by the orchestrator:**
  1. Check the one file the procedure names for the marker (for an added frontmatter key, the marker
     *is* the key). Present at any value → skip entirely, report it as already adopted. This is the
     idempotency rule in its config form: the section fires on an absent key, never on a value it
     disagrees with.
  2. Run the section's steps as written. Where it says to **ask** — a value only a human can state —
     ask, once, with `AskUserQuestion`, exactly the question and options it specifies. Where it names
     a fallback for the no-human case, that fallback is *its* branch for a headless caller, not this
     one: a `/bigin-upgrade-project` run has a human at the terminal by definition, so the asked
     branch is the one that applies here.
  3. Stamp what the answer says, plus whatever changelog line the section names, and nothing else.
* **Rules:**
  - **A single-instance migration is never dispatched, and the reason is not size — it is that a
    subagent cannot ask.** The "one subagent per group, pinned to `sonnet`" rule above exists for
    concurrent-writer safety across many files; one file is not a concurrency hazard, and sending a
    question-asking procedure to a context with no user attached converts the one question into a
    guessed value that then reads as settled fact to every skill downstream. Dispatch buys nothing
    here and costs the only thing that makes the migration correct.
  - **One subagent never migrates two groups.** Cross-group writes are exactly the concurrent-writer
    hazard the underlying procedures are already written to avoid.
  - **A migration that can't cleanly place some content stages what it can and raises a question for
    the rest**, per whatever the matched procedure itself allows — never blocks the whole group on
    one unclear line.
  - **Never touch the old artifact's body, and never exceed what the procedure names.** Every adoption
    procedure in this plugin only adds a marker field (or one frontmatter key) and a changelog line to
    what it migrates; if a matched procedure does more than that, that is a bug in the procedure, not
    license for this skill to go further itself. A config migration in particular touches the named
    key and the `## Changelog` — no other field of `_bigin/system/project.md`, whatever else looks
    stale in it.
  - **`check` mode reports, and asks nothing.** Not "asks and then doesn't write" — a question posed in
    `check` mode extracts a decision from the human and then throws it away, so the real run asks the
    same question again and the second answer may not match the first. `check` names the question that
    a live run *would* put to them, and leaves it unasked.

## 5. Refresh the materialized workspace

* **Goal:** land the new version's rulebook and templates now that whatever needed the *old*
  snapshot (§§ 1–4) has read it.
* **Action:** Same mechanical copy `/bigin-new-project` § 2 already performs —
  `${CLAUDE_PLUGIN_ROOT}/workspace/{conventions,stages,templates}/` → `_bigin/{conventions,stages,templates}/`,
  whole directories, then verify the file count matches the source.
* **Rules:**
  - Identical to `/bigin-new-project` § 2's rules (report the refresh, copy every stage file
    regardless of whether this project uses it yet). This skill doesn't duplicate that section's
    authority over the copy — it's the same operation, run from here because here is where the
    before/after diff also happens.
  - **Prune stage files the new version no longer has.** The copy overwrites and adds; it never
    removes. So a stage guide that was **renamed** between versions leaves its old copy behind, and
    `_bigin/stages/design/` ends up holding both `5-close.md` (a stale file calling itself "Stage 5 —
    Close") and `6-close.md` (the real Stage 5's successor) — two files claiming one stage number,
    with nothing marking which is live. After the copy, list each `_bigin/stages/*/` against its
    `${CLAUDE_PLUGIN_ROOT}/workspace/stages/*/` source and **delete every `.md` the source does not
    have**, naming each deletion in § 6's report. These are plugin-owned files with no project content
    in them — the same class the copy just overwrote wholesale — so removing one loses nothing a human
    wrote. Do not extend this prune to `_bigin/conventions/` or `_bigin/templates/` without the same
    reasoning: a template a project still has content instantiated from is not dead just because the
    plugin stopped shipping it.
    - **1.9 → 1.10 is the sharpest case yet.** `design/2-system.md` became `design/2-navigation.md`,
      `design/4-verify.md` became `design/5-verify.md`, `design/4-flow-review.md` is new, and
      `design/5-prompt.md` was **deleted outright** — the prototype-prompt blocks are gone from the
      pipeline. An upgrade that skips the prune leaves a project reading a stale "Stage 2 — The
      design system", which tells it to seed tokens nothing will ever cite, and a stale "Stage 5 —
      The prototype prompts", which tells it to write blocks Stage 6 check 7 now blocks on. Both
      files look authoritative and neither is live.
      (The earlier 1.8 → 1.9 rename — `design/4-prompt.md`/`design/5-close.md` becoming
      `design/5-prompt.md`/`design/6-close.md` — is the same class, one version back.)
    - **1.8.8 split `_bigin/conventions/` and needs no prune.** `conventions.md` (1,660 lines) and
      `design-conventions.md` (806) each became a short **map** plus one file per concern —
      `core.md`, `use-case.md`, `feature-hub.md`, `intake.md`, `questions.md`, `registers.md`,
      `runtime.md`, and the seven `design-*.md`. Every section moved **verbatim**; nothing was
      rewritten or dropped. The whole-directory copy handles it on its own: the two originals are
      overwritten with their maps and the fourteen new files land beside them, so there is nothing
      stale to delete. Say in § 6's report that the rulebook is now per-concern and that a stage
      loads only the files its `SKILL.md` names — a project whose own notes tell a BA to "read
      conventions.md § Feature Hub" is pointing at a map now, not at the rule.
  - **This copy runs strictly after § 4, and § 4's inputs are why.** § 1 takes its "current" snapshot
    of `_bigin/templates/*.md` — section headers *and* frontmatter keys — before anything is
    overwritten, and § 4 then reads a template's currently *materialized* state again to decide what a
    procedure still has to do. This copy destroys both readings: run it first and the old and new
    snapshots are the same files, § 2 diffs a template against itself, finds no drift on either axis,
    and § 4 correctly runs nothing — an upgrade that reports clean because the evidence was
    overwritten before it was read. The ordering is the mechanism, not a preference.

### 5b. Regenerate the project agent (`CLAUDE.md`)

* **Goal:** the repo-root `CLAUDE.md`'s plugin-owned delimited section is exactly as stale as
  `_bigin/conventions/` was before § 5 — it's the same "plugin-owned, refreshed every run" class of
  file, and an instruction added to it (a routing rule, a non-negotiable) is otherwise invisible to
  every already-materialized project until someone happens to re-run `/bigin-new-project` in full.
  This step is what makes that propagate on an ordinary version bump instead.
* **Action:** Read `${CLAUDE_PLUGIN_ROOT}/skills/bigin-new-project/references/claude-md.md` and run
  its § "Action" exactly as `/bigin-new-project` § 5.4 does: locate the
  `<!-- BEGIN bigin-ba-workflow-plugin --> ... <!-- END bigin-ba-workflow-plugin -->` markers in the
  repo-root `CLAUDE.md` and replace only what's between them with the freshly composed section
  (client/engagement facts pulled from the *current* `_bigin/system/project.md`, not the pre-upgrade
  snapshot — this is regeneration, not a diff). No markers found in an existing file → append the
  section rather than guessing where it belongs. No `CLAUDE.md` at all → write one whose whole body
  is that delimited section, same as a fresh `/bigin-new-project` run.
* **Rules:**
  - **Runs every time, unconditionally** — unlike §§ 2–4, this has no "already current" skip. There is
    no cheap way to tell whether `claude-md.md`'s guidance changed this version, and re-composing the
    section is idempotent (same inputs → same output), so checking first would cost more than just
    doing it.
  - **Never touch anything outside the markers.** A pre-existing codebase `CLAUDE.md` (common on
    `ongoing`) keeps every line it had; this step only ever rewrites its own delimited region, same
    discipline as `/bigin-new-project` § 5.4.
  - **`check` mode reports "would regenerate," never writes** — same as § 4.
  - **Runs before § 6 stamps the version**, so a kill mid-run still leaves `workspace_version` at the
    old value and a re-run redoes this step rather than skipping it as already-done.

## 6. Stamp the version

* **Action:** Set `_bigin/system/project.md`'s `workspace_version` to the new plugin version and
  `updated` to today. Append one `## Changelog` line: date, old → new version, what migrated (prefix
  counts, and any frontmatter key stamped with the value it took), what's flagged as drift with no
  procedure. A config migration § 4 ran inline already wrote its own `## Changelog` line, per its
  procedure — don't restate it, just don't omit the key from this line's summary either.
* **Rules:** This is the last write of a live run — everything in §§ 2–5b must be settled first, so a
  kill mid-run leaves `workspace_version` at the *old* value and a re-run correctly sees the upgrade
  as still pending rather than silently skipping it.

## 7. Report

```text
header    workspace_version <old> → <new> · "already current" · or "HALTED: workspace <a> is newer
          than plugin <b> — <resolved ${CLAUDE_PLUGIN_ROOT}>, likely a stale cache; nothing changed"
migrated  one row per § 3 match, in whichever of the two shapes fits it:
          | Prefix | → | Instances | UC/BR/etc. ids minted | Staged, needs review |
          | Template/file | Key or section adopted | Value stamped (stated | defaulted) | Procedure |
          A § 3 match that did NOT run belongs here too, in its own shape's row, with the reason in
          place of the result — never dropped, and never left implied by the drift table
drift     | What changed | Why nothing ran | What a human should decide |
refresh   file counts for conventions/ stages/ templates/, same shape as /bigin-new-project § 8
          pruned    <N> stale stage file(s) removed, by name (0 is the normal result)
agent     CLAUDE.md: created | merged into existing file | regenerated (delimited section only)
next      point at /bigin-transform-signal (or the relevant review skill) for every id in the
          "migrated" table's Staged column — this run staged content, it approved nothing
```

Every § 3 match appears in `migrated`; only findings with **no** matched procedure appear in `drift`.
A config stamp is a project-wide decision and reports as one — a run that put a one-off question to
the human, stamped the answer into the config, and then said nothing about it in `migrated` has
changed the file every other skill reads as settled fact, invisibly.

`check` mode prints `migrated` as "would migrate" — naming, for a single-instance migration, the
question a live run would ask and the file it would stamp, without asking it — and `agent` as "would
regenerate," then stops before either actually runs (§§ 4, 5b) or `next` is computed.

## Paths

Reuses `_bigin/conventions/paths.md`'s `{variable}` table in full — this skill introduces none of
its own. `{fr_dir}`, `{uc_dir}`, `{stages_dir}`, `{template_*}` all resolve there.
