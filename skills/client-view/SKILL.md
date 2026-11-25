---
name: client-view
description: Builds a sourced profile of one client person from everything they said in the vault - what they want, how they decide, what they pushed back on, the words they use - and reviews a use case, rule, design, prototype or story as that person would. Use for "build the client view for Anna", "review UC-012 as Anna", "what would the client think of this", or before sending work to the client.
argument-hint: "build <person> | review <id, feature or prototype path> as <person>"
---

# Client view

Learn how one client person thinks, then read our work through their eyes.
Read `${CLAUDE_PLUGIN_ROOT}/reference/rules.md` first.

The person must be a client contact in `bigin.md`. If the name matches none or several, list the
client contacts and ask. One profile per person: `04-clients/<name>.md`.

## Build or refresh a profile

1. Open the profile, or create it: `bigin new client "<Full name>"`.
2. Find the notes in `00-inbox/` that involve the person and are newer than `read_through`.
3. From each note, take only what is theirs:

   | Source | Counts as theirs |
   |--------|------------------|
   | meeting transcript | their turns, found through the `speakers:` line in the note's `## Log` |
   | email, Jira comment | what they wrote |
   | answered question | an `A:` line that names them |
   | someone else saying "Anna wants…" | `inferred` only |

   Meetings are the main source: read the whole transcript, not the recap. When the block links to a
   file in `00-inbox/files/`, the transcript is that file. If a meeting note has no
   `speakers:` line, ask the person who is who, add the line, then go on. Never guess a speaker.
4. In a meeting, look for more than requirements. Note, with the timestamp:
   - what they raise by themselves, and what they come back to more than once
   - the questions they ask, and what they ask first
   - what they agree to fast, and where they slow down, object or ask for proof
   - the reason they give for a decision ("because …")
   - what they wave away as not important

   Steps 3 and 4 collect evidence. Keep that list in your working notes. It is not the profile.
5. Write the profile as [The profile](#the-profile) says: what we now know about the person, not a
   list of what they said.
6. When they changed their mind, keep both views with dates under `Changes of mind`.
7. What the notes do not show goes under `Unknowns`. Never invent an opinion.
8. Set `read_through` to the newest note read and `based_on` to the evidence behind the profile
   ("3 meetings, 4 emails"). Add one Changelog line: the notes read and what changed in our view of
   the person.
9. Report in the chat: notes read, principles added or changed, how strong the evidence is
   ("3 meetings, 4 emails — little on design"), and any problem with a source.

## The profile

The profile is finished knowledge. A teammate who reads only this file must know how to deal with the
person. The transcripts hold the evidence; the profile holds what we concluded from it.

| Section | Holds |
|---------|-------|
| In short | At most 120 words, no ids: who they are, what they want, how they decide, and what to do when we show them work. Rewrite it at every refresh. |
| Who they are | Role, what they are responsible for, what they sign off. |
| What they want | The business results they are after, not features. |
| What they care about most | Topics they raise by themselves or come back to, strongest first. One line each: the topic, and what they want from it. |
| How they decide | The pattern behind several remarks, strongest first. Never one requirement repeated. Each row says what the team must do because of it, and gives the one quote that shows it best. |
| What they pushed back on | What they rejected or corrected, and the reason they gave. |
| How they review | What they look at first, the questions they ask, what makes them confident. |
| Their words | Their own term, and what they mean by it. Words that are not theirs. |
| Changes of mind | `<date> — earlier view → newer view`. The newer view is the current one. |
| Unknowns | What we cannot tell yet, written as what we would ask them. |

Writing it:

- **Conclude.** Each line is one conclusion in our words that a teammate can act on. Do not retell
  the meeting, and do not list remarks one by one.
- **Quote only where their exact words matter:** one quote per principle, their terms, and a rejection.
- **Source every line, shortly.** End the line with the notes behind it: `(INT-001, INT-005)`. Give the
  exact place only after a quote: `(INT-005 SRC-1 [18:17:48])`. Never a list of timestamps.
- **Mark only the weak lines.** No mark means they said it. `(inferred)` means we read it from their
  behaviour or from someone else's account. `(said once, not firm)` means exactly that.
- **One fact, one line, one section.** At a refresh, rewrite the line a new note changes and add the
  note to its source. Do not add a second line beside it.
- **Keep it short.** At most 8 lines in a section and 10 principles. When a stronger line comes in,
  the weakest goes out.
- **Principles keep their number.** Reviews cite them. A principle that no longer holds reads
  `Dropped — <reason>`.
- **Leave out the working notes:** how often something was said, how the notes were read, defects in a
  source (missing lines, a bad recording), and notes that held nothing of theirs. Those go in the report.
- **No comments or placeholders** stay in the file.

## Review as the person

1. Read the profile. Missing → offer to build it, and stop. Notes newer than `read_through` → say how
   many, and offer a refresh first.
2. Read the whole target: the file and what it cites. For a feature, all its use cases in flow order.
   For a prototype, the HTML file and its design.
3. Write the review from [review-template.md](review-template.md) to
   `04-clients/reviews/<date>-<target>-<name>.md`:
   - Speak as the person, in their words, in business language.
   - Every issue names the principle or quote behind it. No source, no issue.
   - Rank by what this person cares about, not by general good practice.
   - Something they already rejected, showing up again, is a `blocker`. Quote what they said.
   - A reaction the profile cannot support goes under "I would ask", as a question.
   - Each issue has a concrete fix the team can make.
4. Show in the chat: the verdict, the top issues with their reason, and the number of "I would ask" points.

## Rules

- This is a prediction, not the client's answer. It never replaces a real approval or a real reply.
- Write only inside `04-clients/`. Never edit the reviewed file, add a question to it, or set a status.
- To act on a point, the person captures it with `/bigin-ba:intake` or fixes the draft themselves.
- Keep other people's email addresses, phone numbers and secrets out of the profile.
