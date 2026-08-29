# Bigin BA Workflow Plugin — User Guide

This guide gets a Business Analyst from "never touched this plugin" to running the pipeline
day-to-day. For the deep architecture (why things are built the way they are, subagent
dispatch, the deterministic lint hook), see [README.md](README.md). This document only covers
what you need to install it and use it.

## 1. What this plugin does

It's a Claude Code plugin that turns raw client communication — meeting transcripts, emails,
a note you dictate — into structured requirement documentation: signals → use cases and
business rules → an approved requirement set → a UX design spec → (on request) an interactive
prototype → a PRD. Epics and user stories are still cut by hand; everything before that is
driven by the plugin.

Everything the pipeline writes lands as plain markdown inside the current repo (`00-Inbox/`,
`01-Requirements/`, `04-UIUX/`, `02-PRD/`), so it's readable, diffable, and reviewable without
opening Claude Code at all.

## 2. Prerequisites

- **Claude Code**, with a plugin marketplace or local plugin directory available.
- **A dedicated repo (or folder) for the engagement.** Each client engagement gets its own
  vault — don't run this inside your product's own source repo unless that repo *is* the
  ongoing product you're documenting.
- **At least one email provider and one meeting provider**, so intake can sweep for new client
  communication automatically:
  - Email: **Outlook** (via MCP) or **Spark** (CLI)
  - Meetings: **Fathom** (via MCP), **Spark**, or **Firefly**
  - These aren't hard requirements — `/bigin-intake direct …` works with zero providers
    configured, you'll just paste content in by hand instead of sweeping for it.
- **Open Design** (optional) — only needed if you want to render an interactive prototype from
  a finished UX spec. Nothing on the requirements path needs it.

## 3. Installing the plugin

The plugin ships its own marketplace manifest (`.claude-plugin/marketplace.json`), so anyone
on the team can add it straight from its GitHub repo — no publishing step, no separate
marketplace to stand up.

### 3.1 From the GitHub repo (recommended for a team)

Inside a Claude Code session, run:

```
/plugin marketplace add namphamsynhat/bigin_ba_workflow_plugin
```

This works with any of these source forms, so use whichever matches how your team accesses
the repo:

```
/plugin marketplace add namphamsynhat/bigin_ba_workflow_plugin           # GitHub shorthand
/plugin marketplace add https://github.com/namphamsynhat/bigin_ba_workflow_plugin.git
/plugin marketplace add git@github.com:namphamsynhat/bigin_ba_workflow_plugin.git   # SSH
```

If the repo is private, make sure `git` on your machine can already clone it (an SSH key
loaded, or an HTTPS credential helper / token configured) — Claude Code shells out to your
existing `git`, it doesn't prompt for a fresh login. Append `#<branch-or-tag>` to the URL to
pin a specific branch or release instead of the default branch.

Then install the plugin from that marketplace (the marketplace name, `bigin-ba-workflow`,
comes from the `name` field in `.claude-plugin/marketplace.json`):

```
/plugin install bigin-ba-workflow-plugin@bigin-ba-workflow
```

Useful commands while you're here:

| Command | Does |
|---|---|
| `/plugin marketplace list` | show every marketplace you've added |
| `/plugin marketplace remove bigin-ba-workflow` | remove it |
| `/plugin` | opens the interactive plugin UI (Marketplaces / Installed tabs) — same actions, no typing |

To pick up new commits after a plugin update, re-run the same `/plugin marketplace add`
command (or use the **Marketplaces** tab in `/plugin`) to refresh it, then restart Claude Code.

### 3.2 Local development install

For working on the plugin itself, or trying out a branch before sharing it — point Claude
Code at a local clone directly, no marketplace involved:

```bash
git clone https://github.com/namphamsynhat/bigin_ba_workflow_plugin.git
claude --plugin-dir /path/to/bigin_ba_workflow_plugin
```

You can repeat `--plugin-dir` to load more than one local plugin at once.

### 3.3 After installing, either way

**Restart Claude Code** (or start a fresh session) — hooks and MCP registrations only load at
session start. Run `/hooks` to confirm the plugin's lint hook is listed, and `/plugin` (or
`claude plugin list` from the terminal) to confirm the plugin itself shows as installed.

If you're developing the plugin and edit a `SKILL.md`, `/reload-plugins` picks it up without a
restart; changes under `workspace/` need a re-run of `/bigin-new-project` in your test project
to re-materialize them into `_bigin/`.

### 3.4 The plug-and-play components, at a glance

The plugin itself is just Claude Code skills and a lint hook — everything below is a
**separate tool** it talks to over MCP (or a CLI). None of them are bundled with the plugin;
`/bigin-new-project` checks each one you've configured and connects what it safely can.

| Component | What it's for | Can `/bigin-new-project` install it for you? |
|---|---|---|
| **Outlook** | email intake | Only if an Outlook MCP server binary is already on your machine's `PATH` — it registers it with `claude mcp add`. It cannot obtain that binary for you |
| **Fathom** | meeting-transcript intake | Yes — it runs `claude mcp add` for you; you still authorize it yourself in the browser |
| **Spark** | email + meeting intake (alternative to Outlook/Fathom) | No — it's a desktop app with a bundled CLI; install it yourself, the plugin only detects it afterward |
| **Firefly** | meeting-transcript intake (alternative to Fathom) | No — connect its MCP server yourself; the plugin only detects it afterward |
| **Open Design** | renders the interactive prototype (`/bigin-render-design-od`) | No — it's a third-party desktop app; the plugin reports the install command but never runs it, since it installs software on your machine |

Details on connecting each one are in the next section.

## 4. Connecting the providers and Open Design

You only need **one** email provider and **one** meeting provider — pick whichever your team
already uses. None of this is required to start: `/bigin-intake direct …` and the whole
requirements pipeline work with zero providers connected, you'll just paste content in by hand
instead of sweeping for it automatically. Open Design is only needed for the optional
prototype-render step.

`/bigin-new-project` runs all of the checks below for you and tells you exactly what's
missing — treat this section as what's happening behind that report, and how to fix what it
flags. You can also check any of them yourself at any time with `claude mcp list`.

### 4.1 Outlook (email)

Outlook connects as a local MCP server. The plugin doesn't ship one or know a specific
package for it — get an Outlook MCP server set up on your machine first (ask whoever manages
MCP integrations on your team if you don't already have one), then:

```
command -v <the outlook mcp server binary>      # confirm it resolves on PATH
claude mcp add outlook -- <the path that resolved>
claude mcp list                                 # confirm a row containing "outlook" shows ✔ Connected
```

`/bigin-new-project` does exactly this for you automatically the moment it finds the binary on
`PATH` — you only need to do it by hand if that auto-step reports the binary as absent.

### 4.2 Fathom (meetings)

This is the easiest one — the plugin knows the exact command:

```
claude mcp add --transport http fathom https://api.fathom.ai/mcp
```

`/bigin-new-project` runs this for you automatically when Fathom isn't configured yet. Right
after adding it, it usually shows `! Needs authentication` rather than connected — that's
expected for a remote connector. Authorize it in your **claude.ai connector settings** (in your
browser), then re-run `claude mcp list` to confirm it flips to `✔ Connected`.

### 4.3 Spark (email and/or meetings)

Spark is a third-party desktop app with a bundled `spark` CLI, used in place of Outlook and/or
Fathom. Install Spark Desktop itself first, following its own installer/docs — the plugin has
no automated install for it. Once it's installed:

```
command -v spark      # confirms the CLI resolved on PATH
spark meetings         # a quick manual sanity check
```

Set `email_provider: spark` and/or `meeting_provider: spark` when `/bigin-new-project` asks, or
edit `_bigin/system/project.md` directly afterward. There's no authorization step beyond being
signed in to the Spark desktop app itself.

### 4.4 Firefly (meetings, optional alternative to Fathom)

Same shape as Outlook: the plugin detects a connected Firefly MCP server but doesn't install
one. Connect it following Firefly's own MCP setup instructions, confirm with:

```
claude mcp list      # look for a row matching "firefl", state ✔ Connected
```

then set `meeting_provider: firefly` in your engagement config.

### 4.5 Open Design (prototype rendering)

Only needed if you want `/bigin-render-design-od` to render an interactive prototype later —
nothing on the requirements or design-spec path needs it. It's a desktop app; install it
yourself:

```bash
od mcp install claude
```

or, if that's not available:

```bash
curl -fsSL https://open-design.ai/install.sh | sh -s claude
```

On a macOS desktop install, prefer the Open Design app's own **Settings → MCP server**
snippet over the command line, per its own README. After installing, confirm it's connected:

```
claude mcp list      # look for a row containing "open-design", state ✔ Connected
```

`/bigin-new-project` runs this same check automatically and reports the install command back
to you if it's missing — it never runs the install itself, since it's third-party software
being installed on your machine, not a repo-local MCP registration. A missing Open Design
blocks nothing except the prototype-render step; `/bigin-generate-design` runs regardless.

## 5. Setting up a new engagement

Run this **once per repo**, before anything else:

```
/bigin-new-project [client name]
```

It will ask you for (or default) a handful of things:

| It asks for | What it means |
|---|---|
| Client name & contacts | who this engagement is for, and every address that counts as "client" mail |
| Your team's addresses | so a sweep can tell client mail from internal chatter |
| Email provider | `outlook` (default) or `spark` |
| Meeting provider | `fathom` (default), `spark`, or `firefly` |
| Project mode | `new` (greenfield) or `ongoing` (an existing product) |
| Platform | `web` (default), `mobile`, or `both` — shapes the design stage later, never the requirements |
| Whether to commit `_bigin/` | your call — it holds verbatim client communication |

What it does for you automatically:

- Copies the plugin's rulebook and templates into `_bigin/` in your repo, so every later stage
  and subagent has something project-relative to read.
- Writes a `CLAUDE.md` at the repo root, so any Claude Code session opened here — even outside
  a `/bigin-*` command — knows what this engagement is and what to run next.
- On a greenfield project, asks what's being built (or imports a proposal/SOW if you have one)
  and runs domain research on it up front.
- Checks that your configured email/meeting providers are actually reachable, and installs a
  missing MCP server automatically where it can (never anything beyond `claude mcp add` — no
  package managers, no credentials handled on your behalf).
- Checks whether the design engine your platform needs (Open Design) is installed. A missing
  engine **blocks nothing** except the optional prototype-render step later.

It's safe — and expected — to re-run `/bigin-new-project` later: after a plugin upgrade (to
refresh the materialized rulebook), or to edit a config field. It never touches your captured
intake, requirements, or PRDs.

## 6. The day-to-day workflow

The easiest way to run the pipeline is to **not** think about which command comes next —
just tell it what you want:

```
/bigin-run
```

Run it with no argument to sweep the whole vault ("what's next?"), or name a feature slug /
UC id to scope it ("what's next on checkout?"). It reads the vault, figures out which stage
is due, runs it, and keeps going automatically through anything that doesn't need a decision
from you. It only stops to ask when a decision is genuinely yours — approving a use case,
engagement config, or a prototype render.

If you'd rather run stages by hand, here's the order they normally happen in:

```
/bigin-intake              →  capture raw material (a meeting, an email, a note)
/extract-signal            →  turn captured intake into per-feature signals
/bigin-transform-signal    →  turn signals into drafted use cases + business rules
   (you review & answer open questions)
/approve-uc                →  sign off a use case once it's ready
/sync-entities             →  catch up entity/hub bookkeeping after approvals
/bigin-generate-design     →  produce a UX spec for anything newly approved
/bigin-render-design-od    →  (on request only) render an interactive prototype
/bigin-generate-prd        →  roll approved use cases into a per-feature PRD
```

### A typical morning

```
/bigin-intake
```

With no arguments and content to paste, it asks whether you're pasting something (`direct`)
or want a provider sweep. Left with nothing pasted, it sweeps your configured email and
meeting providers for anything new since the last run and files it into `00-Inbox/`,
untouched and verbatim — nothing is summarized at this stage.

```
/bigin-run
```

This drains the intake queue: extracts signals, drafts/updates use cases and business rules,
and reports back with exactly what changed and what — if anything — needs your input.

### Reviewing and approving a use case

When `/bigin-transform-signal` (or `/bigin-run`) drafts a use case, it may leave open
questions in the file itself, under `## 5 Open Questions & Decision Log`. You have two ways
to answer them:

**Live, in conversation** — just tell `/bigin-run` or the `bigin-ba` agent you're ready to
review, and it walks you through the open use cases one at a time, pools related questions,
and asks for approval once everything's settled.

**Offline, in the file** — open `01-Requirements/_ucs/UC-### <Title>.md`, find the question
under `## 5 Open Questions & Decision Log`, and type your answer on its `A:` line, in your
own words. Leave the checkbox unticked unless your answer actually settles it — "we'll ask
the client" doesn't count. Don't touch the numbered sections above it yourself; the pipeline
applies your answer there. Then say:

```
process UC-042
```

to `/bigin-run` (or name the feature instead of the id). It reads what you wrote, folds it in,
re-counts what's still open, and comes back once — either with genuine follow-up questions, or
an approval ask if you've cleared everything.

To formally sign off a use case once it's ready:

```
/approve-uc UC-042
```

### Generating a design

```
/bigin-generate-design [feature-slug | UC-### | omit for everything pending]
```

Runs automatically as part of `/bigin-run` once a use case has a drafted main flow — you
don't need to approve it first, and it never blocks on a missing design tool. It produces
screens, a navigation shell, and user flows using semantic roles only (no colours, no
component library) — an actual visual design system gets bound later, either by your design
team or at render time.

### Rendering a prototype (only when you ask for one)

```
/bigin-render-design-od [feature-slug ... | --all]
```

**This never runs on its own — only when a human asks.** It syncs the relevant UX spec, use
cases, business rules, and entities into an Open Design project, renders each feature, then
assembles everything into one interactive `index.html`, which gets copied back into
`04-UIUX/_prototypes/<date>-<slug>/` in your repo. Requires Open Design to be connected —
`/bigin-new-project` will have told you if it isn't.

### Generating the PRD

```
/bigin-generate-prd [feature-slug | UC-### | omit for everything ready]
```

Rolls every approved use case for a feature — its rules, entities, pain points, and design —
into one business-flow PRD. Fully headless; run it any time after an approval, no need to run
it after every single one.

## 7. Command reference

| Command | Use it to | Needs your input? |
|---|---|---|
| `/bigin-new-project [client]` | Set up (or refresh) an engagement | Yes — client/contact/config details |
| `/bigin-upgrade-project [check]` | Bring an existing project's rulebook up to a newer plugin version | No |
| `/bigin-intake [auto\|direct] <text\|path\|note>` | Capture raw material into `00-Inbox/` | No, unless prompted for a feature |
| `/extract-signal [resume]` | Extract signals from captured intake and file them onto feature hubs | No |
| `/bigin-transform-signal [feature\|resume]` | Draft/update use cases & business rules from filed signals | No — stages questions, never blocks |
| `/restructure-uc <UC-id> [split description]` | Split a use case that has outgrown one goal | Yes — you name the split |
| `/approve-uc <UC-id>` | Sign off a reviewed use case | **Yes — approval is always yours** |
| `/sync-entities [UC-id \| EN-id \| rebuild]` | Promote/refresh entities and hubs after approvals | No |
| `/enrich-feature <feature-slug>` | Manually refresh domain research for one feature | No |
| `/bigin-generate-design [feature\|UC-###]` | Produce/update a UX spec | No |
| `/bigin-render-design-od [feature... \| --all]` | Render an interactive prototype | **Yes — never run unasked** |
| `/bigin-generate-prd [feature\|UC-###]` | Roll approved UCs into a PRD | No |
| `/bigin-run [feature\|UC-id]` | Figure out what's next and run it | Stops only at real decisions |

Everything above is also reachable by dispatching the `bigin-ba` agent for unattended,
single-feature work — handy when you want one feature moved forward in the background while
you keep reviewing something else live.

## 8. Where things end up

```
_bigin/                    engagement config + the materialized rulebook (plugin-owned, refreshed on upgrade)
00-Inbox/                  raw captures, one INT-### file per intake, verbatim
01-Requirements/
  FEATURES.md              the feature registry — everything anchors to a row here
  _features/<slug>.md      one hub per feature: signal log, use cases, coverage gaps, entities
  _ucs/UC-### <Title>.md   one use case per user goal — the core requirement artifact
  _brs/BR-### <Title>.md   one business rule per file
  _entities/EN-### <Title>.md   promoted, fully data-modeled entities
04-UIUX/UX-### <Feature>.md    UX spec per feature: screens, flows, navigation
04-UIUX/_prototypes/<run>/     a rendered prototype, once you've asked for one
02-PRD/PRD-### <Feature>.md    one PRD per feature, rolled up from approved use cases
```

A full field-by-field breakdown lives in [README.md](README.md#workflow).

## 9. Troubleshooting

**"workspace_version mismatch" / a stage warns or stops** — the plugin was upgraded since
this project was initiated. Run `/bigin-upgrade-project`. If it says the workspace is *ahead*
of the installed plugin instead, stop and check you're on the right plugin version — don't
push past that message.

**A provider sweep fails or is skipped** — check `_bigin/system/project.md` §
`Provider readiness`. `/bigin-new-project` records the last known state per provider; for an
OAuth-gated one ("needs authentication"), authorize it in claude.ai connector settings, or via
`/mcp` for a non-connector MCP server. `/bigin-intake direct …` always works regardless.

**`/bigin-render-design-od` halts** — it needs Open Design connected. Install with
`od mcp install claude`, or see the app's own Settings → MCP server instructions. Nothing else
in the pipeline needs it.

**A write gets rejected with a lint finding** — `hooks/bigin-lint.py` checks structural
invariants (duplicate IDs, malformed tables, bad statuses) on every write into `00-Inbox/` or
`01-Requirements/`. The finding is fed back to whichever stage made the write — that's the
hook doing its job, not a bug. If it's noisy, ask whoever manages the plugin about
`BIGIN_LINT_ADVISORY=1`.

**The hook doesn't seem to be running at all** — hooks load once, at session start. Restart
Claude Code after installing/upgrading the plugin, and confirm with `/hooks`.

**Project-specific overrides** — house style, a standing feature-slug shortcut, a different
domain-research method — go in `.claude/bigin-ba-workflow-plugin.local.md` (scaffolded empty
by `/bigin-new-project`). Never edit the materialized files under `_bigin/conventions/` or
`_bigin/stages/` directly — they're overwritten on every upgrade.

## 10. Getting help mid-session

If you're ever unsure what a command actually does or reads, `/bigin-run` and the `bigin-ba`
agent both re-read that stage's own `SKILL.md` rather than guessing — you can ask either one
"what does approve-uc do?" and get the current behavior, not a stale summary.
