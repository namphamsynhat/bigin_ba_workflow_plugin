---
name: hub-bookkeeper
description: RETIRED in v1.9.0 — replaced by the engine command `bin/bigin hub refresh <slug>` (plus `bigin hub flip` / `bigin hub sweep` / `bigin links sync`). Kept one version so an old dispatch finds this note instead of failing. Never dispatch it; run the command.
model: haiku
color: gray
tools: Read
---

This agent is retired. Hub bookkeeping is deterministic and is now done by the engine:

- `bin/bigin hub refresh <slug>|--all` — `uc:` pointers, ## Use Cases, ## Requirement Readiness (one row per
  artifact), the add-only ## Open Questions / Gates mirror, one Changelog line. Signal Log and Coverage Gaps are
  never touched (the write is refused if they change).
- `bin/bigin hub flip <slug> <row>=<status>[:<dest>][@<note>]` and `bin/bigin hub sweep` — Signal Log rows.
- `bin/bigin links sync` — `brs:`/`uc:`/`features:`/`sources:` and the FEATURES.md UC column.

If you were dispatched anyway, do nothing and reply: `RETIRED — run bin/bigin hub refresh <slug>`.
