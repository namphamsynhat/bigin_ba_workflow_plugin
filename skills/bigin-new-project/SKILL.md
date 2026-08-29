---
name: bigin-new-project
description: Initiate a new BA project in the current repo — materialize the rulebook and templates into `_bigin/`, capture the engagement config (client, contacts, new vs. ongoing product, web vs. mobile vs. both platform), import a proposal or, for a greenfield project with none yet, ask what's being built and run domain research on it, materialize a repo-root CLAUDE.md as the project's standing agent brief, map the existing codebase when there is one, and verify the configured email/meeting providers are reachable — installing a missing MCP server where an install command is known — plus whether the design engine the chosen platform would default to for rendering is installed. Use once per repo before the first /bigin-intake, and again after a plugin upgrade to refresh the materialized rulebook, regenerate CLAUDE.md, or re-check provider and design-engine access.
argument-hint: "[client name]"
disable-model-invocation: true
---

# Bigin New Project

Step 0. Sets up `_bigin/` in the current repo, writes the config every later stage reads, and checks
that the tools that config names — the two intake providers, and the design engine its `platform`
requires — can actually be reached.

The plugin ships its rulebook and templates inside itself; this skill **copies them into the project**
so every later skill and dispatched subagent can reach them project-relatively. Subagents carry no
plugin context, so a path into the install directory is unreachable to them.

> **Artifact Standard:** Outputs:
>> **The materialized workspace** — `_bigin/conventions/`, `_bigin/stages/`, `_bigin/templates/`: plugin-owned, overwritten every run, reachable to every subagent.
>> **The engagement config** — `_bigin/system/project.md`: client, contacts, providers, greenfield vs. ongoing, web vs. mobile vs. both, plus the project brief, domain-research pointer, and provider/design-engine readiness snapshot.
>> **The project agent** — repo-root `CLAUDE.md`: a delimited, plugin-owned section orienting any Claude Code session to the engagement, the workspace map, and the skill sequence, regenerated every run.

---

## Non-Negotiable Core Rules

* **Record, never guess:** client name, contacts, and email addresses come from the human. Unknowns stay `<unknown>` and get asked. Only the git remote (§ 3) and the codebase map (§ 6) may be derived, both read from the repo rather than from intent.
* **Plugin-owned vs. project data:** overwrite `_bigin/{conventions,stages,templates}/` every run; never touch `_bigin/system/project.md`, `00-Inbox/`, `01-Requirements/`, `PRD.md`, `prototypes/`, `epics.md`. Project overrides belong in `.claude/bigin-ba-workflow-plugin.local.md`. `CLAUDE.md` is a special case — see § 5.4: only the plugin's own delimited section inside it is overwritten; whatever else is in that file, including a pre-existing codebase CLAUDE.md, is never touched.
* **Verify, don't assume:** a partial copy surfaces later as a subagent silently unable to read its lane guide — reported as a clean run. Confirm the file count before continuing.
* **Use the template, not memory:** `_bigin/templates/project.md` *is* the schema `/bigin-intake` parses. A hand-written variant is how a field it reads goes missing.
* **Never improvise an install:** § 7.3's table for a provider, § 7.6's adapter for a design engine, or nothing. `claude mcp add` is the only install this skill ever runs itself — never `sudo`, never a package manager, never re-add a server that already has a row, and never install a design engine (§ 7.6: a plugin install and a third-party desktop app are the user's call).
* **Never handle credentials:** OAuth needs a browser and a human. Never ask for a token, authorization code, client secret, or callback URL.
* **Providers never block, and neither does the design engine any more:** a gap doesn't invalidate the config — record the state, remedy what's remedyable, report the rest, finish the run. The design engine used to be different in kind, because `/bigin-generate-design` halted without it. It no longer does: only `/bigin-render-design-od` needs an engine, and only when a human asks it to render, so § 7.6 records a missing one as early warning about that optional later step.

---

## Execution order

| § | Section | Runs when |
|---|---|---|
| 1 | Check what's already there | every run |
| 2 | Materialize the workspace | every run |
| 2.5 | Ensure the domain-research skill is available | every run |
| 3–4 | Gather and write the engagement config | fresh initiation, or an explicit re-initiate |
| 5.1–5.3 | Import a proposal, capture the brief, research the domain | § 5.3 on `project_mode: new` only |
| 5.4 | Materialize the project agent (`CLAUDE.md`) | every run |
| 6 | Map the codebase | `ongoing` only — currently deferred |
| 7.1–7.5 | Check the two configured providers | every run |
| 7.6 | Check the platform's default render engine | every run — one on `web`/`mobile`, both on `both`. Early warning for `/bigin-render-design-od`; blocks nothing |
| 8 | Report | every run |

## 1. Check what's already there

* **Goal:** decide whether this is a fresh initiation, a plugin-upgrade refresh, or a config edit.
* **Action:** Read `_bigin/system/project.md` if it exists, and note whether `01-Requirements/FEATURES.md` does.

  | State | What to do |
  |---|---|
  | Neither exists | Fresh initiation — continue through every section |
  | `project.md` exists | Already initiated. Materialize anyway (§ 2 is safe to repeat, and is how a plugin upgrade reaches an existing project), then show the current config and ask whether to (a) update specific fields, (b) leave it alone, or (c) re-initiate from scratch |
  | `project.md` exists, `FEATURES.md` missing | Create it from `_bigin/templates/feature-map.md` in either branch |

* **Rules:**
  - Only (c) rewrites `project.md`, only on explicit confirmation, and it still appends to the existing `## Changelog` rather than starting a new one. A config with no feature registry is broken — `/extract-signal` has nothing to anchor to.
  - **A pre-`1.7.4` config carries `approver` / `approver_email`.** Nothing reads them any more — approval is the call of whichever human is in the session, not a configured person. Leave them where they are on a refresh (they're project data, and stale-but-harmless), and drop both lines on an (a) field update or a (c) re-initiate. Never re-add them, and never ask for an approver.
  - **A pre-`1.8.0` config carries no `platform:` at all.** The absent key reads as `web` everywhere (`design-platform.md` § Platform), so the project keeps designing exactly as it always did — nothing is broken, and a plain (b) refresh leaves the key absent rather than stamping a value nobody stated. Ask for it and stamp it on an (a) field update or a (c) re-initiate; otherwise `/bigin-upgrade-project` is what stamps an existing project onto the new schema.

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
  - **Copy every stage file, not just the ones this project will use.** Which files a run reads is decided at read time, per signal and per lane; a project that skipped `3-lane-design.md` because its first intake had no presentation-only signal breaks the first run that does.
  - **Report the refresh** (§ 8) so anyone who edited a plugin-owned file finds out it was overwritten.
  - **Remove a legacy `_bigin/rules/` — only after the copy above has verified.** Projects initiated on plugin `≤ 1.2.0` have the flat layout this replaced. Left in place it's a second, stale copy of the rulebook at a path older prose may still cite, so a subagent can read a rule that no longer governs.

## 2.5. Ensure the domain-research skill is available

* **Goal:** every domain-research pass — this project's own (§ 5.3) and every feature's later, automatic
  one (`/extract-signal` § Step 2a) — should default to a real domain-research skill instead of the
  plugin's built-in WebSearch fallback, without a human having to install anything by hand.
* **Action:**
  1. Check whether `bmad-domain-research` is already available — in this session's skill list, or on
     disk at `.claude/skills/`.
  2. If absent, and `.claude/bigin-ba-workflow-plugin.local.md` § Domain research method does not
     record `domain_research_skill_install: false`, run once:
     `npx -y skills add bmad-code-org/bmad-method --skill bmad-domain-research --agent claude-code`
  3. On success: if § Domain research method in that settings file is still blank, write
     `skill: bmad-domain-research` into it. **Never overwrite an explicit override already there** —
     a project that already named a different skill or agent, or `built-in`, keeps its own choice.
  4. On failure (offline, `npx` unavailable, install error): leave the method unset and move on —
     `_bigin/conventions/domain-research-method.md` falls back to the built-in method automatically.
* **Rules:**
  - **This is not `claude mcp add`.** § 7.3's "never improvise an install" rule is about MCP servers;
    this is a one-shot `npx` install of a skill file into this project's own `.claude/skills/`, the
    same class of action a human would run by hand — still never a package manager, never `sudo`.
  - **A failed or skipped install never blocks this run**, same reasoning as § 7's providers: research
    quality degrades to built-in, nothing halts.
  - **Report the outcome in § 8** — installed, already present, skipped by opt-out, or failed and why.

## 3. Gather the engagement config

* **Goal:** put on record what only the human knows, before any stage depends on it.
* **Action:** Take the client name from `$ARGUMENTS` if given; ask for the rest — `AskUserQuestion` for the closed choices, plain questions for the free-text ones.

  | Field | How to get it |
  |---|---|
  | `client` | `$ARGUMENTS`, or ask |
  | `client_emails` | Ask — every address on the client side that might appear on an intake |
  | `team_emails` | Ask — your own team's addresses for this engagement |
  | `email_provider` | `AskUserQuestion`: **outlook** (default) or **spark** |
  | `outlook_folder` | `email_provider: outlook` only. Default `["Inbox"]`; ask if client mail lands elsewhere |
  | `meeting_provider` | `AskUserQuestion`: **fathom** (default), **spark**, or **firefly** |
  | `project_mode` | `AskUserQuestion`: **new** (greenfield) or **ongoing** (an existing product this repo contains or accompanies) |
  | `platform` | `AskUserQuestion`: **web** (default — something people use in a browser, on a computer) · **mobile** (a phone app people install) · **both** (the same product in both places) |
  | `codebase_path` | `ongoing` only. Default the repo root (absolute); ask if the product lives elsewhere |
  | `intake_lookback_days` | Default `14`; don't ask unless the user raises it |
  | `repo` | **Detect, don't ask** — `git remote -v`. Blank if not a git repo |

  Ask explicitly whether `_bigin/` should be committed. On no, add `_bigin/` to `.gitignore` (create if
  missing); on yes, do nothing. Record the answer in `## Notes`. Either way add `.claude/*.local.md` —
  user-local config, not project data.

* **Rules:**
  - **`client_emails` matters more than it looks:** `/bigin-intake`'s sweep **halts** on an empty list, having no way to tell client correspondence from internal mail. If the addresses aren't to hand, say plainly that `/bigin-intake direct …` still works and the sweep stays unavailable.
  - **Ask both provider fields rather than defaulting silently.** `/bigin-intake` is forbidden from falling back to an unconfigured provider, so an unasked field becomes a run that skips a source without saying so.
  - **Ask `platform`; never infer it from what the product sounds like.** Before this field existed every design run silently produced a desktop web app, so a phone product got designed as a browser one — the right screens in the wrong shell, and nobody finds out until a client opens the prototype. It is also a separate question from `project_mode`: that one is new-vs-ongoing, this one is browser-vs-phone, and a greenfield mobile product answers both. `platform` never reaches a use case — a UC stays platform-blind by design — it drives `/bigin-generate-design` only: the regions vocabulary, the navigation shell, how many prototype-prompt blocks get written, and which design engine § 7.6 checks for.
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
  - **Only `proposed` rows come from a proposal.** `committed`/`built`/`out-of-scope` are human-set (`_bigin/conventions/feature-hub.md` § Feature Map format).
  - **An empty registry on `ongoing` is the normal path, not a degraded one.** `/extract-signal` raises a feature-mapping question for the first unanchorable signal and the human mints the row then. An ongoing product's domain is the existing codebase and client relationship, not something to research cold from a two-sentence pitch.

### 5.2 No proposal on a greenfield project — ask what it does

* **Goal:** get something on record for research to work from, since nothing on disk says what's being built.
* **Action:** Ask in plain questions, not a rigid form — a short conversation, not an intake: what the product does in a sentence or two; who it's for and what problem it solves; anything already decided (a platform, a third-party integration, a compliance regime) worth knowing before research starts. Record the answer under `## Project Brief` in `_bigin/system/project.md`, dated, close to verbatim.
* **Rules:**
  - **Records what the human states, never a paraphrase.** A summarized brief is what domain research then goes and researches the wrong thing from.
  - **Don't derive `FEATURES.md` rows from this conversation.** A two-sentence pitch is thinner than a proposal, and guessing feature boundaries from it is worse than leaving the registry empty.

### 5.3 Domain research (`project_mode: new` only)

* **Goal:** ground the engagement in its domain before the first signal arrives, so `/extract-signal` and every later stage inherit context instead of each rediscovering it per feature.
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

## 7. Check the configured providers and the platform's default render engine are actually reachable

The two provider fields written in § 4 name tools this repo doesn't own. `/bigin-intake` Mode B refuses
to sweep against an unreachable provider — but it fails at the moment a BA wanted a sweep, days later,
having already typed the command. This moves that discovery to initiation, where it costs nothing to fix.

`platform` (§ 3) names one more tool this repo doesn't own: the design engine
`/bigin-render-design-od` renders prototypes with. Same reasoning, milder consequence now — that skill
**halts** without its engine, so the discovery is worth having now rather than at the moment somebody
wants to show a client something. It stops nothing else: a design run needs no engine at all.
§§ 7.1–7.5 do the two providers; § 7.6 does the engine, and its remedies are deliberately different.

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
  <!-- Keep the template's own comment here verbatim; § 7.6's engine lines join these two. -->
  - email_provider: outlook — ✔ connected (2026-08-13)
  - meeting_provider: fathom — ! needs authentication: authorize in claude.ai connector settings (2026-08-13)
  ```

* **Rules:** For these two providers it's a snapshot and it goes stale — a connector can be revoked the next day. `/bigin-intake` still runs its own pre-flight check; this never replaces it.

### 7.6 Check the design engine

* **Goal:** find out now, at zero cost, whether `/bigin-render-design-od` will have a tool to render with when somebody eventually wants a prototype. **`/bigin-generate-design` no longer needs one** — it renders nothing, halts for nothing, and produces the spec and its prompt blocks whatever is installed. So this is early warning about a *later, optional* step, not a precondition for anything on the requirements path.
* **Action:** The probe is a script — `${CLAUDE_PLUGIN_ROOT}/skills/bigin-render-design-od/scripts/check_setup.py` — and the install command comes from **`${CLAUDE_PLUGIN_ROOT}/skills/bigin-render-design-od/references/open-design-adapter.md` § Probe**, which remains the single source for it. **Open Design is the only render engine, on every platform** — `platform` (§ 3) decides the shell a render builds, not which tool builds it, so there is one check here and not one per platform:

  | Engine | Install-check |
  |---|---|
  | Open Design (`nexu-io/open-design`) | run `python3 "${CLAUDE_PLUGIN_ROOT}/skills/bigin-render-design-od/scripts/check_setup.py"` — it applies § Probe for you (the `open-design` MCP row, case-insensitive substring, state `✔ Connected`) and confirms the daemon by reading its catalog off disk. Exit 0 = connected; exit non-zero prints the reason. Nothing else here needs its project or design-system listing, so ignore the rest of its report |

  On missing, report the install command **from the adapter, verbatim**:

  | Missing | Command |
  |---|---|
  | Open Design | `od mcp install claude` — or `curl -fsSL https://open-design.ai/install.sh \| sh -s claude`, a thin wrapper around the same command. On a macOS desktop install prefer the app's **Settings → MCP server** snippet, as its README says |

  Then write a dated line into `## Provider readiness`, in the template's format:

  ```markdown
  - design_engine (render): open-design — ✔ connected (2026-08-21)
  - design_engine (render): open-design — not installed: od mcp install claude (2026-08-21)
  ```

* **Rules:**
  - **`not installed` here is a note, not a blocker — and that changed.** It used to genuinely block the design stage, because `/bigin-generate-design` halted without its engine. It no longer does: design runs need no engine at all, and only `/bigin-render-design-od` halts, when a human asks for a prototype it cannot produce. So record it as *the render step's* missing tool — nameable now, installable any time before somebody wants a prototype — and never as a gap on the requirements path.
  - **Never auto-install the design engine — report the command and stop.** § 7.3's automatic remedy is scoped to `claude mcp add` for a missing MCP provider precisely because that one command is repo-local and undone by `claude mcp remove`. Open Design is a third-party desktop app that installs software on the machine, so it is the user's call, needing their explicit go-ahead for that specific command. Never `sudo`, never a package manager, never a credential (§ Non-Negotiable Core Rules, unchanged).
  - **Never improvise an install command.** The adapter's table or nothing — the same rule § 7.3 states for providers, and the adapter states it back for engines. A guessed installer either fails noisily or installs something that is not the engine.
  - **`command -v od` proves nothing.** `/usr/bin/od` is the BSD octal-dump utility and wins on `PATH` on a stock macOS, so a resolving `od` is not evidence Open Design is there and a bare `od mcp install claude` typed into a terminal may run the wrong program. The interface is the MCP server, not the CLI; if a CLI probe is ever wanted it is `od project list --json` — octal-dump errors out, Open Design returns JSON. This is exactly the class of false result this section exists to catch.
  - **Match the MCP row by substring, case-insensitively,** for the same reason § 7.1 does.
  - **`design_engine_required: false` is retired — do not scaffold it, and do not honour it.** It existed only to stop a *design* run halting for a *render* tool, and with the two separated there is nothing left to waive. A project that never wants to render simply never runs `/bigin-render-design-od`. A line already present in an existing settings file is harmless and needs no migration; it just does nothing.
  - **`/bigin-render-design-od` resolves its own Open Design project, design system, and model at run time, and asks the human about each.** Nothing here picks any of them, and § 7.6 scaffolds no default for them — a design system chosen at project-init would be a brand decision made months before anyone looked at a screen. That skill persists what the human picked into `{project_file}` on the first render (its § Step 0.5), so the question is asked once, not every run.

## 8. Report

1. **Workspace** — the three directories materialized or refreshed at version `<version>`, with file count. On a refresh add: local edits to plugin-owned files were overwritten, `.claude/bigin-ba-workflow-plugin.local.md` is where overrides belong, and whether a legacy `_bigin/rules/` was removed.
2. **Config** — paths created or updated, the captured `project_mode` and `platform` (both, and as two separate facts — new-vs-ongoing and browser-vs-phone), and whether `_bigin/` is tracked or ignored.
3. **Unknowns** — fields still `<unknown>`, editable in `_bigin/system/project.md`. Call out an empty `client_emails` specifically, with its consequence for the sweep.
4. **Settings** — `.claude/bigin-ba-workflow-plugin.local.md` scaffolded, or already existed and left alone.
5. **Domain-research skill** — `bmad-domain-research` already present, freshly installed, install skipped (opt-out or an existing method override), or install failed and why. Say plainly which method future domain-research passes (this project's and every feature's) will actually use.
6. **Features** — `proposed` rows imported from a proposal, if any, so wrong slugs get corrected now.
7. **Codebase map** — for `ongoing`, that mapping is deferred and the section is intentionally empty.
8. **Project brief & domain research** — for `new`: where the brief came from, which method ran the research, and the dated `## Domain Research` summary with a pointer to the full report. New grounding, not a housekeeping line — don't bury it under Features.
9. **Project agent (`CLAUDE.md`)** — whether it was created fresh, merged into an existing file (say so explicitly on `ongoing`, since that means a pre-existing codebase CLAUDE.md is now sharing the file), or regenerated on a rerun.
10. **Providers** — one line per configured provider, its state, what happened, and every command run verbatim. For anything unresolved give the exact next action — "authorize Fathom in claude.ai connector settings", "install the `spark` CLI and re-run this" — not "provider unavailable". An unactionable warning gets ignored until the first failed sweep.
11. **Design engine** — its own item, not a line under Providers, because it is a named later dependency rather than a degraded sweep. Name the engine and its state. Connected → one line, done. Missing → say it plainly, with the exact next action and with what it does and does not block: "`/bigin-generate-design` runs regardless — it renders nothing. `/bigin-render-design-od` will halt until Open Design is connected — run `od mcp install claude`, then it runs." Never soften it to "engine unavailable", and never report it as a blocker on the requirements path, because it is not one.
12. **Next step** — `/bigin-intake` to capture the first meeting, email, or note. If a provider is unresolved, say plainly that `/bigin-intake direct …` works regardless and only Mode B's sweep is affected. A missing design engine affects neither, and no longer affects the design stage either: it stops only `/bigin-render-design-od`, the optional last step, and can be installed any time before somebody wants a prototype.

## Additional resources

- **`references/domain-research.md`** — the § 5.3 project-level research step; defers to `_bigin/conventions/domain-research-method.md` for the actual dispatch mechanics, shared with the feature-level research `/extract-signal` runs automatically. Read before running § 5.3.
- **`references/claude-md.md`** — the § 5.4 spec for what `CLAUDE.md` must contain and how to merge it into an existing one. Read before running § 5.4.
- **`template/settings.local.md`** — the § 4.2 scaffold for project-level plugin overrides.
