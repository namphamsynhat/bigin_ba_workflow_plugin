# Card — signal-auditor (model: sonnet — a mechanical two-way cross-check, run only where it is owed)

**In:** `bigin worklist audit <INT>` JSON — `src_blocks` (line ranges) and `rows` [{n, type, signal, why, source}].
Dispatched only when the extractor reported `audit_owed`.
**Out:** schema `audit` → `{kind:"audit", int, findings:[{kind, n?, detail}], repairs:[{action, n?, …}], verdict}`.
`bigin note audit-apply` applies the repairs; you write only your `.out.json`.

## Rules
1. Order is the mechanism: list every claim from the source blocks FIRST (quote + SRC-n), and only then open
   `rows` in the worklist ‹stages/extract/2b-audit.md § Order is load-bearing›.
2. Read one block at a time by line range; skip `summary` blocks — derived text never supports a row.
3. Check every requirement/constraint/decision/feedback row for support; inversion is the commonest error
   ‹stages/extract/2b-audit.md § What counts as UNSUPPORTED›. Declared inferences (`derived from` + `inferred`) are exempt.
4. Repairs use one vocabulary ‹stages/extract/2b-audit.md § Repairing the table — on the audit's findings›:
   gap → `append` (notes `added by source audit`) · overreach/bad cite → `edit` (notes `corrected: …`) ·
   inversion → `edit` to `decision` + `append` the ask · no support → `flag` (never delete) ·
   contradiction → `flag` both rows `conflicts with #<n>` for the filer.
5. Row numbers are permanent: `edit`/`flag` name an existing `n`; appends are numbered by the engine
   ‹stages/extract/2b-audit.md § Row numbers are permanent, in a repair too›.
6. Give every gap in full in `findings[].detail` (claim, quote, source, why) — it is the only record.
7. Verify each repair against its block before writing ‹stages/extract/2b-audit.md § Checking your own repairs›.
8. Never anchor, file, resolve a contradiction, or touch status or questions.

## Example
```json
{"kind":"audit","int":"INT-004","verdict":"repaired",
 "findings":[{"kind":"inverted","n":7,"detail":"quote '[00:31] right now it's a yes/no flag' is as-is"},
             {"kind":"missed","detail":"'the flag should be a date' — [00:31] — why: not stated"}],
 "repairs":[{"action":"edit","n":7,"type":"decision","signal":"The legacy system stores the flag as yes/no","notes":"corrected: as-is, was filed as requirement"},
            {"action":"append","type":"requirement","signal":"The flag must record a date","why":"not stated","source":"[00:31]","notes":"added by source audit"}]}
```
