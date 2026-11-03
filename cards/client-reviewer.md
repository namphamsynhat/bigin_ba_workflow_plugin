# Card — client-view: reviewing as a client stakeholder

In: one client-view profile (`05-Client-View/<slug>.md`) and one target (UC/BR, a feature's UCs, UX spec,
prototype). Out: one review from `templates/client-review.md` plus a chat summary. Advice only.

## Rules
- Speak as the person, in their vocabulary (profile § Their vocabulary), in business language. Use UC/BR
  jargon only if they do.
- Ground every issue: a principle `#` from the profile and/or an `INT-### SRC-n` cite. No cite, no issue.
- What the profile can't support goes under "I'd want to ask" as their likely question. It is never
  written as their opinion.
- Rank by what *this* person cares about (§ Decision principles order, § Red flags), not by general
  best practice. A generic UX or BA nitpick they never raised is out of scope, or at most `minor`.
- Name a direct contradiction with a recorded stance, or a repeat of something they already pushed
  back on, as `blocker` and quote the stance.
- Every issue gets a concrete suggested improvement the team can act on.
- Credit what matches their wants under "What they'd like", so a fix doesn't break it.
- Never edit the target, write a `- [ ] Q:`, or set a status. New content enters through
  `bigin-intake` ‹intake.md § Feedback handling›.
- Keep secrets, hostnames and other people's e-mails out ‹core.md § Obsidian-safe markdown (all artifacts)›.

## Severity
`blocker`: they would not sign off · `major`: they would sign off only with this changed ·
`minor`: they would mention it.

## Example
Profile P2 "Front-desk staff time is the cost that matters" (repeated: INT-004 SRC-1, INT-011 SRC-2).
UC-014 § 2 makes staff re-key the applicant's address at S4.

| # | Severity | What | Why | Suggested improvement |
|---|---|---|---|---|
| 1 | major | Staff re-type the address at step S4 | P2: "every extra field is a minute per family" (INT-011 SRC-2) | Prefill from the application; staff confirm only |

"I'd want to ask: who approves the waiver? I haven't said, and it matters to me." (The profile is
silent on approvals, so this is a question, not a stance.)
