# Card — PRD writer (model: session default — translating flows for a sponsor is judgement, not haiku work)

**In:** the dispatch block from `/bigin-generate-prd`: feature slug, `PRD-###` (new or update in place), UCs
TO FOLD (approved, with versions), UCs PENDING, CHAIN, DESIGN (`UX-###@version` or none), PRD engine.
Read each folded UC in full, every BR in their `brs:`, every EN in `entities:`, the feature's PAIN-POINTS
rows, the UX spec if one exists, and `_bigin/templates/prd.md` (the schema — instantiate it).
**Out:** ONE file — `02-PRD/PRD-<NNN> <Feature>.md`, §§ 1–12 + Traceability + Changelog — and the report block.
The stage guides `_bigin/stages/prd/2-business.md`, `3-flows.md`, `4-design.md` stay the full procedure.

## Rules
1. Every line traces to something written; nothing to trace → "not stated" ‹stages/prd/2-business.md § The one rule that governs every line in this stage›.
2. Business language only — a sentence naming an endpoint, table, payload, status code or field type is a
   System Response leaking through untranslated ‹stages/prd/3-flows.md § The translation rule›.
3. Translation keeps every validation, record and notification the step carried; dropping one loses scope
   ‹stages/prd/3-flows.md § § 6 Business Flows›.
4. Approved UCs only in §§ 5–9; pending UCs go to § 10 and nowhere else ‹stages/prd/4-design.md § § 10 Scope & Release Framing›.
5. § 7 rules come from the BR file; the UC's § 4 only says where it bites. A blank Enforced-at or two
   contradicting rules are reported, never reconciled ‹stages/prd/3-flows.md § § 7 Business Rules & Policies›.
6. § 9 quotes the design; no UX spec → one line saying so, never screens described from flows
   ‹stages/prd/4-design.md § § 9 Experience & Design — report the design, never decide it›.
7. § 11 pools every open UC question, UX requirement gap and open/answered Coverage Gap
   ‹stages/prd/4-design.md § § 11 Open Business Decisions›.
8. Read-only on every UC, BR, entity, UX spec and hub; `status: draft` always; the orchestrator stamps
   `absorbed:` and refreshes hubs ‹stages/prd/5-close.md § Part 4 — Refresh every participating hub, one at a time›.

## Example (one § 6 line)
UC-003 S2 | Finance officer releases the payment | System sends a bank transfer and records it →
PRD § 6: "The finance officer releases the payment; the grant is paid by bank transfer and the payment is
recorded. (S2)" — and BR-005 in § 7: "Applies at: when the payment is released (S2). Consequence if
broken: not stated."
