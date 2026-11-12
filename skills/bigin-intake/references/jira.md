# Jira tickets — provider detail for `/bigin-intake` Stage 2D

One INT note per ticket, for its whole life. The onshore team creates it, offshore is assigned, and both keep
editing the description and commenting for days — every sweep appends **only what changed** since the last one.
The engine does the delta, the ADF rendering and the onshore/offshore tagging; this stage only fetches.

```text
0. tools — the Atlassian MCP (claude.ai connector). Read tools only:
       getAccessibleAtlassianResources  → cloudId for jira_site
       searchJiraIssuesUsingJql         → the keys to fetch
       getJiraIssue                     → issue fields (summary, description, issuetype, status, parent, labels,
                                          priority, reporter, assignee, created, updated)
       listJiraIssueComments            → EVERY page of comments (or getJiraIssue with the comment field)
       listJiraIssueChangelogs          → EVERY page of the changelog (or getJiraIssue expand=changelog)
   Tool names have moved between connector versions: match by capability, and name the missing one if a
   capability is absent — never fall back to WebFetch on a Jira URL.

S. SPRINT START (only for "sprint <name> KEY …", or "new sprint" with a ticket list / a Jira sprint name)
       the team gives the keys; a Jira sprint name only → JQL  sprint = "<name>"  for the keys
       BIN intake jira-sprint --sprint "<name>" --keys KEY …
           → project.md jira_sprint / jira_watch = the new list; every ticket note not on it (and not a child
             of a listed ticket) → jira_watch: false — closed, never swept again. Jira itself is not touched.
           → prints kept / reopened / closed, and to_fetch: the listed keys with no note yet
       then run steps 2–3 for EVERY key — to_fetch mints the new notes, the rest pick up any change since
       relay the closed list and every `!` warning (a ticket closed while still waiting on dev) to the human

R. SPRINT REPORT  BIN intake jira-sprint --report   — run after sprint start AND after each extract
       every watched ticket → new-feature | update | bug | needs-anchor | pending
         new-feature   anchored to a feature born this sprint (every FEATURES.md source is a sprint ticket),
                       or extraction found none and drafted a new-scope question — a human confirms the slug
         update        anchored to a feature that existed before the sprint
         bug           a Bug ticket, with the feature it hit
         needs-anchor  several features fit — the note's open question asks which
         pending       not extracted yet; the hint (Epic → likely new feature) is a hint, never a decision
       relay it grouped; the new-feature rows are the ones the team must confirm before they become hubs

1. KEYS
       explicit "jira KEY …"  → those keys
       sweep, jira_watch set  → the watch list only:
                                (key in (<jira_watch>) OR parent in (<jira_watch>)) AND updated >= "<timeframe>"
                                — `parent in` picks up Stories added to a watched Epic mid-sprint
       sweep, no jira_watch   → jira_jql if set, else
                                project in (<jira_projects>) AND updated >= "<timeframe>" ORDER BY updated ASC
   an Epic in the list → also its children: JQL  parent = <EPIC-KEY>   (Epic Link is gone from the API)
   fetch the Epic BEFORE its children, so a child inherits the Epic's resolved feature

2. FETCH each key → write ONE file, unmodified:
       {inbox_dir}/_raw/jira/<KEY>.json  =  {"issue": <getJiraIssue>, "comments": [<all pages>],
                                             "changelog": [<all pages>]}
   never trim, translate or summarise a body — ADF stays ADF; the engine renders it

3. CAPTURE  BIN intake jira --issue {inbox_dir}/_raw/jira/<KEY>.json
       new ticket   → minted INT-### (source: jira, kind: requirement — feedback for a Bug)
       known ticket → only new comments / description revisions / field changes appended as new
                      ### SRC-n blocks; the note goes back to status: raw so /extract-signal re-reads it
       ignored / closed / unchanged → reported, nothing written
       a watched Epic's new child → watched too; a closed (off-sprint) ticket fetched by explicit key →
                      captured with a warning, stays closed
   the engine prints the phase from ## Jira status mapping, unknown authors (tagged needs-review), and a
   warning for any status the mapping does not cover — surface those, never edit the mapping yourself
```

Phases (`## Jira status mapping` in `{system_config}`, one table, rows per project): `active` and
`scope-agreed` capture normally (`scope-agreed` tells extraction the newest description and scope comment
are the agreed baseline), `ignore` never captures, `done` captures one last time and then the note stays
closed while the ticket stays done. `dev` is the status the team moves a ticket to once it is clear
(e.g. "Ready for Dev"). It gates approval only: use cases and designs are drafted from the ticket as soon
as its rows are filed, so the dev team reviews the flow, the PM reviews a quick design, and both feed
questions back through Jira. Once a project maps any status to `dev`, a UC built from that project's
tickets cannot be approved until they reach it (`bigin intake jira-gate --uc UC-###`, which /approve-uc
runs). The sweep that sees the status change prints `READY FOR DEV → approve UC-###, …`. Relay it to the
human. The team decides when a ticket is clear; never infer it from the thread.

`withdrawn` is for a ticket the client removed (Cancelled, Won't Do, Rejected …). The sweep that sees it
withdraws the note (`analysis.withdraw`, `_bigin/stages/extract/4-analysis.md` § Withdrawal): every hub row it
filed is closed, and content already applied to a UC becomes a `retract` row that the next
`/bigin-transform-signal` takes back out, with the reason on the UC's Changelog. Map those statuses to
`withdrawn`, not `ignore`. `ignore` only stops capture, so anything already extracted would stay in the spec.
A ticket that was **deleted** can no longer be fetched: when a watched key returns not-found, ask nothing,
run `bigin note withdraw <INT> --reason "Jira <KEY> deleted" --by "Jira sweep <date>"` and report it.
Withdrawal is per ticket or per feature, never per meeting or email. When the client drops a whole feature
(for example it costs too much or no longer fits the market), the human runs, or tells you to run,
`bigin feature withdraw <slug> --reason "<their words>" --by "<who, where, date>"`. A single point dropped in a
meeting is an ordinary signal, captured and extracted like any other. Never withdraw on your own reading of a thread.

Block kinds this stage writes: `ticket` (first capture: fields + summary + description), `comment`
(one per comment; an edited comment is a NEW block marked `(edited <ts>)`), `description` (the full new
summary + description each time either changes), `fields` (changelog: status, type, parent, labels, …).
Every ref carries `<author> (onshore|offshore|unknown) <timestamp>`.

