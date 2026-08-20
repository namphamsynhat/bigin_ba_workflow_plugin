---
type: entity
id: EN-
name:            # the real-world BUSINESS OBJECT — "Application", "Vendor", "Wallet". Never an
                 # attribute: "Application.Certification Status" is a FIELD of Application, and a
                 # doc named that way is the fragmentation this artifact exists to prevent
                 # (conventions.md § Entity Data Model, The doc is a data dictionary).
kind:            # actor | data | system
status: proposed # proposed (row exists in ENTITIES.md, no doc yet) -> draft (this doc exists,
                 # fields still settling) -> approved (human confirmed at a UC/BR review gate).
                 # Plus one side-state: merged — an attribute-shaped doc whose fields have been
                 # folded into their owning object. Never deletion; the id stays resolvable.
merged_into:     # EN-### this doc's fields were folded into, on `status: merged` only. Blank
                 # otherwise. Set by /sync-entities, which also repoints every citation.
features: []     # every feature slug whose UC(s)/BR(s) reference this entity
updated:
---

# `EN-<NNN> <Entity Name>`

`<one-line description — what this entity represents, in plain language.>`

## Fields
<!-- THE DATA DICTIONARY for this business object — every field it is known to carry, not only the
ones the use case being synced happened to touch. /sync-entities rebuilds this from the union of
every source that has stated a field for this object: the ENTITIES.md row's `Fields (so far)`, the
rows already here, and every UC/BR in `features:` that references it (conventions.md § Entity Data
Model, The doc is a data dictionary).

Type spells out the values. A bare `enum`, `status`, or `code` documents nothing — enumerate the
states inline, separated by ` / ` (a `|` would break the table): `enum: Pending School Review /
Certified / Rejected`. Give the format where one was stated: `date: YYYY-MM-DD`, `money: USD`.
Values never stated → `enum: values not stated`, plus a `- [ ] Q:` on a UC that references the
field — never a plausible list invented here.

Never invent a field, type, value, or required-ness no source stated (hard rule 1). Complete means
complete over what the vault knows, with the gaps left visible as gaps.

Source cites the Signal Log row (or UC-### S<n> / BR-###) that introduced or last changed the field. A
field-level business rule is not a subsection here — it's its own BR-### file under
01-Requirements/_brs/ (conventions.md § Entity Data Model), citing this entity's fields it
governs in its own body. -->

| Field | Type | Required? | Source | Notes |
|-------|------|------------|--------|-------|

## Relationships
<!-- e.g. "- belongs to EN-002 Customer (many-to-one), drawn from UC-004 S3" -->

## Changelog
- (YYYY-MM-DD) — promoted from ENTITIES.md proposed row, via `<INT-###>`
