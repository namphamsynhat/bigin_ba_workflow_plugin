---
name: intake
description: Captures raw client communication into the vault inbox, word for word - a pasted note, a file, an email thread, a meeting transcript, or a Jira ticket with its comments. Use when new material arrives, at the start of the day to pull what is new, or when the user names a Jira key or sprint to track.
argument-hint: "[pasted text | file path | Jira key(s) | meeting name | 'sweep']"
---

# Capture intake

Put the source into `00-inbox/` exactly as it is. Do not summarise, clean up or interpret.
Read `${CLAUDE_PLUGIN_ROOT}/reference/rules.md` first.

## Steps

1. **Find what to capture** from `$ARGUMENTS`:

   | Given | Do |
   |-------|----|
   | pasted text | capture it as one block |
   | a file path | `bigin new int "<short title>" --file <path>` copies it in. Do not retype a file |
   | Jira key(s) | read [jira.md](jira.md) and follow it |
   | a meeting (name, date or link) | read [meetings.md](meetings.md) and follow it |
   | `sweep`, or nothing | pull what is new since the newest note: Jira ([jira.md](jira.md)), meetings ([meetings.md](meetings.md)), then email from the contacts in `bigin.md` with whichever mail tool is connected |

   If no tool can reach a source, say so and ask the person to paste it. Never capture from memory.
2. **Check it is not already captured.** Search `00-inbox/` for the same `source_ref` or `jira_key`.
   Found → add only the new material to that note as a new block, and set its `status` back to `raw`.
   For a file: `bigin attach INT-### <path>`.
3. **Create the note** for new material: `bigin new int "<short title>"` (with `--file <path>` for a file).
4. **Fill the note:**
   - frontmatter: `source` (`email` · `meeting` · `jira` · `file` · `direct`), `source_ref` (subject,
     meeting name, link or file name), `date` (when it was said), `people`
   - `## Raw`: one block per source — `### SRC-1 · <kind> · <who, date or link>` — then the full text.
     A block made from a file holds a link to the copy in `00-inbox/files/`; that copy is the source.
     Read it to fill the frontmatter, the speakers and the Log. Do not paste it into the note
   - `## Log`: one line for what you captured, and one for anything you could not fetch
5. **Report** the note ids. The next step is `/bigin-ba:extract`.

## Rules

- A meeting needs its full transcript, with speaker labels and timestamps as the tool gives them. An AI
  recap goes in its own block marked `summary`; it is never quoted as a source.
- For a meeting, say who is who. Match each speaker label to a contact in `bigin.md` and write it in
  `## Log`: `speakers: Speaker 2 = Anna Tran (client), Speaker 1 = Minh (team)`. If a label is not
  clear, ask the person once. This line is what lets `/bigin-ba:client-view` learn from the meeting.
- List things the source points to but does not contain (a linked sheet, a file shown on screen)
  in `## Log` as `not captured: <what> — <how to get it>`.
- Leave `## Signals`, `## Analysis` and `## Open questions` empty. They belong to extract.
- Read-only: never mark mail as read, reply, or change a ticket.
