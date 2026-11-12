---
name: client-view
description: "Build or refresh a cited profile of one client stakeholder's point of view from everything they said in the vault, or review a use case, rule, feature, UX spec or prototype in that person's voice (saved as a dated review note; never edits the artifact). Use on \"build/update the client view for <person>\", \"review UC-012 as <person>\", \"what would <person> think of this\"."
argument-hint: "build|refresh <person> · review <UC-###|BR-###|feature-slug|UX-###|prototype path> as <person>"
---

# Client View — think like the client, review like the client

Two modes, one footprint: `{client_view_dir}` (`05-Client-View/`). Nothing else in the vault is written.

```text
build|refresh <person>
  in:    project.md § Client contacts, 00-Inbox/INT-*.md, UC/BR answers and Discussion entries
  out:   05-Client-View/<person-slug>.md  (from _bigin/templates/client-view.md)
review <target> as <person>
  in:    the profile + the target (UC/BR, a feature's UCs, UX spec, prototype)
  out:   05-Client-View/_reviews/<YYYY-MM-DD> <target> — <person-slug>.md  (from _bigin/templates/client-review.md)
         + a short chat summary
never:   edit the reviewed artifact, write a `- [ ] Q:`, set any status, or invent an opinion
```

Not to be confused with a **UX persona** (an end-user type in `/bigin-generate-design`): a client view
is one real stakeholder on the client's side, the person who signs the work off.

## Precondition — check this first

Missing `_bigin/conventions/core.md` or `_bigin/templates/` → stop, say `/bigin-new-project` must run
first. Missing `_bigin/templates/client-view.md` → recommend `/bigin-upgrade-project` and stop.

Then run `version-check.md` § Workspace version check. Behind → warn and recommend
`/bigin-upgrade-project`; ahead → stop.

**Resolve the person.** Match `<person>` (name, first name, or email) against `_bigin/system/project.md`
§ Client contacts and `client_emails`. Exactly one match → use it; the profile slug is the name,
kebab-cased (`anna-tran`). No match or several → list the client contacts and ask which one. A person
who is not a client contact (a team member) is refused: this skill models the client's view only.

## Mode: build / refresh

1. **Scope the evidence.** Read the existing profile's `read_through` (absent → build from scratch). List
   `00-Inbox/INT-*.md` newer than it whose frontmatter `participants` or whose `## Raw` blocks mention the
   person's name or email. Read frontmatter first; open a body only for a match. Skip `kind: info`.
2. **Take only what is theirs.** Per note, keep the person's own words and the decisions they made:
   - **Email** — messages whose sender is the person: reliable attribution.
   - **Jira** — comments and description revisions authored by them: reliable.
   - **Transcript** — a turn counts only when the attribution is unambiguous (named by others, or
     self-identified). Speaker labels merge voices (template `intake.md`, Source column), so a turn you
     can't pin to them is skipped, and one you can carries at most `inferred` confidence unless an
     email or Jira entry confirms it.
   - **Answers** — `A:` lines on UCs/BRs, and `## Discussion` entries attributed to them.
   - Others' summaries of what the person wants ("Anna wants…") count as `inferred` only.
3. **Read large sets one note at a time.** Over ~15 notes, extract each into a running list
   (claim · cite · date) before opening the next, so no more than one note body sits in context at once.
4. **Synthesise** into the template, instantiated from `_bigin/templates/client-view.md`
   (structure only, never the guidance comments):
   - Each **decision principle** is a general rule behind several remarks ("cost of staff time beats
     feature richness"), not a restated requirement. Every one cites evidence (`INT-### SRC-n`, or
     `INT-### #row` for an extracted signal) and gets a confidence level: `stated` (said outright),
     `repeated` (2+ independent sources), or `inferred` (read from behaviour or someone else's account).
   - **Never invent.** Whatever you can't support goes to `## Unknowns`, phrased as what we don't know.
   - **Shifts:** when they change their mind, keep both views with dates under `## Shifts over time`;
     the newer one is current everywhere else.
   - Quote their **vocabulary** verbatim; it is what the review voice uses.
   - Never copy e-mail addresses other than the person's own, phone numbers, hostnames or secrets.
5. **Refresh = update in place.** Revise affected sections, never drop a cited principle without saying
   why, set `read_through` to the newest INT read, update `sources_count` and `updated`, and append one
   `## Changelog` line: what was added, strengthened, weakened or reversed, and from which INTs.
6. **Report:** notes read, principles added/changed (with confidence), open unknowns, and one line on how
   well the evidence supports the profile (e.g. "4 emails, 1 attributable transcript — thin on design").

## Mode: review

1. **Load the profile.** Missing → offer to build it first, and stop. `read_through` behind the newest
   INT that involves the person → say how many notes it is missing and offer a refresh. Review on the
   stale profile only if the user says so, and note it in the review's `## Notes for the team`.
2. **Resolve the target and read it whole:**
   - `UC-###` / `BR-###` — the file, its feature hub, the BRs it cites, its open questions.
   - a feature slug — every UC on the hub in flow order (`cards/ba-review.md` § Scope by flow), with its BRs.
   - `UX-###` — the spec in `04-UIUX/`, plus the UCs it cites for context.
   - a prototype — `04-UIUX/_prototypes/<render>/index.html` and its `screens/`; when screenshots or
     rendered frames exist, read them as images as well, since layout is what a client reacts to.
3. **Review in role,** following `_bigin/cards/client-reviewer.md` (or `<plugin>/cards/client-reviewer.md`).
4. **Write the review** from `_bigin/templates/client-review.md` to `{client_review_dir}`, then summarise it
   in chat: the verdict, the top 3–5 issues with their why, and the count of "I'd want to ask" points.
5. **Close with the path in:** "To act on these, capture the points you agree with as feedback
   (`/bigin-intake direct`), or answer them on the UC." The review is advice. The pipeline stays the only
   way content changes.

## Rules

- **Footprint:** `05-Client-View/` only. Never a UC, BR, hub, INT, UX spec, prototype, ledger or status.
- **Evidence or silence:** every principle and every review issue traces to a cite. An unsupported
  reaction is written as a question the person would ask, never as their opinion.
- **One person per profile.** If two client contacts disagree, that disagreement is a finding: name it in
  `## Notes for the team` when reviewing as either of them.
- **Human-only use of the output.** A review never feeds an agent's change set directly; a person decides
  what becomes feedback.
