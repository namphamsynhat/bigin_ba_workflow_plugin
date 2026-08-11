---
type: entity
id: EN-
name:
kind:            # actor | data | system
status: proposed # proposed (row exists in ENTITIES.md, no doc yet) -> draft (this doc exists,
                 # fields still settling) -> approved (human confirmed at an FR/BR review gate)
features: []     # every feature slug whose FR(s)/BR(s) reference this entity
updated:
---

# EN-<NNN> <Entity Name>

<one-line description — what this entity represents, in plain language.>

## Fields
<!-- Source cites the Signal Log row (or FR/BR) that introduced or last changed the field. A
field-level business rule is not a subsection here — it's its own BR-### file under
01-Requirements/_brs/ (conventions.md § Entity Data Model), citing this entity's fields it
governs in its own body. -->

| Field | Type | Required? | Source | Notes |
|-------|------|------------|--------|-------|

## Relationships
<!-- e.g. "- belongs to EN-002 Customer (many-to-one), drawn from FR-004" -->

## Changelog
- (YYYY-MM-DD) — promoted from ENTITIES.md proposed row, via <INT-###>
