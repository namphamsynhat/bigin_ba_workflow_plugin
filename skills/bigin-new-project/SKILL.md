---
name: bigin-new-project
description: Initiate a new BA project in the current repo — scaffold `_bigin/`, capture the engagement config (client, approver, contacts, new vs. ongoing product), and map the existing codebase when there is one. Use once per repo, before the first /bigin-intake.
argument-hint: "[client name]"
disable-model-invocation: true
---

# Bigin New Project

Step 0 of the workflow. Sets up `_bigin/` in the repo Claude Code is running from and writes `_bigin/system/project.md` — the config every later stage reads for who the client is, who approves, and whether this is greenfield or an existing product.

Like `/bigin-intake`, this stage **records what the human tells you** — never guess a client name, an approver, or an email address. Anything unknown stays as `<unknown>` and gets asked, not inferred. The one thing you may derive on your own is the codebase map (§ 4), because that's read from the repo itself, not from anyone's intent.

See `references/conventions.md` for the plugin-wide ID scheme and artifact conventions every later stage follows.

## 1. Check what's already there

Read `_bigin/system/project.md` if it exists.

- **It exists** — this repo is already initiated. Show the current config and ask whether to (a) update specific fields, (b) leave it alone, or (c) re-initiate from scratch. Only (c) rewrites the file, and only after the user explicitly confirms; even then, keep the existing `## Changelog` and append to it rather than starting a new one.
- **It doesn't exist** — writes `01-Requirements/FEATURES.md` using `skills/bigin-new-project/template/feature-map.md` template and continue.

## 2. Gather the engagement config

Take the client name from `$ARGUMENTS` if given. Ask for the rest — use `AskUserQuestion` for the closed choices, plain questions for the free-text ones:

| Field | How to get it |
|---|---|
| `client` | `$ARGUMENTS`, or ask |
| `approver` / `approver_email` | Ask — the one human who signs off FRs (`/approve-fr` gates on this person) |
| `client_emails` | Ask — every address on the client side that might appear on an intake |
| `team_emails` | Ask — your own team's addresses for this engagement |
| `project_mode` | `AskUserQuestion`: **new** (greenfield — nothing built yet) or **ongoing** (an existing product this repo contains or accompanies) |
| `codebase_path` | `ongoing` only. Default to the repo root (absolute path); ask if the product lives elsewhere |
| `intake_lookback_days` | Default `14`, no need to ask unless the user raises it |

Also detect, don't ask: the repo's remote/name via `git remote -v` and the current branch. Record them in frontmatter as `repo:` and leave blank if the directory isn't a git repo.

One question worth asking explicitly: **should `_bigin/` be committed?** Intake files hold verbatim client emails and transcripts, so this is the user's call, not a default to assume. If they say no, add `_bigin/` to the repo's `.gitignore` (create it if missing); if yes, do nothing — the files are tracked like any other. Record the answer in the config's `## Notes`.

## 3. Scaffold and write the config

1. Write `_bigin/system/project.md`:

   ```
   ---
   type: config
   client: <client name>
   approver: <approver name>
   approver_email: <approver email>
   client_emails: [<client contact emails>]
   team_emails: [<your team's emails>]
   project_mode: new|ongoing
   codebase_path: <absolute path to the product repo — ongoing only, else blank>
   repo: <git remote or repo name, blank if not a git repo>
   intake_lookback_days: 14
   updated: <YYYY-MM-DD>
   ---

   # Project — <Client Name>

   Client: **<Client Name>** · Approver: **<Approver Name>** (<approver email>)

   ## Client contacts
   | Name | Email | Role |
   |------|-------|------|
   | <name> | <email> | <role> |

   ## Team contacts
   | Name | Role | Notes |
   |------|------|-------|
   | <name> | <role> | |

   ## Codebase map
   <!-- project_mode: ongoing only — written by /bigin-new-project § 4, refreshed on re-run. -->

   ## Notes
   - <anything the user said about the engagement that doesn't fit a field above, e.g. whether `_bigin/` is committed>

   ## Changelog
   - Initiated for <Client Name> (<YYYY-MM-DD>)
   ```

   Every field the user didn't give stays `<unknown>` — list them back at the end (§ 5) so they can be filled in later.

2. Scaffold `.claude/bigin-ba-workflow-plugin.local.md` from `skills/bigin-new-project/template/conventions.md`, only if it doesn't already exist — never overwrite one a project already wrote. This is the plugin's settings file (lives in `.claude/`, not `_bigin/`, since it configures how `/bigin-intake` and `/extract-signal` behave, not project data), and it ships empty: `/extract-signal` and `/bigin-intake` fall back to their built-in defaults for any section left blank. Don't ask the user to fill it in now — just create the scaffold and mention it in the report (§ 5) so they know it's there to edit later.

## 4. Ask for project proposal is exist

ask user for the project proposal file. if exists, tool `Read` then import the feature list to `01-Requirements/FEATURES.md` if not keep the feature file as placeholder.

## 5. Map the codebase (`project_mode: ongoing` only)

Skip this entirely as will be enhance later when finalizing the code repo mapping approach. Currently only support new mode

<!-- Skip this entirely when the mode is `new` — leave `## Codebase map` empty with its comment.

Read the repo to establish where features will land, so `/bigin-transform-signal` and `/enrich-feature` can anchor requirements to real code areas instead of inventing them. Look at the manifest/build files, the top-level source layout, entry points, and the test setup. Then write into `## Codebase map`:

```
- **Stack**: <languages, frameworks, notable libraries — as evidenced by manifests, not assumed>
- **Entry points**: <path> — <what it starts>
- **Code areas**:
  | Slug | Path(s) | What lives here |
  |------|---------|-----------------|
  | <kebab-slug> | <dir> | <one line> |
- **Tests**: <framework + how to run, if discoverable>
- **Not covered**: <parts of the repo you didn't map, if any>
```

Rules for this section:

- **Code areas are directories, not features.** A slug here names a place in the code (`billing-api`, `web-checkout`); it does **not** assert that a feature exists or what it should do. Feature names come from client signals via `/extract-signal`, never from reading code.
- **Only record what you actually verified.** If you can't tell what a directory does, say so under "Not covered" rather than writing a plausible guess.
- Keep it to roughly a screen — this is an orientation map, not documentation of the codebase. -->

## 5. Report

Tell the user:

1. What was created (paths), and whether `_bigin/` is tracked or ignored.
2. The fields still `<unknown>`, if any, and that they can edit `_bigin/system/project.md` directly.
3. That `.claude/bigin-ba-workflow-plugin.local.md` was scaffolded (or already existed, and was left alone) — an optional settings file they can edit for house-style overrides.
4. For `ongoing`: the code-area slugs you recorded, so they can correct any that are wrong.
5. Next step: `/bigin-intake` to capture the first meeting, email, or note.
