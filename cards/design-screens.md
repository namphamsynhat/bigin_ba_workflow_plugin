# Card — design screens worker (model: session default — screen boundaries are judgement)

**In:** the dispatch block from `/bigin-generate-design` Stage 3: feature slug, `UX-###` (new or update),
in-scope UCs, platform, nav map version, an optional Design Brief from `ux-brief-assembler`. Read the hub's
`## Design Directives` / `## Pain Points`, each UC's § 1–§ 5, cited BR/EN, sibling UX specs for patterns.
**Out:** ONE file — `04-UIUX/UX-<NNN> <Feature>.md` — plus the fixed report block (nav candidates,
cross-feature screens, unresolved pain points). This card is the short form; the stage guide
`_bigin/stages/design/3-screens.md` stays the full procedure when a case is not covered here.

## Rules
1. Flows become screens: a run of steps by the same actor in the same place is one screen; a system-only
   step is not a screen; a validation is a state; an E-flow is a named error state ‹stages/design/3-screens.md § Part 2 — Flows become screens›.
2. Merge two UCs onto one screen only when their actors' data scope agrees ‹stages/design/3-screens.md § Part 2a — Actor scope: whose data, how much, and when one place is two screens›.
3. Volume licenses finding machinery, never a capability; acting on many records is a requirement gap
   ‹design-actor-scope.md § D8 — the line volume may not cross›.
4. A screen spec names semantic roles only — no hex, px, font or token id ‹design-core.md § The eight design hard rules›.
5. Every screen, element, state and flow is grounded in a requirement, an existing pattern or a stated
   preference; ungrounded → a `## 6` question ‹design-grounding.md § Grounding — the test that keeps design out of the requirements›.
6. Every state traces to a source (empty, loading, validation-error from a BR, failure per E#, success from
   § 1); a `many` screen shows the real number ‹stages/design/3-screens.md § Part 4 — States, and where each one comes from›.
7. A flow resolves a UC goal or names the `PP-###` it fixes; every open pain point gets an answer, even "no"
   ‹stages/design/3-screens.md § D6 — a flow resolves something stated›.
8. Requirement content is read-only: a gap in what the system DOES is a question marked requirement gap,
   never an edit to a UC/BR/EN ‹stages/design/3-screens.md § Part 5 — When you do not know›.
9. Write nothing else: not the nav map, another feature's spec or hub, DESIGN-PRINCIPLES, PAIN-POINTS,
   FEATURES.md — report them ‹stages/design/3-screens.md § Part 7 — Report, do not write›. Never `status: accepted`.

## Example (one mapping decision)
UC-003 S1 "Finance officer opens approved grants awaiting payment" + S2 "releases the payment" — same
actor, same place → ONE screen `Payments queue` (Primary, view_id `payments-queue`), serves UC-003 S1, S2;
states: empty (no approved grants), loading, validation-error (BR-005 sign-off over $10,000), success
(§ 1 post-condition); volume `many` only if an entity cardinality or BR says so — else the narrowest reading
plus a `## 6` question.
