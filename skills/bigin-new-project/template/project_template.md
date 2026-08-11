---
type: config
client: <client name>
approver: "<approver name>"
approver_email: "<approver email>"
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
updated: <YYYY-MM-DD>
---

# Vault settings — <Client Name>

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

Client: **<Client Name>** · Approver: **<Approver Name>** (<approver email>)

## Client contacts
| Name | Email | Role |
|------|-------|------|
| <name> | <email> | <role> |

## Team contacts
| Name | Role | Notes |
|------|------|-------|
| <name> | <role> | |

## Changelog
- Initialized for <Client Name> (<YYYY-MM-DD>)
