---
name: bigin-upgrade-project
description: Compare a materialized project's current rulebook/templates against the plugin version now installed, run whatever documented migration procedures apply to what changed, refresh the materialized workspace, and stamp the project onto the new version. Use after upgrading the plugin, whenever `_bigin/system/project.md`'s `workspace_version` is behind `${CLAUDE_PLUGIN_ROOT}`'s version — instead of guessing whether re-running `/bigin-new-project` alone moved old content forward. Built to need no changes itself the next time an artifact type retires or a template's shape changes: it discovers what to do from "## Adopting an existing <PREFIX>" sections in the stage guides and from template diffs, rather than hardcoding any one migration.
argument-hint: "[check]"
---

# Bigin Upgrade Project

Answers one question a version bump alone can't: **did upgrading the plugin actually move this
project's own content forward, or only the rulebook?** `/bigin-new-project` refreshes
`_bigin/conventions/`, `_bigin/stages/`, and `_bigin/templates/` on every re-run — but those are the
plugin's own files. A project's *content* (its features, its `01-Requirements/` artifacts) only
moves onto a new artifact model when something runs the migration procedure that change shipped
with, and nothing does that automatically today. This skill is that something.

> **Artifact Standard:** Outputs:
>> **Migrated artifacts** — for every retirement the diff finds with a documented adoption
>> procedure: new artifacts minted, retired ones stamped as absorbed, content **staged** for human
>> review, never auto-approved.
>> **A drift report** — template or convention changes the diff finds with **no** documented
>> procedure: named explicitly, changed nothing, left for a human to decide how to handle.
>> **An updated `workspace_version`** in `_bigin/system/project.md`, so the next run's diff starts
>> from where this one left off.

---

## Non-Negotiable Core Rules

* **Discover migrations, never hardcode one.** The only artifact-specific knowledge this skill is
  allowed to contain is *how to find* a migration procedure (§ 2) — never the procedure itself. A
  procedure lives in the stage guide that introduced the new artifact type, as its own
  `## Adopting an existing <PREFIX>` section. Baking FR→UC logic (or any future pair) directly into
  this skill defeats the reason it exists: it must still work, unmodified, the next time a type
  retires.
* **No documented procedure → report, never improvise.** A retirement or template change with
  nothing named after it in § 2's scan is drift to name in § 5, not a migration to attempt from
  first principles. A best-effort guess at how content should transform is exactly the failure mode
  every other skill in this plugin halts rather than risks (`_bigin/conventions/conventions.md`
  hard rule: never invent a validation, field, or structure the source didn't state).
* **Stage, never approve.** Every migration this skill runs ends in `draft`-status content and
  `## Discussion` entries, the same human gate as any other UC/BR change
  (`_bigin/conventions/conventions.md` § Status vocabularies, hard rule 4). This skill mints and
  stages; it never sets `approved`, `enriched`, or `consolidated`, and never folds a `## Discussion`
  entry into `## 1`–`## 6` itself.
* **Idempotent by construction.** Re-running this skill against an already-upgraded project is a
  no-op: nothing here re-migrates a marker that's already stamped, re-mints a UC that already
  `absorbs:` the old id, or re-copies a workspace file already at the target version.
* **`check` mode never writes.** `$ARGUMENTS: check` runs §§ 1–3 and produces the report a live run
  would, then stops — no file in `_bigin/` or `01-Requirements/` changes.

---

## Precondition

Requires `_bigin/system/project.md` to exist. Missing → say `/bigin-new-project` must run first
(there is no `workspace_version` to compare from) and stop.

## 1. Read both versions

* **Goal:** establish "current project workflow" and "new version workflow" as two comparable
  snapshots before anything is overwritten.
* **Action:**
  - **Current** — read `_bigin/system/project.md`'s `workspace_version`, and the *currently
    materialized* `_bigin/conventions/conventions.md` § ID scheme table and `_bigin/templates/*.md`
    section headers (`Grep '^## '` per file). This is what the project was actually built against —
    read it **before** § 4 overwrites it.
  - **New** — read `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`'s `version`, and the same two
    things from `${CLAUDE_PLUGIN_ROOT}/workspace/conventions/conventions.md` and
    `${CLAUDE_PLUGIN_ROOT}/workspace/templates/*.md`.
* **Rules:**
  - **`workspace_version` equal to the plugin version → report "already current" and stop at § 1.**
    Nothing downstream runs — this is what makes re-running the skill after every session cheap.
  - Use the `Grep` **tool** for every scan in this skill, never a shell pipeline — a silently denied
    pipeline under an unattended run reads as "nothing changed" instead of "the scan didn't happen"
    (same reasoning as the ID-scan rule in `_bigin/conventions/conventions.md`).

## 2. Diff the two snapshots

* **Goal:** turn "the rulebook changed" into a concrete list of what this project needs done.
* **Action:**
  1. **ID scheme retirements.** Row-by-row, prefix by prefix: a row **Implemented** in the current
     snapshot and **Retired** in the new one is a migration candidate. Note the prefix and, from the
     new row's "replaced by" text, the prefix that replaces it (e.g. `FR` → `UC`).
  2. **ID scheme additions.** A prefix present in the new snapshot with no row at all in the current
     one is new capability, not a migration — note it for § 5, nothing to run.
  3. **Template drift.** For every template present in both snapshots, diff its `^## ` section
     headers. A changed, added, or removed section is drift to report (§ 5) — this skill never
     rewrites an existing artifact's structure to match a new template on its own; that transform
     isn't safe to assume.
* **Rules:**
  - **A retirement is only a migration candidate if the project actually has content in the old
    prefix's folder.** A vault with an empty `_frs/` (or none at all) has nothing to migrate — don't
    report it as a pending item.
  - **Compare by prefix, not by section title wording.** Section titles get copyedited across
    versions without meaning anything changed; the ID scheme table's Status column is the signal.

## 3. Discover the migration procedure for each retirement

* **Goal:** find the documented, runnable procedure for each candidate from § 2.1, or confirm there
  isn't one.
* **Action:** `Grep` `${CLAUDE_PLUGIN_ROOT}/workspace/stages/` (the **new** version's stage guides,
  not the currently materialized ones) for `## Adopting an existing <PREFIX>`, one prefix per
  retirement found in § 2.1. A match names: which file owns the procedure, and — read the section
  itself — what marker field it stamps on a migrated artifact (today, FR's is `absorbed_by:`) to
  tell an already-migrated instance from one still pending.
* **Rules:**
  - **No match for a retirement in § 2.1 → that retirement moves to the drift report (§ 5) instead
    of § 4.** Don't invent a procedure by analogy to one that does exist (e.g. don't reuse FR's
    adoption steps for a differently-shaped retirement just because both are "old files becoming
    new files").
  - **Read the matched section fresh every run.** Its own steps are the spec; this skill's job is
    routing to it, not memorizing a copy that can drift from the source.

## 4. Run each discovered migration

Skip this section entirely in `check` mode — report what *would* run instead (§ 5).

* **Goal:** apply every procedure § 3 found, across every affected instance, without touching
  anything the procedure doesn't name.
* **Action:** For each retirement with a matched procedure:
  1. Scan the old prefix's folder for instances missing the marker field § 3 identified — those are
     pending; skip anything already marked (idempotency).
  2. Group pending instances the way the procedure expects (§ Adopting an existing FR groups by
     `feature:` — follow whatever grouping the matched procedure itself specifies).
  3. **Dispatch one subagent per group** — same write-ownership discipline `/bigin-transform-signal`
     uses for the same reason (one legitimate writer per destination artifact). Give the subagent
     the pending instances and one instruction: **run the matched section's steps, exactly, and
     nothing beyond them.**
  4. Refresh whatever mirrors the matched procedure names as its own maintenance contract (e.g. a
     feature hub's `## Use Cases` / `uc:` for the FR→UC case) — read that from the procedure, not
     assumed.
* **Rules:**
  - **One subagent never migrates two groups.** Cross-group writes are exactly the concurrent-writer
    hazard the underlying procedures are already written to avoid.
  - **A migration that can't cleanly place some content stages what it can and raises a question for
    the rest**, per whatever the matched procedure itself allows — never blocks the whole group on
    one unclear line.
  - **Never touch the old artifact's body.** Every adoption procedure in this plugin only adds a
    marker field and a changelog line to what it migrates from; if a matched procedure does more
    than that, that is a bug in the procedure, not license for this skill to go further itself.

## 5. Refresh the materialized workspace

* **Goal:** land the new version's rulebook and templates now that whatever needed the *old*
  snapshot (§§ 1–4) has read it.
* **Action:** Same mechanical copy `/bigin-new-project` § 2 already performs —
  `${CLAUDE_PLUGIN_ROOT}/workspace/{conventions,stages,templates}/` → `_bigin/{conventions,stages,templates}/`,
  whole directories, then verify the file count matches the source.
* **Rules:** Identical to `/bigin-new-project` § 2's rules (report the refresh, copy every stage
  file regardless of whether this project uses it yet). This skill doesn't duplicate that section's
  authority over the copy — it's the same operation, run from here because here is where the
  before/after diff also happens.

## 6. Stamp the version

* **Action:** Set `_bigin/system/project.md`'s `workspace_version` to the new plugin version and
  `updated` to today. Append one `## Changelog` line: date, old → new version, what migrated
  (prefix counts), what's flagged as drift with no procedure.
* **Rules:** This is the last write of a live run — everything in §§ 2–5 must be settled first, so a
  kill mid-run leaves `workspace_version` at the *old* value and a re-run correctly sees the upgrade
  as still pending rather than silently skipping it.

## 7. Report

```text
header    workspace_version <old> → <new> (or "already current" if § 1 stopped here)
migrated  | Prefix | → | Instances | UC/BR/etc. ids minted | Staged, needs review |
drift     | What changed | Why nothing ran | What a human should decide |
refresh   file counts for conventions/ stages/ templates/, same shape as /bigin-new-project § 8
next      point at /bigin-transform-signal (or the relevant review skill) for every id in the
          "migrated" table's Staged column — this run staged content, it approved nothing
```

`check` mode prints `migrated` as "would migrate" and stops before `refresh`/`next`.

## Paths

Reuses `_bigin/conventions/paths.md`'s `{variable}` table in full — this skill introduces none of
its own. `{fr_dir}`, `{uc_dir}`, `{stages_dir}`, `{template_*}` all resolve there.
