---
name: bigin-new-project
description: Initiate a new BA project in the current repo — materialize the rulebook and templates into `_bigin/`, capture the engagement config (client, approver, contacts, new vs. ongoing product), import a proposal or, for a greenfield project with none yet, ask what's being built and run domain research on it, materialize a repo-root CLAUDE.md as the project's standing agent brief, map the existing codebase when there is one, and verify the configured email/meeting providers are reachable, installing a missing MCP server where an install command is known. Use once per repo before the first /bigin-intake, and again after a plugin upgrade to refresh the materialized rulebook, regenerate CLAUDE.md, or re-check provider access.
argument-hint: "[client name]"
---

# Bigin New Project

Step 0. Sets up `_bigin/` in the current repo, writes the config every later stage reads, and checks
that the providers that config names can actually be reached.

The plugin ships its rulebook and templates inside itself; this skill **copies them into the project**
so every later skill and dispatched subagent can reach them project-relatively. Subagents carry no
plugin context, so a path into the install directory is unreachable to them.

> **Artifact Standard:** Outputs:
>> **The materialized workspace** — `_bigin/conventions/`, `_bigin/stages/`, `_bigin/templates/`: plugin-owned, overwritten every run, reachable to every subagent.
>> **The engagement config** — `_bigin/system/project.md`: client, approver, contacts, providers, greenfield vs. ongoing, plus the project brief, domain-research pointer, and provider-readiness snapshot.
>> **The project agent** — repo-root `CLAUDE.md`: a delimited, plugin-owned section orienting any Claude Code session to the engagement, the workspace map, and the skill sequence, regenerated every run.

---

## Non-Negotiable Core Rules

* **Record, never guess:** client name, approver, and email addresses come from the human. Unknowns stay `<unknown>` and get asked. Only the git remote (§ 3) and the codebase map (§ 6) may be derived, both read from the repo rather than from intent.
* **Plugin-owned vs. project data:** overwrite `_bigin/{conventions,stages,templates}/` every run; never touch `_bigin/system/project.md`, `00-Inbox/`, `01-Requirements/`, `PRD.md`, `prototypes/`, `epics.md`. Project overrides belong in `.claude/bigin-ba-workflow-plugin.local.md`. `CLAUDE.md` is a special case — see § 5.4: only the plugin's own delimited section inside it is overwritten; whatever else is in that file, including a pre-existing codebase CLAUDE.md, is never touched.
* **Verify, don't assume:** a partial copy surfaces later as a subagent silently unable to read its lane guide — reported as a clean run. Confirm the file count before continuing.
* **Use the template, not memory:** `_bigin/templates/project.md` *is* the schema `/bigin-intake` parses. A hand-written variant is how a field it reads goes missing.
* **Never improvise an install:** § 7.3's table or nothing. `claude mcp add` only, never `sudo`, never re-add a server that already has a row.
* **Never handle credentials:** OAuth needs a browser and a human. Never ask for a token, authorization code, client secret, or callback URL.
* **Providers never block:** a provider gap doesn't invalidate the config — record the state, remedy what's remedyable, report the rest, finish the run.

---

## Execution order

| § | Section | Runs when |
|---|---|---|
| 1 | Check what's already there | every run |
| 2 | Materialize the workspace | every run |
| 3–4 | Gather and write the engagement config | fresh initiation, or an explicit re-initiate |
| 5.1–5.3 | Import a proposal, capture the brief, research the domain | § 5.3 on `project_mode: new` only |
| 5.4 | Materialize the project agent (`CLAUDE.md`) | every run |
| 6 | Map the codebase | `ongoing` only — currently deferred |
| 7 | Check the configured providers | every run |
| 8 | Report | every run |

## 1. Check what's already there

* **Goal:** decide whether this is a fresh initiation, a plugin-upgrade refresh, or a config edit.
* **Action:** Read `_bigin/system/project.md` if it exists, and note whether `01-Requirements/FEATURES.md` does.

  | State | What to do |
  |---|---|
  | Neither exists | Fresh initiation — continue through every section |
  | `project.md` exists | Already initiated. Materialize anyway (§ 2 is safe to repeat, and is how a plugin upgrade reaches an existing project), then show the current config and ask whether to (a) update specific fields, (b) leave it alone, or (c) re-initiate from scratch |
  | `project.md` exists, `FEATURES.md` missing | Create it from `_bigin/templates/feature-map.md` in either branch |

* **Rules:** Only (c) rewrites `project.md`, only on explicit confirmation, and it still appends to the existing `## Changelog` rather than starting a new one. A config with no feature registry is broken — `/extract-signal` has nothing to anchor to.

## 2. Materialize the workspace

* **Goal:** put the rulebook, stage procedures, and scaffolds on a project-relative path every subagent can reach.
* **Action:** Read the plugin version from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json` (`version`) to stamp in § 4, then copy all three directories **whole**, preserving their internal structure — the nesting is what lets a subagent load one stage file instead of the rulebook:

  ```
  ${CLAUDE_PLUGIN_ROOT}/workspace/conventions/  →  _bigin/conventions/
  ${CLAUDE_PLUGIN_ROOT}/workspace/stages/       →  _bigin/stages/       (incl. extract/, transform/, design/)
  ${CLAUDE_PLUGIN_ROOT}/workspace/templates/    →  _bigin/templates/
  ```

  Then list all three recursively and confirm the file count matches the source. Anything missing:
  stop and report rather than continue to § 3.

  What lands, and who reads it — nothing reads all of it, and this skill reads none of it itself:

  | Path | Read by |
  |---|---|
  | `_bigin/conventions/` | every skill and subagent, but only its own named section or file — never the whole tree |
  | `_bigin/stages/` | the orchestrator or per-feature subagent for whichever stage is currently running — never the whole directory |
  | `_bigin/templates/*.md` | whichever skill creates that artifact type, the first time it's needed |

* **Rules:**
  - **Copy every stage file, not just the ones this project will use.** Which files a run reads is decided at read time, per signal and per lane; a project that skipped `3-lane-entity.md` because its first intake had no entity signal breaks the first run that does.
  - **Report the refresh** (§ 8) so anyone who edited a plugin-owned file finds out it was overwritten.
  - **Remove a legacy `_bigin/rules/` — only after the copy above has verified.** Projects initiated on plugin `≤ 1.2.0` have the flat layout this replaced. Left in place it's a second, stale copy of the rulebook at a path older prose may still cite, so a subagent can read a rule that no longer governs.

## 3. Gather the engagement config

* **Goal:** put on record what only the human knows, before any stage depends on it.
* **Action:** Take the client name from `$ARGUMENTS` if given; ask for the rest — `AskUserQuestion` for the closed choices, plain questions for the free-text ones.

  | Field | How to get it |
  |---|---|
  | `client` | `$ARGUMENTS`, or ask |
  | `approver` / `approver_email` | Ask — the one human who signs off requirements (`/approve-fr` gates on this person) |
  | `client_emails` | Ask — every address on the client side that might appear on an intake |
  | `team_emails` | Ask — your own team's addresses for this engagement |
  | `email_provider` | `AskUserQuestion`: **outlook** (default) or **spark** |
  | `outlook_folder` | `email_provider: outlook` only. Default `["Inbox"]`; ask if client mail lands elsewhere |
  | `meeting_provider` | `AskUserQuestion`: **fathom** (default), **spark**, or **firefly** |
  | `project_mode` | `AskUserQuestion`: **new** (greenfield) or **ongoing** (an existing product this repo contains or accompanies) |
  | `codebase_path` | `ongoing` only. Default the repo root (absolute); ask if the product lives elsewhere |
  | `intake_lookback_days` | Default `14`; don't ask unless the user raises it |
  | `repo` | **Detect, don't ask** — `git remote -v`. Blank if not a git repo |

  Ask explicitly whether `_bigin/` should be committed. On no, add `_bigin/` to `.gitignore` (create if
  missing); on yes, do nothing. Record the answer in `## Notes`. Either way add `.claude/*.local.md` —
  user-local config, not project data.

* **Rules:**
  - **`client_emails` matters more than it looks:** `/bigin-intake`'s sweep **halts** on an empty list, having no way to tell client correspondence from internal mail. If the addresses aren't to hand, say plainly that `/bigin-intake direct …` still works and the sweep stays unavailable.
  - **Ask both provider fields rather than defaulting silently.** `/bigin-intake` is forbidden from falling back to an unconfigured provider, so an unasked field becomes a run that skips a source without saying so.
  - **Intake holds verbatim client email and transcripts,** so whether `_bigin/` is tracked is the user's call, never a default.

## 4. Write the config

* **Goal:** land the config in the exact schema `/bigin-intake` parses.
* **Action:**
  1. Instantiate `_bigin/templates/project.md` into `_bigin/system/project.md`, filling frontmatter from § 3 plus `workspace_version` (the plugin version from § 2) and `updated` (today). Unsupplied fields stay `<unknown>` and get listed in § 8.
  2. Scaffold `.claude/bigin-ba-workflow-plugin.local.md` from `skills/bigin-new-project/template/settings.local.md`, **only if absent**.
* **Rules:**
  - **`workspace_version` is what makes staleness detectable** — a later run compares against it to tell whether `_bigin/conventions/` and `_bigin/stages/` need refreshing.
  - **Never overwrite a settings file a project wrote.** It's the one place a project may legitimately override plugin behavior (a `Why` house style, a standing feature-slug shortcut, § 5.3's research method). It lives in `.claude/` because it configures behavior rather than describing the engagement, and ships empty — every section falls back to a built-in default. Don't ask the user to fill it in; mention it in § 8.

## 5. Import a proposal, capture what's being built, research the domain

### 5.1 Import a proposal, if there is one

* **Goal:** seed `FEATURES.md` from a document that already names the scope.
* **Action:** Ask whether a proposal, scope document, or SOW exists.

  | Answer | What to do |
  |---|---|
  | Yes, with a path | `Read` it, add one `proposed` row to `01-Requirements/FEATURES.md` per feature it names, citing the document in each `Sources` cell. `project_mode: new` → straight to § 5.3 (the proposal is also the research input, so skip § 5.2). `ongoing` → stop here |
  | No / unreadable, `ongoing` | Leave `FEATURES.md` as the empty scaffold. Skip § 5.2 and § 5.3 |
  | No / unreadable, `new` | Continue to § 5.2 |

* **Rules:**
  - **Take slugs and names from the document's own wording.** Don't invent a feature it doesn't name; don't merge two it lists separately. Report the rows added so wrong slugs get corrected before signals anchor to them — a slug is permanent once artifacts reference it.
  - **Only `proposed` rows come from a proposal.** `committed`/`built`/`out-of-scope` are human-set (`_bigin/conventions/conventions.md` § Feature map).
  - **An empty registry on `ongoing` is the normal path, not a degraded one.** `/extract-signal` raises a feature-mapping question for the first unanchorable signal and the human mints the row then. An ongoing product's domain is the existing codebase and client relationship, not something to research cold from a two-sentence pitch.

### 5.2 No proposal on a greenfield project — ask what it does

* **Goal:** get something on record for research to work from, since nothing on disk says what's being built.
* **Action:** Ask in plain questions, not a rigid form — a short conversation, not an intake: what the product does in a sentence or two; who it's for and what problem it solves; anything already decided (a platform, a third-party integration, a compliance regime) worth knowing before research starts. Record the answer under `## Project Brief` in `_bigin/system/project.md`, dated, close to verbatim.
* **Rules:**
  - **Records what the human states, never a paraphrase.** A summarized brief is what domain research then goes and researches the wrong thing from.
  - **Don't derive `FEATURES.md` rows from this conversation.** A two-sentence pitch is thinner than a proposal, and guessing feature boundaries from it is worse than leaving the registry empty.

### 5.3 Domain research (`project_mode: new` only)

* **Goal:** ground the engagement in its domain before the first signal arrives, so `/extract-signal` and `/enrich-feature` inherit context instead of each rediscovering it per feature.
* **Action:** Read **`references/domain-research.md`** before doing anything here and follow it through to its own "Writing the findings" step. The output lands in two places: `_bigin/system/domain-research.md` (the full report) and a dated pointer line under `_bigin/system/project.md`'s `## Domain Research` (the summary).
* **Rules:** **Don't improvise a research procedure inline.** That file defines the built-in method and, separately, how to swap it for a different skill or agent without touching this file. Report the summary in § 8 as new grounding, not a housekeeping detail.

### 5.4 Materialize the project agent (`CLAUDE.md`)

* **Goal:** give any Claude Code session opened in this repo — not just one running a `/bigin-*`
  command — a standing brief: what the engagement is, where the BA artifacts live, and which skill to
  reach for next, without having to read `_bigin/system/project.md` and every SKILL.md cold.
* **Action:** Read **`references/claude-md.md`** before doing anything here and follow it through.
  It covers what the file must contain, how to merge into an existing repo-root `CLAUDE.md` (common on
  `ongoing`) without disturbing anything outside the plugin's own delimited section, and what to skip
  when there's no domain research to point to.
* **Rules:** **Don't improvise the content shape inline** — that file is the spec, the same way § 5.3
  defers to `domain-research.md`. Never overwrite a `CLAUDE.md` a codebase already had; only the
  delimited section is the plugin's to write. Report what happened in § 8 — new file, section added to
  an existing one, or section regenerated on a rerun.

## 6. Map the codebase (`project_mode: ongoing` only)

* **Goal:** anchor requirements to real code areas rather than invented ones.
* **Action:** **Deferred — leave `## Codebase map` empty with its comment, in both modes.** The repo-mapping approach isn't finalized, so `ongoing` behaves like `new` apart from recording `codebase_path`.
* **Rules:** Say so in § 8 rather than let the user believe a map was written.

<!-- Planned shape, once the mapping approach is settled:

Read the repo to establish where features will land. Look at the manifest/build files, the top-level
source layout, entry points, and the test setup. Then write into `## Codebase map`:

- **Stack**: <languages, frameworks, notable libraries — as evidenced by manifests, not assumed>
- **Entry points**: <path> — <what it starts>
- **Code areas**: a table of | Slug | Path(s) | What lives here |
- **Tests**: <framework + how to run, if discoverable>
- **Not covered**: <parts of the repo you didn't map, if any>

Rules for that section: code areas are directories, not features — a slug there names a place in the
code (`billing-api`, `web-checkout`) and asserts nothing about what a feature should do; feature names
come from client signals via `/extract-signal`, never from reading code. Only record what you actually
verified; an unclear directory goes under "Not covered" rather than getting a plausible guess. Keep it
to roughly a screen. -->

## 7. Check the configured providers are actually reachable

The two provider fields written in § 4 name tools this repo doesn't own. `/bigin-intake` Mode B refuses
to sweep against an unreachable provider — but it fails at the moment a BA wanted a sweep, days later,
having already typed the command. This moves that discovery to initiation, where it costs nothing to fix.

### 7.1 Probe

* **Goal:** establish the live state of the two providers this project selected.
* **Action:** Run `claude mcp list` **once** and reuse its output for both, then resolve each:

  | Provider | Kind | Reachable means | Tools `/bigin-intake` calls |
  |---|---|---|---|
  | `outlook` | MCP (local stdio) | a server row whose name contains `outlook`, state `✔ Connected` | `list_emails`, `search_emails`, `get_email`, `list_attachments`, `download_attachment` |
  | `fathom` | MCP (remote HTTP) | a row matching `fathom`, state `✔ Connected` | `list_meetings`, `get_meeting_transcript`, `get_recording_by_url` |
  | `firefly` | MCP (remote) | a row matching `firefl`, state `✔ Connected` | its list-meetings and transcript equivalents |
  | `spark` | CLI binary | `command -v spark` resolves | `spark emails`, `spark search`, `spark thread`, `spark meetings` |

* **Rules:**
  - **Check only the two providers this project selected.** Probing all five wastes turns and reports problems with tools nobody configured.
  - **Match server rows by substring, case-insensitively — never by exact name.** The same provider is `outlook`, `claude.ai Microsoft 365`, or `plugin:foo:outlook` depending on how it was added, and an exact-name check reports a connected server as missing.
  - **A connected row still needs its tools confirmed.** A connected server with a different toolset is a different integration wearing the right name. Missing tools are a mismatch, not a connection failure — report them, don't reinstall.

### 7.2 Remedy by state — install fixes exactly one of them

"Not available" is four different problems. Applying the install remedy to the wrong one wastes a run
at best and overwrites working config at worst.

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

* **Goal:** close the one gap that can be closed automatically, without mutating anything else.
* **Action:** Run the install for a provider in the **not configured** state only, **from this table alone**. Then re-run `claude mcp list` and re-classify — an install that lands typically arrives in `! Needs authentication`, not `✔ Connected`, so § 7.4 usually follows.

  | Missing | Command | Then |
  |---|---|---|
  | `fathom` | `claude mcp add --transport http fathom https://api.fathom.ai/mcp` | § 7.4 — remote connectors need authorizing |
  | `outlook`, server binary already on `PATH` | `claude mcp add outlook -- <the path `command -v` resolved>` | re-check; a local stdio server usually lands `✔ Connected` |
  | `outlook`, binary absent · `spark` · `firefly` | **none — stop and report** | § 7.5 |

* **Rules:**
  - **The last row is the common case, and guessing is worse than reporting it.** A wrong `brew install`/`npm i -g` either fails noisily or installs something that isn't the provider. Name the exact missing binary or server, say no install command is pinned for it, and let the user supply one.
  - **`claude mcp add` and nothing else** — it's undone by `claude mcp remove`. A package manager mutates the machine outside this repo, which needs the user's explicit go-ahead for that specific command.
  - **Re-adding a configured server** replaces working config with a default, turning an auth problem into an auth problem *plus* a lost transport setting.
  - **Report every command run, verbatim,** in § 8.

### 7.4 When a provider needs authorization

* **Goal:** hand the user an exact next action. OAuth needs a browser and a human — this step cannot complete it and must not try.
* **Action:** **A claude.ai connector** (Fathom, Microsoft 365, Gmail — a remote `https://…/mcp` row) → authorize it in claude.ai connector settings. **Any other MCP server** → run `/mcp` in an interactive Claude Code session, or `claude mcp` from the terminal.
* **Rules:** Never offer to paste a credential on the user's behalf. Authorization happens in their browser, not in this conversation.

### 7.5 Record the outcome

* **Goal:** give a later `/bigin-intake` failure a checked-once baseline to compare against instead of re-probing blind.
* **Action:** Write a dated line per provider into `_bigin/system/project.md`'s `## Provider readiness`:

  ```markdown
  ## Provider readiness
  <!-- Written by /bigin-new-project § 7. A snapshot, not a gate — /bigin-intake re-checks at sweep time. -->
  - email_provider: outlook — ✔ connected (2026-08-13)
  - meeting_provider: fathom — ! needs authentication: authorize in claude.ai connector settings (2026-08-13)
  ```

* **Rules:** It's a snapshot and it goes stale — a connector can be revoked the next day. `/bigin-intake` still runs its own pre-flight check; this never replaces it.

## 8. Report

1. **Workspace** — the three directories materialized or refreshed at version `<version>`, with file count. On a refresh add: local edits to plugin-owned files were overwritten, `.claude/bigin-ba-workflow-plugin.local.md` is where overrides belong, and whether a legacy `_bigin/rules/` was removed.
2. **Config** — paths created or updated, and whether `_bigin/` is tracked or ignored.
3. **Unknowns** — fields still `<unknown>`, editable in `_bigin/system/project.md`. Call out an empty `client_emails` specifically, with its consequence for the sweep.
4. **Settings** — `.claude/bigin-ba-workflow-plugin.local.md` scaffolded, or already existed and left alone.
5. **Features** — `proposed` rows imported from a proposal, if any, so wrong slugs get corrected now.
6. **Codebase map** — for `ongoing`, that mapping is deferred and the section is intentionally empty.
7. **Project brief & domain research** — for `new`: where the brief came from, which method ran the research, and the dated `## Domain Research` summary with a pointer to the full report. New grounding, not a housekeeping line — don't bury it under Features.
8. **Project agent (`CLAUDE.md`)** — whether it was created fresh, merged into an existing file (say so explicitly on `ongoing`, since that means a pre-existing codebase CLAUDE.md is now sharing the file), or regenerated on a rerun.
9. **Providers** — one line per configured provider, its state, what happened, and every command run verbatim. For anything unresolved give the exact next action — "authorize Fathom in claude.ai connector settings", "install the `spark` CLI and re-run this" — not "provider unavailable". An unactionable warning gets ignored until the first failed sweep.
10. **Next step** — `/bigin-intake` to capture the first meeting, email, or note. If a provider is unresolved, say plainly that `/bigin-intake direct …` works regardless and only Mode B's sweep is affected.

## Additional resources

- **`references/domain-research.md`** — the § 5.3 research method, and how to swap it for another skill or agent. Read before running § 5.3.
- **`references/claude-md.md`** — the § 5.4 spec for what `CLAUDE.md` must contain and how to merge it into an existing one. Read before running § 5.4.
- **`template/settings.local.md`** — the § 4.2 scaffold for project-level plugin overrides.
