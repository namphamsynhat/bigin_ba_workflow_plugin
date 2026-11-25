# Rewrite notes

Version 2.0.0, a full rewrite of `bigin_ba_workflow_plugin` 1.14.0. It lives on the `v2` branch;
version 1 stays on `main`, on the `v1` branch and in the `v1.14.0` release.

## What changed, and why

| Version 1 | Version 2 |
|-----------|-----------|
| 17 skills, 9 agents, 14 role cards, 19 convention files, 16 stage guides | 11 skills, 2 agents, 1 rulebook (`reference/rules.md`) |
| A 20,000-line Python engine: change sets, ledger, worklists, migrations | One 1,100-line script (`bin/bigin`): ids, file copies, checks, status, approval |
| Rulebook copied into every project (`_bigin/`), with an upgrade skill | Rules stay in the plugin. A plugin update needs no project upgrade |
| Signals kept twice (note table and feature Signal Log) | Signals kept once, on the intake note |
| Hub tables kept in sync by the engine | One generated `INDEX.md` |
| Review cards, estimate sheet, build pack, Jira paste text | The story file is the hand-off: it holds everything those held |
| Open Design for prototypes | One self-contained HTML file per feature, no extra tool |

The ideas kept from version 1: capture word for word, never guess, questions with an owner, permanent
ids, a trace from every line to its source, "AI assumed" lists, stale flags, delta stories, Jira as a
living read-only note, and approval only by a person.

## Checked

- `python3 -m unittest discover tests` — 27 tests pass (ids, file copy, checks, questions, approval,
  status, stale, hook).
- `claude plugin validate .` — passes.
- Plugin facts (`bin/` on PATH, `${CLAUDE_PLUGIN_ROOT}` in skill text, hook output, frontmatter fields)
  were checked against the current Claude Code docs.

## Test run on FlightFault (2026-11-21)

A fresh version 2 vault, fed with five real sources from the FlightFault project: the first meeting,
the client's workflow spec, a BA review note, the BA's answers, and the demo call transcript. Each skill
ran in its own headless Claude Code session with only this plugin loaded. The FlightFault folder was
only read.

| Step | Result |
|------|--------|
| setup | Vault created, `bigin.md` filled. `bigin` was on the PATH. |
| intake | 5 notes. Speakers matched to contacts. It found by itself that one speaker is on the client side. |
| extract | 477 signals, 18 features proposed, 40 questions, 7 real conflicts found. A script confirmed that all 477 quotes are in their source word for word. About 14 minutes. |
| draft (one feature) | 2 use cases, 3 rules, every step sourced, 17 questions. About 6 minutes. |
| answer round | I typed 2 answers and ran `next`. One answer was written into 2 use cases and 1 rule. |
| client-view build | A profile of the client lead: 10 principles, 2 changes of mind, 12 unknowns, all sourced. |
| client-view review | UC-002 read as the client lead: "sign-off with changes", 5 issues, each with their own quote, 6 "I would ask" points. |
| design | 2 screens and a clickable prototype for the one approved use case, 7 questions. The reviewer agent caught that "Fix now" was styled as the main button, against a rule. I did not open the prototype in a browser. |
| stories | 1 epic, 3 stories with acceptance criteria and full rule text. The check caught 2 questions asked again that the use case had already answered. |

To get an approved use case for the last two steps, I closed its questions with a dummy test answer and
ran `bigin approve` myself. The whole run cost about 35 USD of model use; extract was 12 of it.

What the test changed in the plugin:

1. **Files are copied, not retyped.** The first intake made the AI retype a 29 KB transcript. Now
   `bigin new int --file` copies the file into `00-inbox/files/` and the note links to it.
2. **Raw text is not checked.** Source text that names ids (`UX-012`) no longer causes check errors.
3. **Quotes are checked.** `bigin check` warns when a signal's quote is not in its source.
4. **Questions have one home.** See rules section 5: a question on the feature page names the use
   cases it holds, an answer is "applied" by draft, and approval waits for both.
5. **`bigin status` is short.** It shows counts per feature, not every row.
6. **`design` signals no longer keep `draft` busy for ever.**

Seen in the test, not changed:

- **Many questions — fixed and re-tested.** The first draft of one feature asked 24 client questions
  for 2 use cases. Rules section 5 now makes the AI sort every gap first: park it, assume it with a
  reason, or ask. At most 5 client questions per file. The same feature, drafted again: 1 question,
  12 written assumptions (6 for the client to confirm, 6 team calls) and 5 parked items. The risk is
  now the other way: read the assumptions when you approve, because approving confirms them.
- **Proposals to confirm (added after the test, 2026-11-21).** A middle level between a question
  and an assumption: our default is written into the text and the client only says yes or no. An
  unanswered proposal warns at approval and stops only the stories, so the requirement, design and
  prototype can go to the client first. At review, a person may also give a working answer to an open
  question, which turns it into a proposal. The same feature drafted again: 1 open question, 3 proposals, 20 assumptions; the use case
  with only proposals could be approved, with a warning. Design and stories were not re-run. Two
  small things this run showed, not fixed: a parked signal has no status of its own, so the AI wrote
  two "not in the first build" rules to hold it; and `A1` names both an assumption and an alternative flow.
- **Build pack for an MVP (added 2026-11-23).** `/bigin-ba:handoff <feature>` and `bigin pack` write
  `05-handoff/<feature>/` from the approved use cases and can copy it into the code repository. It is
  not tied to one development plugin: the pack is plain Markdown with a `README.md` that lists the
  files and what they were built from. Once a plugin is chosen, add its import format if it needs one.
- **Less to read at review (added 2026-11-23).** Developers said the files are too long to read. Now:
  a review card (`bigin card`) shows only what needs a person; use cases and stories start with a
  summary of at most 120 words; questions carry answer choices; `/bigin-ba:approve <feature>` reviews
  a whole feature in one session. The risk: a person approves steps they did not read. The card says
  how many, and the second reader checks the summary against the details.
- **Client profile reads as knowledge (changed 2026-11-23).** The first profile of the client lead read
  like working notes: every remark with its timestamps, counts of how often, and notes on the
  transcript. Now the profile starts with `## In short`, each line is a conclusion with a short source,
  each principle says what it means for our work, and working notes go in the chat report. The
  profile in the test vault was rewritten by hand to the new shape; `client-view build` was not re-run.
- **Many features.** Extract proposed 18 features for this project (version 1 had 13). The skill asks
  the person before it creates a feature; in the test I told it not to ask.
- **Cost.** Extracting two long sources (a 400-line spec and a 47-minute call) is the expensive step.

## Not checked — please test

1. **Jira.** `skills/intake/jira.md` names no specific MCP tool, so it works with whichever Atlassian
   server is connected. It has not been run against your Jira.
2. **Meetings.** `skills/intake/meetings.md` has exact steps for Claude Meetings, written from its tool
   descriptions but not run on a real meeting. The test used transcript files.
3. **Email sweep.** Version 1 had exact steps for Outlook and Spark. Version 2 says "use the connected
   mail tool". If the sweep is unreliable, add a short file next to `jira.md`.
4. **Windows.** `bin/bigin` is a Python script with a `#!` line. It works on macOS, Linux and Git
   Bash. Plain `cmd.exe` may need a `bigin.cmd` wrapper.
5. **`/bigin-ba:approve` as a conversation.** The test approved with `bigin approve` directly.

## Decisions I need from you

1. **Old projects.** Version 2 cannot read a version 1 vault (new folder names, new file layout).
   Options: keep old projects on version 1, or I write a one-time converter. Which do you want?
2. **Design before approval.** Version 1 designed from draft use cases. Version 2 waits for approval,
   unless the person asks. Say if your team needs the old order for Jira tickets.
3. **Jira gate.** Version 1 blocked approval until the ticket reached "Ready for Dev". Version 2 only
   warns (`jira_ready_statuses`). Say if it should block.
4. **Name.** The plugin is `bigin-ba`, so commands read `/bigin-ba:intake`. The marketplace is `bigin`.
5. **Model per agent.** Version 1 fixed every agent to Sonnet. Version 2 uses the session's model.

## Left out on purpose

Tell me if any of these is needed; each can come back as one small skill.

- Importing rules mined from code, and settling conflicts against the code (`grounding: codebase`).
  Version 2 only reads the code to answer a dev question.
- Automatic domain research for a new feature.
- The estimate sheet and the question packs in `06-Outbox/` (now: `bigin questions --owner client`).
- Sprint watch lists and the sprint report. A sweep reads every ticket that already has a note.
- Token metrics, run records, backups and the golden-set evaluation. Use git for history.
- Confluence pages as living notes.

## Known limits

- `/bigin-ba:client-view` learns mostly from meetings. It needs the full transcript and a `speakers:`
  line that says who is who; intake asks for it. If your meeting tool gives no speaker labels at all,
  the profile can only use emails and Jira comments. Files in `04-clients/` are not checked by `bigin check`.

- `bigin` trusts the files. It cannot see a content edit to an approved file if `version` was not
  raised. The rules tell the AI to raise it; git diff is the real record.
- Two people creating files at the same moment can get the same id. `bigin check` reports it.
- A file fresh from `bigin new` has no open question, so `bigin status` lists it as ready to approve
  until it is filled in.
