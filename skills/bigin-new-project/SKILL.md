---
name: bigin-new-project
description: Initiate a new BA project in the current repo — materialize the rulebook and templates into `_bigin/`, capture the engagement config (client, approver, contacts, new vs. ongoing product), map the existing codebase when there is one, and verify the configured email/meeting providers are reachable, installing a missing MCP server where an install command is known. Use once per repo before the first /bigin-intake, and again after a plugin upgrade to refresh the materialized rulebook or re-check provider access.
argument-hint: "[client name]"
---

# Bigin New Project

Step 0. Sets up `_bigin/` in the current repo and writes `_bigin/system/project.md` — the config every
later stage reads for the client, the approver, and greenfield vs. existing product — then checks that
the providers that config names can actually be reached (§ 7).

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
  belong in `.claude/bigin-ba-workflow-plugin.local.md`, § 4.2). Report the refresh (§ 8) so anyone who
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
  that no longer governs. Delete the directory, say so in § 8, and never delete it before the new copy
  is confirmed on disk.

What lands, and who reads it. Nothing reads all of it — each row names its only readers:

| Path | Read by |
|---|---|
| `_bigin/conventions/conventions.md` | every skill and subagent, **named sections only** — see that file's own stage table |
| `_bigin/conventions/paths.md` | any subagent resolving a `{variable}` a stage file refers to |
| `_bigin/stages/extract/2-extraction.md` | `/extract-signal`'s extraction subagent — that one only |
| `_bigin/stages/extract/3-filing.md` | `/extract-signal`'s filing subagent — that one only |
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
   - Unsupplied fields stay `<unknown>`; list them in § 8.

   Use the template, don't compose from memory — the template *is* the schema `/bigin-intake` parses,
   and a hand-written variant is how a field it reads goes missing.

2. Scaffold `.claude/bigin-ba-workflow-plugin.local.md` from
   `skills/bigin-new-project/template/settings.local.md`, **only if absent** — never overwrite one a
   project wrote. This is the one place a project may legitimately override plugin behavior (a `Why`
   house style, a standing feature-slug shortcut). It lives in `.claude/` because it configures how
   `/bigin-intake` and `/extract-signal` behave rather than describing the engagement, and ships empty
   — both fall back to built-in defaults per blank section. Don't ask the user to fill it in; just
   mention it in § 8.

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
isn't finalized, so `ongoing` behaves like `new` apart from recording `codebase_path`. Say so in § 8
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

## 7. Check the configured providers are actually reachable

The two provider fields written in § 4 name tools this repo doesn't own. `/bigin-intake` Mode B has its
own gate and will refuse to sweep against an unreachable provider — but it fails at the moment a BA
wanted a sweep, days later, having already typed the command. This step moves that discovery to
initiation, where it costs nothing to fix.

**Check only the two providers this project selected.** Probing all five wastes turns and reports
problems with tools nobody configured.

**Never block on this step.** A provider gap doesn't invalidate the config — `/bigin-intake direct …`
works without any provider at all. Record the state, remedy what's remedyable, report the rest, finish
the run.

### 7.1 Probe

Run `claude mcp list` **once** and reuse its output for both providers — it reports every configured
server with a health state, which is the whole check for an MCP provider. Then resolve each provider:

| Provider | Kind | Reachable means | Tools `/bigin-intake` calls |
|---|---|---|---|
| `outlook` | MCP (local stdio) | a server row whose name contains `outlook`, state `✔ Connected` | `list_emails`, `search_emails`, `get_email`, `list_attachments`, `download_attachment` |
| `fathom` | MCP (remote HTTP) | a row matching `fathom`, state `✔ Connected` | `list_meetings`, `get_meeting_transcript`, `get_recording_by_url` |
| `firefly` | MCP (remote) | a row matching `firefl`, state `✔ Connected` | its list-meetings and transcript equivalents |
| `spark` | CLI binary | `command -v spark` resolves | `spark emails`, `spark search`, `spark thread`, `spark meetings` |

Match server rows **by substring, case-insensitively** — never by an exact name. The same provider is
`outlook`, `claude.ai Microsoft 365`, or `plugin:foo:outlook` depending on how it was added, and an
exact-name check reports a connected server as missing.

For a `✔ Connected` MCP row, also confirm the tools above are actually exposed to this session (a
connected server with a different toolset is a different integration wearing the right name). Missing
tools are a mismatch, not a connection failure — report them, don't reinstall.

### 7.2 Remedy by state — install is the fix for exactly one of them

"Not available" is four different problems. Applying the install remedy to the wrong one wastes a run at
best and overwrites working config at worst.

| State | What it means | Remedy | Automatic? |
|---|---|---|---|
| `✔ Connected`, tools present | Working | none | — |
| `✔ Connected`, expected tools absent | Name collision or version skew | Report the tools you looked for and what the server exposes instead. Never reinstall over a connected server | no |
| **Not configured at all** — no matching row | Genuinely missing | § 7.3 — install it | **yes** |
| `! Needs authentication` | Configured, unauthorized | § 7.4 — hand off to the user | no |
| `✘ Failed to connect` | Configured, endpoint down or misconfigured | Re-run `claude mcp list` once. Still failing → report the error text verbatim | retry only |

A missing CLI binary (`spark`) is the "not configured" row, and § 7.3's rule about unknown installers
applies to it directly.

### 7.3 Install a missing provider

Run the install for a provider in the **not configured** state only. Then re-run `claude mcp list` and
re-classify — an install that lands typically arrives in `! Needs authentication`, not `✔ Connected`,
so § 7.4 usually follows.

**Only from this table. Never improvise an install command.**

| Missing | Command | Then |
|---|---|---|
| `fathom` | `claude mcp add --transport http fathom https://api.fathom.ai/mcp` | § 7.4 — remote connectors need authorizing |
| `outlook`, when the server binary is already on `PATH` | `claude mcp add outlook -- <the path `command -v` resolved>` | re-check; a local stdio server usually lands `✔ Connected` |
| `outlook`, binary absent · `spark` · `firefly` | **none — stop and report** | § 7.5 |

The last row is the common case, and guessing is worse than reporting it. A package name, tap, or
registry entry this skill hasn't been given is a guess, and a wrong `brew install`/`npm i -g` either
fails noisily or installs something that isn't the provider. Name the exact missing binary or server,
say no install command is pinned for it, and let the user supply one.

Two hard limits on anything run here:

- **`claude mcp add` and nothing else.** It writes MCP config and is undone by `claude mcp remove`. A
  package manager mutates the machine outside this repo — that needs the user's explicit go-ahead, in
  their own words, for that specific command.
- **Never `sudo`, and never re-add a server that already has a row.** Re-adding a configured server
  replaces working config with a default, which turns an auth problem into an auth problem *plus* a lost
  transport setting.

Report every command run, verbatim, in § 8.

### 7.4 When a provider needs authorization

OAuth needs a browser and a human. **This step cannot complete it, and must not try.** Tell the user
what to do and move on:

- **A claude.ai connector** (Fathom, Microsoft 365, Gmail — a remote `https://…/mcp` row) — authorize it
  in claude.ai connector settings.
- **Any other MCP server** — run `/mcp` in an interactive Claude Code session, or `claude mcp` from the
  terminal.

**Never ask the user for a token, an authorization code, a client secret, or a callback URL,** and never
offer to paste one on their behalf. Authorization happens in their browser, not in this conversation.

### 7.5 Record the outcome

Write the result into `_bigin/system/project.md`'s `## Provider readiness` section — a dated line per
provider, so a later `/bigin-intake` failure has a checked-once baseline to compare against instead of
re-probing blind:

```markdown
## Provider readiness
<!-- Written by /bigin-new-project § 7. A snapshot, not a gate — /bigin-intake re-checks at sweep time. -->
- email_provider: outlook — ✔ connected (2026-08-13)
- meeting_provider: fathom — ! needs authentication: authorize in claude.ai connector settings (2026-08-13)
```

It's a snapshot and it goes stale — a connector can be revoked the next day. `/bigin-intake` still runs
its own pre-flight check; this never replaces it.

## 8. Report

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
7. **Providers** — one line per configured provider, its state, and what happened (§ 7). List every
   command this run executed, verbatim. For anything still unresolved, give the exact next action —
   "authorize Fathom in claude.ai connector settings", "install the `spark` CLI and re-run this" — not
   "provider unavailable". An unactionable warning gets ignored until the first failed sweep.
8. **Next step** — `/bigin-intake` to capture the first meeting, email, or note. If a provider is
   unresolved, say plainly that `/bigin-intake direct …` works regardless and only Mode B's sweep is
   affected.
