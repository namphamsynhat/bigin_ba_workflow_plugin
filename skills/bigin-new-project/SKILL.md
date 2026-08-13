---
name: bigin-new-project
description: Initiate a new BA project in the current repo — materialize the rulebook and templates into `_bigin/`, capture the engagement config (client, approver, contacts, new vs. ongoing product), and map the existing codebase when there is one. Use once per repo before the first /bigin-intake, and again after a plugin upgrade to refresh the materialized rulebook.
argument-hint: "[client name]"
---

# Bigin New Project

Step 0. Sets up `_bigin/` in the current repo and writes `_bigin/system/project.md` — the config every
later stage reads for the client, the approver, and greenfield vs. existing product.

This stage is what makes every other stage work. The plugin ships its rulebook and templates inside
itself; this skill **copies them into the project** so every later skill and dispatched subagent can
reach them project-relatively. Subagents carry no plugin context, so a path into the install directory
is unreachable to them; `_bigin/conventions/…`, `_bigin/stages/…`, and `_bigin/templates/…` are
reachable to everything.

Like `/bigin-intake`, the config half **records what the human states** — never guess a client name,
approver, or email address. Unknowns stay `<unknown>` and get asked, not inferred. Only two things may
be derived: the git remote (§ 3) and the codebase map (§ 6), both read from the repo rather than from
intent.

## 1. Check what's already there

Read `_bigin/system/project.md` if it exists, and note whether `01-Requirements/FEATURES.md` does.

- **Neither exists** — fresh initiation. Continue through every section.
- **`project.md` exists** — already initiated. Materialize the workspace anyway (§ 2 is safe to repeat,
  and is how a plugin upgrade reaches an existing project), then show the current config and ask
  whether to (a) update specific fields, (b) leave it alone, or (c) re-initiate from scratch. Only (c)
  rewrites `project.md`, only on explicit confirmation, and it still appends to the existing
  `## Changelog` rather than starting a new one.
- **`project.md` exists but `FEATURES.md` is missing** — create it from
  `_bigin/templates/feature-map.md` in either branch. A config with no feature registry is broken:
  `/extract-signal` has nothing to anchor to.

## 2. Materialize the workspace

Copy the workspace template into the repo, then **verify every file landed**. Read the plugin version
from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json` (`version`) to stamp in § 4.

Copy all three directories **whole**, preserving their internal structure — the nesting is what lets a
subagent load one stage file instead of the rulebook:

```
${CLAUDE_PLUGIN_ROOT}/workspace/conventions/  →  _bigin/conventions/
${CLAUDE_PLUGIN_ROOT}/workspace/stages/       →  _bigin/stages/       (incl. extract/, transform/)
${CLAUDE_PLUGIN_ROOT}/workspace/templates/    →  _bigin/templates/
```

Rules for this copy:

- **All three are plugin-owned.** Overwrite every run. They're the shipped rulebook, stage procedures,
  and blank scaffolds, not project data — a project that edited one edited the wrong file (overrides
  belong in `.claude/bigin-ba-workflow-plugin.local.md`, § 4.2). Report the refresh (§ 7) so anyone who
  did edit one finds out.
- **Copy every stage file, not just the ones this project will use.** Which stage files a run reads is
  decided at read time, per signal and per lane; a project that skipped `3-lane-entity.md` because its
  first intake had no entity signal breaks the first run that does.
- **Never touch project data.** `_bigin/system/project.md`, `00-Inbox/`, `01-Requirements/`, `PRD.md`,
  `prototypes/`, `epics.md`. This step writes only the three directories above.
- **Verify, don't assume.** List all three directories, recursively, and confirm the file count matches
  the source. A partial copy surfaces later as a subagent silently unable to read its lane guide —
  reported as a clean run. Anything missing: stop and report rather than continue to § 3.
- **Remove a legacy `_bigin/rules/` — but only after the copy above has verified.** Projects initiated
  on plugin `≤ 1.2.0` have the flat `_bigin/rules/` layout this replaced. Left in place it's a second,
  stale copy of the rulebook at a path that older prose may still cite, so a subagent can read a rule
  that no longer governs. Delete the directory, say so in § 7, and never delete it before the new copy
  is confirmed on disk.

What lands, and who reads it. Nothing reads all of it — each row names its only readers:

| Path | Read by |
|---|---|
| `_bigin/conventions/conventions.md` | every skill and subagent, **named sections only** — see that file's own stage table |
| `_bigin/conventions/paths.md` | any subagent resolving a `{variable}` a stage file refers to |
| `_bigin/stages/extract/2-extraction.md` | `/extract-signal`'s extraction subagents |
| `_bigin/stages/transform/1-foldin.md` | `/bigin-transform-signal` Stage 1 (orchestrator) |
| `_bigin/stages/transform/2-qualification.md`, `3-routing.md` | `/bigin-transform-signal` Stages 2–3 (orchestrator) |
| `_bigin/stages/transform/3-lane-{fr,br,design,entity}.md` | `/bigin-transform-signal`'s per-feature subagents — only the lanes that run |
| `_bigin/stages/transform/4-sync.md`, `5-status.md` | `/bigin-transform-signal` Stages 4–5 (orchestrator) |
| `_bigin/templates/*.md` | whichever skill creates that artifact type, the first time it's needed |

## 3. Gather the engagement config

Take the client name from `$ARGUMENTS` if given. Ask for the rest — use `AskUserQuestion` for the
closed choices, plain questions for the free-text ones:

| Field | How to get it |
|---|---|
| `client` | `$ARGUMENTS`, or ask |
| `approver` / `approver_email` | Ask — the one human who signs off FRs (`/approve-fr` gates on this person) |
| `client_emails` | Ask — every address on the client side that might appear on an intake |
| `team_emails` | Ask — your own team's addresses for this engagement |
| `email_provider` | `AskUserQuestion`: **outlook** (default) or **spark** — which tool `/bigin-intake` pulls client email from |
| `outlook_folder` | `email_provider: outlook` only. Default `["Inbox"]`; ask if client mail lands in a specific folder |
| `meeting_provider` | `AskUserQuestion`: **fathom** (default), **spark**, or **firefly** — which tool `/bigin-intake` pulls transcripts from |
| `project_mode` | `AskUserQuestion`: **new** (greenfield — nothing built yet) or **ongoing** (an existing product this repo contains or accompanies) |
| `codebase_path` | `ongoing` only. Default to the repo root (absolute path); ask if the product lives elsewhere |
| `intake_lookback_days` | Default `14`, no need to ask unless the user raises it |

`client_emails` matters more than it looks: `/bigin-intake`'s sweep **halts** on an empty list, having
no way to tell client correspondence from internal mail. If the addresses aren't to hand, say plainly
that `/bigin-intake direct …` still works and the sweep stays unavailable until the list is filled.

Ask the two provider fields rather than defaulting silently: `/bigin-intake` is forbidden from falling
back to an unconfigured provider, so an unasked field there becomes a run that skips a source without
saying so.

Detect, don't ask: the repo's remote via `git remote -v`. Record as `repo:`, blank if not a git repo.

Ask explicitly: **should `_bigin/` be committed?** Intake files hold verbatim client emails and
transcripts, so it's the user's call. On no, add `_bigin/` to `.gitignore` (create if missing); on yes,
do nothing. Record the answer in `## Notes`. Either way add `.claude/*.local.md` to `.gitignore` —
user-local config, not project data.

## 4. Write the config

1. Instantiate `_bigin/templates/project.md` into `_bigin/system/project.md`, filling frontmatter from
   § 3 plus:

   - `workspace_version` — the plugin version from § 2. A later run compares against it to tell whether
     `_bigin/conventions/` and `_bigin/stages/` are stale.
   - `updated` — today's date.
   - Unsupplied fields stay `<unknown>`; list them in § 7.

   Use the template, don't compose from memory — the template *is* the schema `/bigin-intake` parses,
   and a hand-written variant is how a field it reads goes missing.

2. Scaffold `.claude/bigin-ba-workflow-plugin.local.md` from
   `skills/bigin-new-project/template/settings.local.md`, **only if absent** — never overwrite one a
   project wrote. This is the one place a project may legitimately override plugin behavior (a `Why`
   house style, a standing feature-slug shortcut). It lives in `.claude/` because it configures how
   `/bigin-intake` and `/extract-signal` behave rather than describing the engagement, and ships empty
   — both fall back to built-in defaults per blank section. Don't ask the user to fill it in; just
   mention it in § 7.

## 5. Import a project proposal, if there is one

Ask whether a proposal, scope document, or SOW exists.

- **Yes, with a path** — `Read` it, then add one `proposed` row to `01-Requirements/FEATURES.md` per
  feature it names. Take slugs and names from the document's own wording; don't invent a feature it
  doesn't name, don't merge two it lists separately. Cite the document in each `Sources` cell. Report
  the rows added so wrong slugs get corrected before signals anchor to them — a slug is permanent once
  artifacts reference it.
- **No, or unreadable** — leave `FEATURES.md` as the empty scaffold. `/extract-signal` raises a
  feature-mapping question for the first unanchorable signal and the human mints the row then. This is
  the normal path, not a degraded one.

Only `proposed` rows come from a proposal. `committed`/`built`/`out-of-scope` are human-set
(`_bigin/conventions/conventions.md` § Feature map).

## 6. Map the codebase (`project_mode: ongoing` only)

**Deferred — leave `## Codebase map` empty with its comment, in both modes.** The repo-mapping approach
isn't finalized, so `ongoing` behaves like `new` apart from recording `codebase_path`. Say so in § 7
rather than let the user believe a map was written.

<!-- Planned shape, once the mapping approach is settled:

Read the repo to establish where features will land, so `/bigin-transform-signal` and
`/enrich-feature` can anchor requirements to real code areas instead of inventing them. Look at the
manifest/build files, the top-level source layout, entry points, and the test setup. Then write into
`## Codebase map`:

- **Stack**: <languages, frameworks, notable libraries — as evidenced by manifests, not assumed>
- **Entry points**: <path> — <what it starts>
- **Code areas**: a table of | Slug | Path(s) | What lives here |
- **Tests**: <framework + how to run, if discoverable>
- **Not covered**: <parts of the repo you didn't map, if any>

Rules for that section: code areas are directories, not features — a slug there names a place in the
code (`billing-api`, `web-checkout`) and asserts nothing about what a feature should do; feature
names come from client signals via `/extract-signal`, never from reading code. Only record what you
actually verified; an unclear directory goes under "Not covered" rather than getting a plausible
guess. Keep it to roughly a screen. -->

## 7. Report

Tell the user:

1. **Workspace** — `_bigin/conventions/`, `_bigin/stages/`, and `_bigin/templates/` materialized (or
   refreshed) at version `<version>`, with file count. On a refresh, add three things: that local edits
   to those three directories were overwritten, that
   `.claude/bigin-ba-workflow-plugin.local.md` is where overrides belong instead, and whether a legacy
   `_bigin/rules/` was removed (§ 2).
2. **Config** — paths created or updated, and whether `_bigin/` is tracked or ignored.
3. **Unknowns** — fields still `<unknown>`, editable directly in `_bigin/system/project.md`. Call out an
   empty `client_emails` specifically, with its consequence for the sweep.
4. **Settings** — `.claude/bigin-ba-workflow-plugin.local.md` scaffolded, or already existed and left
   alone.
5. **Features** — `proposed` rows imported from a proposal, if any, so wrong slugs get corrected now.
6. **Codebase map** — for `ongoing`, that mapping is deferred and the section is intentionally empty.
7. **Next step** — `/bigin-intake` to capture the first meeting, email, or note.
