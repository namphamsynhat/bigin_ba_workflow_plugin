---
type: config
client: <client name>
client_emails:
  - <client contact email>
team_emails:
  - <your team's email group for this project>
outlook_folder:
  - <Outlook folder(s) where client emails land — email_provider: outlook only>
intake_lookback_days: 14
email_provider: outlook   # outlook | spark — which tool /intake pulls client email from
meeting_provider: fathom  # fathom | spark | firefly — which tool /intake pulls meeting transcripts from
project_mode: new        # new | ongoing
codebase_path:            # absolute path to the product repo — required when project_mode: ongoing
repo:                     # git remote or repo name — blank if this isn't a git repo
workspace_version:        # the plugin version that last materialized _bigin/{conventions,stages,templates}
updated: <YYYY-MM-DD>
---

# Vault settings — `<Client Name>`

> [!info] Single-project vault
> This is the canonical, machine-readable config for the pipeline commands. There is no
> `project:` field on individual notes — every artifact in this vault belongs to this
> engagement implicitly. Keep the frontmatter above current; it drives intake matching.
> - `client_emails` — every address on the client's side that might appear in From/To/CC.
> - `team_emails` — your own team's email group(s) for this project.
> - `outlook_folder` — the Outlook folder(s) where client emails land (`email_provider: outlook` only).
> - `intake_lookback_days` — fallback timeframe for `/intake`.
> - `email_provider` — which tool `/intake` reads client email from: `outlook` (Outlook MCP, default)
>   or `spark` (Spark Desktop via the `spark` CLI — see the `use-spark` skill).
> - `meeting_provider` — which tool `/intake` reads meeting transcripts from: `fathom` (Fathom MCP,
>   default), `spark` (Spark Desktop's `meetings`/`meeting` commands), or `firefly` (a Firefly MCP,
>   if one is connected to this session — none ships with this vault by default).
> - `project_mode` — `new` (greenfield) or `ongoing` (existing product).
> - `codebase_path` — absolute path to the product repo (only relevant when `project_mode: ongoing`).
> - `workspace_version` — written by `/bigin-new-project`; the plugin version whose rulebook and
>   templates are currently materialized under `_bigin/`. Re-run `/bigin-new-project` after a plugin
>   upgrade to refresh them.

Any field the human didn't supply stays `<unknown>` — never inferred.

Client: **`<Client Name>`**

## Client contacts
| Name | Email | Role |
|------|-------|------|
| `<name>` | `<email>` | `<role>` |

## Team contacts
| Name | Role | Notes |
|------|------|-------|
| `<name>` | `<role>` | |

## Codebase map
<!-- project_mode: ongoing only — written by /bigin-new-project § 6, refreshed on re-run. -->

## Project Brief
<!-- project_mode: new only, no proposal on file — written by /bigin-new-project § 5.2 from what
the human states in answer to "what does this do / who's it for / what's already decided", close
to verbatim rather than summarized. Skipped when a proposal exists (§ 5.1) or project_mode: ongoing. -->

## Domain Research
<!-- project_mode: new only — written by /bigin-new-project § 5.3. One dated line per research run,
pointing at the full report in _bigin/system/domain-research.md rather than duplicating it here. -->

## Provider readiness
<!-- Written by /bigin-new-project § 7 — one line per configured provider, dated. A snapshot for
orientation, never a gate: /bigin-intake re-checks at sweep time, and a connector can be revoked the
day after this was written. Only the two providers this project selected appear here. -->
- email_provider: `outlook | spark` — one of: `✔ connected` · `! needs authentication: <what to do>` · `✘ failed to connect: <error>` · `not installed: <what to install>` (`YYYY-MM-DD`)
- meeting_provider: `fathom | spark | firefly` — same states as above (`YYYY-MM-DD`)

## Notes
<!-- Anything about the engagement that doesn't fit a field above — e.g. whether `_bigin/` is
committed to git. -->

## Changelog
- Initialized for `<Client Name>` (`<YYYY-MM-DD>`)
