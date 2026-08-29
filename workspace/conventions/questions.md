# Conventions — open questions

How a question is worded, where its two copies live, and the consistency rule that ties an open
question to the artifact status it blocks.

**Read by** every stage that can raise or resolve a question — `/extract-signal`,
`/bigin-transform-signal`, `/bigin-generate-design`, `/bigin-generate-prd`.

## Open Questions ↔ status consistency (verification, not just intent)

`status: needs-clarification` and the artifact's own question list are two mirrors
of one fact — that list is `## 5`'s **Still open** section on a use case, and `## Open Questions` on an
INT note or a BR — the same drift risk as a stale Feature Hub Signal Log `Status` column left
`question` after its UC absorbed the row (`feature-hub.md` § Feature Hub), just on the `status:`
frontmatter/body pairing instead. A human reads whichever surfaces first (a queue badge reads
`status:`; opening the note reads the section body) and both must agree, or the note reads as
done in one place and stuck in the other.

**The invariant:** zero unchecked `- [ ] Q:` lines in that list (INT note, UC, or BR) ⟺
`status` is not `needs-clarification`. Any unchecked line ⟺ `status` **is**
`needs-clarification`. This holds for every artifact that carries one — INT notes, use cases, and BRs
alike. **A use case's decision-log rows are not open items**: they are settled history, and counting
them would park a finished UC at `needs-clarification` forever.

Every skill that writes to a question list or sets `status` on such an artifact
(`/extract-signal`, `/bigin-transform-signal`) must make the status line the
**last** write-back step, derived by re-counting the section **after** every accepted change has
been applied to it that run — never decided earlier in the run and then left stale by a later
edit to the same section:

1. Apply every accepted change to the question list first (tick resolved boxes with `A:` filled, append
   genuinely new ones; on a use case, move a genuinely resolved line into the `## 5` decision log).
2. Count remaining unchecked `- [ ] Q:` lines in that list.
3. Set `status: needs-clarification` if the count is > 0; otherwise move it to whatever "done"
   means for that artifact type (`in-review` for an INT note; whatever stage the UC/BR was
   already at — `draft` if it hasn't been enriched yet — for a UC/BR, `core.md` § Status vocabularies).
   Do this from the count, not from memory of what the run intended to resolve.

**Common ways this drifts** (treat each as the bug it is, not a cosmetic gap): ticking every box
while `status` still reads a stale `needs-clarification` from before the run; flipping `status`
off `needs-clarification` while a `- [ ] Q:` line — even one raised earlier in the same session
and forgotten — is still unchecked in the body; ticking a box that isn't genuinely resolved (an
answer that still needs a client round-trip stays unchecked, and `status` stays
`needs-clarification`, even if every *other* question closed) just to make the count zero.

## Open Questions wording (all artifacts)

An Open Question gets read cold — by a client, or by whoever picks up the vault days after it was
drafted — with none of the drafting context loaded. **It must be self-contained.** The failure
mode: a question that only makes sense to whoever just wrote it, because it references an internal
number without restating what that number means — e.g. "Does UC4's Organization Experience
narrative-question set *replace* UC-004 S23's single" (which "UC4"? the fourth item in *this* note,
or the `UC-###` artifact id? "S23's single" — single *what*?). This
applies wherever `/extract-signal` or `/bigin-transform-signal` write a
`- [ ] Q: …` line, on an INT note or a UC.

**Format:**

```
- [ ] Q: <How it works today — plain business language, no ids.> <What the new request changed —
  plain business language.> <The one decision needed, as its own question sentence: yes/no,
  A-or-B, or an (a)/(b)/(c) list when there are three or more options.> (owner: client|team)
  (ref: UC-###, BR-###, INT-### — traceability only, safe to ignore when answering)
```

**Rules — content:**

- **Quote or tightly paraphrase both sides in plain business language** — the requirement as it
  stands today, and what the new signal proposes — before asking anything. Never point at a bare
  internal number ("FR4", "FR23", "BR-104") as if it's self-explanatory; if a number is cited for
  traceability, always pair it with what it says ("FR3 — the vendor must submit a W-9 before
  payout"). Where the readability rules below send ids to the trailing `(ref: …)` instead, they
  need no gloss there — that block is pure traceability the answerer skips; the pairing rule
  governs any id that appears in the ask itself.
- **End with one concrete, answerable question** — a yes/no or a named choice ("replace or
  supplement?", "which one wins?") — not a sentence fragment or a dangling clause.
- **One question, one decision.** Don't compress two ambiguities into a single run-on question;
  split them into separate `Q:` lines instead.
- **Never assume the reader has the note open elsewhere.** The question must stand alone even if
  it's the only line anyone reads.

**Rules — readability.** Pairing every id with its meaning is necessary but *not sufficient*: a
question can satisfy every rule above and still be unreadable, because it's written in vault
register — dense with ids, in one long sentence, using vocabulary coined while drafting. So also:

- **Write in the register of the question's `owner`.** `owner: client` means this line will be
  read — often pasted verbatim into an email — by someone outside the vault. No ids in the ask
  itself, and none of the vault's own vocabulary: no *signal*, *CR*, *intake*, *staged*,
  *fold-in*, *bucket*, *UC/BR/INT/PP/EN*. Push every id into the trailing `(ref: …)` parenthetical
  where a reader can skip it. `owner: team` may use ids inline — still always paired with what
  they say.
- **Use only the client's own words for the business concepts.** Never invent a term to compress
  something ("the 20% cap bucket", "the narrative-question set") unless the client or the source
  document actually used it. If you need a name for a group of things, list the things.
- **Three short sentences, and the question is one of them.** Today → what changed → what we need
  decided. Never bury the ask behind a *but*, an em-dash, or a subordinate clause on the end of a
  statement — a reader scanning for "what am I being asked?" must find a sentence that starts as a
  question and ends with `?`.
- **Three or more options → an `(a)/(b)/(c)` list**, each option a complete alternative in plain
  terms. Two options may stay inline ("replace, or keep both?").
- **Say what the answer decides** when the consequence isn't obvious from the question — one short
  clause is enough ("this sets which limit the wallet enforces at checkout").
- **Self-check before writing the line.** Read it once as the `owner` would, cold. If answering it
  requires opening the UC, knowing what a `BR-###` is, or re-reading the sentence to find the
  actual question, rewrite it. A question the human has to decode is a question that sits
  unanswered.

**Before/after** (the id-reference failure):

> ❌ *Does UC4's Organization Experience narrative-question set *replace* UC-004 S23's single*

> ✅ *In UC-004, the existing Organization Experience question is a single free-text field
> ("Describe your organization's relevant experience"). The new signal proposes a richer
> narrative-question set covering scope, past engagements, and references instead. Should the new
> set **replace** the original field, or should both appear on the form? (owner: client)*

**Before/after** (the readability failure — the ❌ version below satisfies every content rule
above, and was still unreadable to the human who had to answer it):

> ❌ *BR-039's original 20% cap bucket covered supplies, equipment, subscriptions, and
> recreational-activity together. The recent CR (INT-014) gives equipment/supplies their own
> dollar caps (BR-138) and narrows the 20% cap to extracurriculars only (BR-139), but the signal
> never mentions where **subscriptions** now lands — still under the 20% cap (renamed
> "extracurriculars"), moved to a new dollar cap of its own, or dropped as a distinct category
> entirely? (owner: client)*
>
> Four ids in three clauses; "cap bucket", "the CR", "the signal" are vault vocabulary; one
> 60-word sentence with the ask hanging off a *but*; three options run together after a dash.

> ✅ *The program guidelines currently put four kinds of spending under a single ceiling of 20% of
> the award: supplies, equipment, subscriptions, and recreational activities. The recent update
> gave supplies and equipment their own fixed dollar limits, and left the 20% ceiling covering
> recreational activities only — it didn't say what happens to **subscriptions**. Where should
> subscription spending sit now? (a) still inside the 20% ceiling, (b) under its own fixed dollar
> limit — please state the amount, or (c) no longer tracked as its own category. This decides
> which limit the wallet enforces when a student spends on a subscription. (owner: client)
> (ref: BR-039, BR-138, BR-139, INT-014)*

### Answering a question (the human side of the loop)

A question is written to be answered **cold, in the file** — a BA opens the UC, BR, or INT note on
their own time, types on the `A:` lines, and comes back later. Everything downstream reads that line
and nothing else, so:

- **The answer goes on the question's own `A:` line, verbatim.** An answer given in chat, in a comment,
  or in prose above the question is invisible to every skill: the fold-in's three-way read
  (`transform/1-foldin.md`) looks at the `A:` line to tell "unanswered" from "answered, not applied".
  Whoever relays such an answer moves it onto the `A:` line first; that is the one edit allowed.
- **Tick the box only if the answer genuinely settles the question.** "Ask the client", "TBD after the
  demo", a reply restating the disagreement, or one that answers a *different* question, all leave the
  box unchecked — the box is what the status invariant counts (§ Open Questions ↔ status consistency),
  so ticking an unsettled one is what makes a parked artifact read as approvable.
- **An answer still needing a client round-trip stays unchecked but is still worth writing.** A partial
  answer set is normal: the fold-in applies what settled and leaves the rest.
- **Don't hand-edit the numbered sections to match your own answer.** The fold-in applies the answer
  into the content and moves the question into the decision log; editing both is how the same change
  lands twice, or how a staged change silently overwrites the reviewer's wording (`1-foldin.md`
  § The human may have edited the section first).
- **Then say "process UC-###".** That pass reads the answers instead of re-asking them, folds in once,
  and returns either the follow-up questions it produced or the flow and an approval ask
  (`agents/bigin-ba.md` § Answers already written: the process-the-UC pass).
