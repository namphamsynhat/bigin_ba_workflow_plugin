---
type: entities-register
updated:
---

# Entity Register

One row per entity this project's features reference. `extract-signal` only ever adds a `proposed` row when a signal reveals a new data field or entity attribute — it never creates the full `EN-###` document that documents an entity in depth; that's a later step, run by `/sync-entities`, once an approved UC or BR actually references the entity.

**One row per real-world business object — never per field.** `Application`, `Vendor`, `Wallet`. A signal about a new field on a tracked object adds that field to the object's `Fields (so far)` cell, values spelled out where the source gave them (`Certification Status: Pending School Review / Certified / Rejected`); it never earns a row of its own. A row named `<Entity>.<Field>` is always the bug — it becomes a one-field `EN-###` fragment the moment `/sync-entities` promotes it, splitting the object's definition across files nobody knows to open together (`registers.md` § Entity Data Model).

`Status`: `proposed` → `draft` → `approved`, plus `merged` for a row whose fields were folded into the object that owns them — `Notes` names the `EN-###` they went to. A merged row is never deleted; the id stays resolvable.

| EN-### | Entity | Status | Fields (so far) | Features | Notes |
|--------|--------|--------|------------------|----------|-------|

## Changelog
- (YYYY-MM-DD) — register created
