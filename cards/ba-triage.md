# Card — bigin-ba: answer it yourself before you ask

Every question passes this gate before a human sees it — vault-written, fold-in-raised, or one you spotted.
A question you could have answered is work pushed onto the approver. First bucket that fits:

1. **On record** — another UC's § 2/§ 4, a BR, an EN field table, a Signal Log row, an INT `## Raw`, a
   decision log, any feature. Grep first. Answer, tick, never show it.
2. **A fix, not a question** — a governing BR not cited, a stale mirror: `bigin-transform-signal` (the
   engine's `bin/bigin mirror br` / `links sync`) reconciles it. Fix that ADDS content goes
   `bigin-intake` → `extract-signal` → `bigin-transform-signal`, never your edit.
3. **Research** — statute, deadline, platform behaviour, accessibility/industry norm. `WebSearch`/`WebFetch`,
   write the finding with its source, tick.
4. **Your drafting call** — A# vs E#, which UC an exception belongs in, step order. Decide, label, report.
5. **Client/team decision** — policy, money, meaning, who may see what. The ONLY bucket that reaches the human.

## Rules
- The `A:` line is the one write this gate makes: never § 1–§ 6, never `status`, never a reword of someone
  else's answer ‹questions.md § Answering a question (the human side of the loop)›.
- Provenance leads your answer: `[from <id> §<n>]`, `[researched — <source>]`, `[BA call]` — so it never
  reads as the client's position.
- Buckets 1–4 tick; bucket 5 never does and its `A:` stays blank — the fold-in applies every filled `A:`
  ‹questions.md § Open Questions ↔ status consistency (verification, not just intent)›.
- On a bucket-5 line, rewrite the `Q:` into named options with consequences — "(a) 28 days per statute,
  (b) 14 days your team proposed" — keeping its `owner` and `(ref: …)` ‹questions.md § Open Questions wording (all artifacts)›.
- True-in-general research that may not hold for this client: answer, tick nothing, raise the narrow variant
  as bucket 5.
- Volume is the tell: ten questions after a pass means the gate was skipped. Re-gate what a fold-in just raised.
- A feature-shaped gap ("nothing describes how a donor is retired") is a Coverage Gap, not a UC question:
  `bigin-transform-signal <slug>` owns that register; never hand-write a row ‹feature-hub.md § Feature Hub›.
- The human contradicts your answer → new information → `bigin-intake`; don't defend it or hand-edit back.
