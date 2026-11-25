# Bigin BA

A Claude Code plugin that keeps the development team's **second brain**: one folder of plain Markdown
that holds what the client said, what was decided, and what will be built.

It captures client communication and Jira tickets, turns them into use cases, rules, designs and
stories, and traces every line back to its source. AI does the writing. **A person approves.**

```
capture ─► extract ─► draft ─► approve ─► design ─► approve ─► stories ─► approve ─► build
 intake     signals   use cases  (person)  screens +  (person)  epic +     (person)
                      + rules              prototype            stories
```

## Install

```
/plugin marketplace add https://github.com/namphamsynhat/bigin_ba_workflow_plugin.git#v2
/plugin install bigin-ba@bigin
```

Version 2 lives on the `v2` branch. Version 1 (`bigin-ba-workflow-plugin`, last release 1.14.0) stays on
`main` and on the `v1` branch. A version 2 vault cannot be read by version 1, or the other way round.

To try a local copy: `claude --plugin-dir /path/to/this/folder`.

Needs Python 3.9 or newer (`python3`). For Jira intake, connect an Atlassian MCP server. For meetings,
connect Claude Meetings (or another transcript tool). For email, connect any mail tool. Without them, paste the text or give a file.

## Daily use

| When | Run |
|------|-----|
| Once per project | `/bigin-ba:setup` |
| New material arrived | `/bigin-ba:intake` — paste text, give a file, name Jira keys, or `sweep` |
| "What now?" | `/bigin-ba:next` — runs every step that needs no person, then reports |
| Ready to review | `/bigin-ba:approve <feature>` — one session: answer by choice, read the review cards, decide |
| "What did the client say about …?" | `/bigin-ba:ask <question>` |
| Build an MVP to show the client | `/bigin-ba:handoff <feature>` — a folder your development plugin builds from |
| "What would the client think of this?" | `/bigin-ba:client-view build Anna`, then `review UC-003 as Anna` |

The single steps, if you want to run one by hand: `/bigin-ba:extract`, `/bigin-ba:draft`,
`/bigin-ba:design`, `/bigin-ba:stories`.

## What the vault looks like

```
bigin.md                  project settings and contacts
INDEX.md                  generated: everything that exists, and what is waiting
00-inbox/                 INT-### notes — the source, word for word, plus its signals
01-requirements/
  GLOSSARY.md             the project's terms
  features/               one page per feature
  use-cases/              UC-### — one user goal each
  rules/                  BR-### — one business rule each
  entities/               the data dictionary
02-design/                UX-### — screens and flows; prototypes/<feature>.html
03-stories/               EP-###/ — an epic and its US-### stories
04-clients/               one profile per client person, and reviews written as them
05-handoff/               generated build packs, one folder per feature
```

## How review works

- **Nothing is guessed.** A missing fact becomes an open question with an owner: client, team or dev.
  Type the answer on its `A:` line, then run `/bigin-ba:next`: it writes the answer into the text.
  `bigin questions --owner client` lists what to send.
- **One question, one place.** A question about one use case sits in that use case. A question about
  several sits on the feature page and names them, so one answer there frees them all.
- **Few questions, visible assumptions.** Only a real decision becomes a question, at most 5 per file.
  A detail with a sensible default is written as an assumption, with its reason, and you confirm the
  list when you approve. `bigin assumptions --owner client` prints the list to send.
- **The work never waits for a yes.** A default that changes how the client works is a proposal:
  "We plan to do X. Is that right?" The use case, design and prototype go ahead as proposed. Only the
  stories wait for the answer. `bigin questions --kind confirm` prints the yes/no list.
- **You read a card, not a file.** `bigin card UC-003` shows the summary, what changed since the last
  approval, the questions with their choices, and the assumptions. The steps that name a source are
  counted, not shown; the full text is one word away. Use cases and stories start with a summary.
- **Everything is traced.** Each step names its source (`INT-004 #3`). Each design and story names the
  use-case version it was built from. When a use case changes, `bigin status` lists what is now stale.
- **Approval is yours.** Only `/bigin-ba:approve`, run by a person, sets `approved`. A change to an
  approved file sets it back to `draft`.
- **MVP.** `/bigin-ba:handoff` writes a build pack from the approved use cases: brief, use cases with
  full rule text, data, screens, acceptance scenarios, and the list of what may still change. It may
  go out with unconfirmed proposals. Point any development plugin at its `README.md`.
- **Hand-off.** A story holds its flow, screens, full rule text and acceptance criteria. Give the file
  to the developer or their coding agent.

## What is inside the plugin

| Path | What |
|------|------|
| `skills/` | eleven skills: `setup` `intake` `extract` `draft` `approve` `design` `stories` `handoff` `next` `ask` `client-view` |
| `agents/` | `signal-extractor` (reads one note) · `spec-reviewer` (independent second reading) |
| `reference/rules.md` | the one rulebook every skill and agent reads |
| `templates/` | one template per file type |
| `bin/bigin` | a small Python helper: ids, file copies, checks, status, approval. No AI. `bigin --help` |
| `hooks/hooks.json` | after each write to a vault: check the file, refresh `INDEX.md` |
| `tests/` | `python3 -m unittest discover tests` |

To change how the plugin behaves, edit `reference/rules.md` first: it is the single source of the rules.

See [NOTES.md](NOTES.md) for what changed from version 1 and what is still open.
