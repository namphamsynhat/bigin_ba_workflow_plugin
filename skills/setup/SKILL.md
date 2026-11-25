---
name: setup
description: Creates the Bigin BA vault (the team's second brain) in the current folder and fills in the project settings. Use once per client project, or again to change a setting such as contacts or the Jira project.
argument-hint: "[client name]"
disable-model-invocation: true
---

# Set up the vault

Create the vault, then fill `bigin.md` with what the person tells you.

## Steps

1. Run `bigin init`. It creates the folders, `bigin.md`, `CLAUDE.md` and the glossary. It never
   overwrites a file that exists, so it is safe to run again.
2. Read `bigin.md`. Ask only for the fields that are still blank, in one batch:
   - client name (`$ARGUMENTS` if given)
   - what is being built and for whom, in a few sentences
   - platform: `web`, `mobile` or `both`
   - client contacts and team contacts (name, role, email)
   - Jira: site, project keys, and which ticket statuses mean "ready to build" — or no Jira
   - the path to the product's code, if the product already exists
   - the folder for build packs in the code repository (`handoff_path`), if an MVP will be built
3. Write the answers into `bigin.md`. Leave a field blank when the person does not know. Never guess.
4. Check the connections this project needs and report each as connected or missing:
   - Jira: an Atlassian MCP tool is available.
   - Meetings: Claude Meetings, or another meeting-transcript tool.
   - Email: any connected mail tool.
   A missing connection blocks nothing. `/bigin-ba:intake` also takes pasted text and files.
5. Tell the person the next step: `/bigin-ba:intake`.

## Rules

- Do not create features, use cases or notes here.
- The vault holds client communication. Ask whether it may be committed to git before any commit.
