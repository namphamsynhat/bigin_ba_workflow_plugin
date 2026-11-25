---
name: next
description: Works out what the vault needs next and does it - extract raw notes, draft from waiting signals, refresh stale designs and stories - and keeps going until a person must decide something. Use for "what's next", "process the inbox", "move this feature forward", a daily catch-up, or a status report on the project.
argument-hint: "[feature slug | omit for the whole vault]"
---

# Do the next step

Read the state, run the next step, repeat. Stop when the next step belongs to a person.

## Steps

1. Run `bigin status $ARGUMENTS`. If it says there is no vault, tell the person to run
   `/bigin-ba:setup`, and stop.
2. Take the first line of the output that has work, and run its skill:

   | Line starts with | Run |
   |------------------|-----|
   | extract | `/bigin-ba:extract` |
   | draft | `/bigin-ba:draft` |
   | apply | `/bigin-ba:draft` — a person answered; write the answers into the text |
   | answer | nothing — list the questions by owner; a person answers |
   | confirm | nothing — list the proposals; the work goes on, only the stories wait |
   | approve | nothing — name the features; a person runs `/bigin-ba:approve <feature>` |
   | design | `/bigin-ba:design` |
   | stories | `/bigin-ba:stories` |
   | refresh | `/bigin-ba:design` or `/bigin-ba:stories` for the stale file |

3. After an extract: for each client person who spoke in the new notes and has a profile in
   `04-clients/`, run `/bigin-ba:client-view build <person>` so the profile stays current.
4. Run `bigin status` again. Go on with the next line that has work you may do.
5. Stop when only `answer`, `confirm` and `approve` lines are left, or when nothing is waiting.

## Report

End with a short report:

- **Done:** steps run, files created or changed
- **Waiting on people:** questions by owner (`bigin questions`), proposals to confirm, and ids ready to approve
- **Next:** the one thing the person should do now

## Rules

- Never approve. Never answer a question for a person.
- If the person asked for new material ("pull Jira", "check email"), run `/bigin-ba:intake sweep` first.
- If `bigin status` reports check errors, run `bigin check` and fix them before anything else.
