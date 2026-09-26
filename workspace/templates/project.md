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
platform: web             # web | mobile | both — drives design screen composition, nav shape, and prototype prompts
codebase_path:            # absolute path to the product repo — required when project_mode: ongoing
repo:                     # git remote or repo name — blank if this isn't a git repo
grounding: communication  # communication | codebase | both — where requirements come from (v1.12.0)
repos: []                 # grounding: codebase|both — read-only code roots, e.g. [repos/backend, repos/fe-web]
conflict_policy: ask      # ask | code-first — who settles a factual conflict between two readings
coverage_id_pattern:      # optional: trace rule-card ids instead of note rows, e.g. XR-[A-Z]+-\d{3}
budgets:                  # optional: {transform_per_feature_tokens: 600000, extract_per_note_tokens: 150000}
signal_log: split         # split | inline — hub Signal Logs in <slug>.signals.md (split) or in the hub
engine: engine            # engine | legacy — legacy = the v1.8 behaviour, for one minor version only
workspace_version:        # the plugin version that last materialized _bigin/{conventions,stages,templates,cards}
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
> - `platform` — what's being built: `web` (a browser app), `mobile` (a phone app), or `both`. Read by
>   `/bigin-generate-design`: it decides the regions vocabulary a screen spec uses, the shape of the
>   navigation map (sidebar shell vs. tab bar), how many prototype-prompt blocks get written, and which
>   design engine is required. It never reaches a use case — a UC stays platform-blind by design.
>   Absent on a project initiated before this field existed → treated as `web`.
> - `codebase_path` — absolute path to the product repo (only relevant when `project_mode: ongoing`).
> - `grounding` — `communication` (email, meetings, notes: extracted by agents), `codebase` (rule cards
>   mined from code, imported by `bin/bigin intake codebase` with no LLM call), or `both`. `codebase`/`both`
>   enables the adjudication stage (`workflows/adjudicate.js`): a `conflict`/`held` Signal Log row is
>   refereed against the code by `code-adjudicator`.
> - `repos` — the read-only code roots adjudication and codebase intake may read. Nothing writes under them.
> - `conflict_policy` — `code-first`: the code settles a factual disagreement between two readings;
>   `ask` (default): the facts are settled from code but the decision goes to a human as a gated question.
>   Intent ("should …") is never settled by code under either value.
> - `coverage_id_pattern` — when rule cards carry permanent ids, `bin/bigin coverage` traces those ids
>   through extract → file → transform instead of note rows.
> - `budgets` — token budgets per stage unit; `bin/bigin metrics report <run>` flags overruns.
> - `signal_log` — `split` keeps each hub's append-only Signal Log in `_features/<slug>.signals.md`
>   (agents read rows only through `bin/bigin worklist`); `inline` keeps it in the hub.
> - `engine` — `engine` (default). `legacy` is the one-minor-version escape hatch that lets a
>   half-migrated vault finish a run on v1.8 behaviour (`docs/MIGRATION.md`).
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
day after this was written. Only the two providers this project selected appear here.

The design-engine line(s) are the exception: /bigin-generate-design DOES gate on them (it halts
rather than designing against no engine), so an engine left `not installed` is a real blocker for
the design stage, not just an orientation note. One line per engine this project's `platform`
requires — `web` and `mobile` require one each, `both` requires both.

Which engine each platform requires is NOT named here on purpose: it is resolved at write time from
the plugin's own design-engine adapter, so swapping an engine stays a one-file edit there and never
means re-editing this template or a project's config. Fill `<engine>` with whatever that adapter
names for this project's platform. -->
- email_provider: `outlook | spark` — one of: `✔ connected` · `! needs authentication: <what to do>` · `✘ failed to connect: <error>` · `not installed: <what to install>` (`YYYY-MM-DD`)
- meeting_provider: `fathom | spark | firefly` — same states as above (`YYYY-MM-DD`)
- design_engine (`web | mobile`): `<engine>` — one of: `✔ installed` · `not installed: <install command>` · `skipped — waived in project settings` (`YYYY-MM-DD`)

## Notes
<!-- Anything about the engagement that doesn't fit a field above — e.g. whether `_bigin/` is
committed to git. -->

## Changelog
- Initialized for `<Client Name>` (`<YYYY-MM-DD>`)
