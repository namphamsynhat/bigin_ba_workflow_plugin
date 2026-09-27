# Codebase intake — rule cards in, notes and hub rows out, no LLM call

For a code-grounded project (`grounding: codebase | both` in `_bigin/system/project.md`), requirements are
read out of existing code as **rule cards** — for example by `code-modernization:modernize-extract-rules`.
Cards are already signals: an agent re-extracting them from prose would only lose recall. So they are imported
by the engine, deterministically.

```bash
"$CLAUDE_PLUGIN_ROOT/bin/bigin" intake codebase --cards analysis/_rules-store.json \
    [--assignment analysis/ba/rule-assignment.json] [--group-by capability|feature|group|none] \
    [--title "…"] [--unmapped-out _runs/<id>/tasks/unmapped.file.in.json] [--dry]
```

## Card formats

1. **Rules store** (`modernize-extract-rules` output, `analysis/_rules-store.json`):
   `{"rules": {"<key>": {name, category, priority, source, plainEnglish, given, when, then, confidence,
   suspectedDefect?, smeQuestion?, _xr?}}}`. The card id is `_xr` when present, else `id`, else the key.
2. **JSON list** of generic cards, each validated against `lib/bigin/schema/rule-card.json`:

   | Field | Required | Meaning |
   |---|---|---|
   | `id` | yes | permanent card id, carried verbatim into every row (e.g. `XR-CALC-058`) |
   | `plainEnglish` | yes | the rule, as-built, in business language |
   | `name`, `category`, `priority`, `confidence` | | shown in the rule pack; `category` drives filing themes |
   | `source` | | `repo/path:lines` — becomes the row's Source cite |
   | `given`, `when`, `then` | | example, kept in the rule pack |
   | `suspectedDefect` | | becomes its own `problem` row |
   | `smeQuestion` | | becomes its own `question` row and a hub question (owner: team) |
   | `feature`, `capability`, `surface` | | mapping hints |
   | `verified` | | `true` when an independent referee confirmed the citation |
3. **CSV** with a header row using the same field names.

## Feature mapping

In order, per card: `--assignment` map (`{"<card id>": {"slug", "cap", "group", "alt"?}}` or `{"<id>": "<slug>"}`;
an entry with `alt` is treated as ambiguous) → the card's own `feature` → its `capability` matched against the
capability codes in FEATURES.md rows (`C4.2`) → the card's `source` path matched against slugs. A slug must exist in
FEATURES.md; the engine never invents one.

## What gets written

Per group (`--group-by capability` default; `feature`; `group` from the assignment; `none` = one note):

- one INT note (minted under the id lock): `source: codebase`, `grounding: codebase`, `status` set by filing,
  `declared_features` = the group's slugs, a provenance header and the **asymmetry warning** in `## Raw`;
- the rule pack as its attachment: `00-Inbox/_attachments/<INT>/rule-pack.md`;
- `## Extracted signals` written directly: one `decision` row per card (`` `<id>` — <plainEnglish> ``, Source
  `SRC-1 · rule pack · <source>`), plus a separate `problem` row per suspected defect and `question` row per SME question;
- filing through the same engine path as a signal-filer's `filing.json` (`bigin file apply`): rows grouped by
  (feature, capability · category, type) into one themed hub Signal Log row each; question rows file alone with a
  hub question; hubs created from the template when missing (split companion files when the vault is split).

## The unmapped remainder

Cards with no feature, or an ambiguous one, are filed on the note as `question` with
`unresolved — none found` / `unresolved — candidates: a / b`, and — with `--unmapped-out` — written as ONE
`signal-filer` task input (schema output `filing`). That is the only LLM work codebase intake can leave.

## Idempotence

A card whose id already appears in any note's signal table is skipped, so re-running an import (or importing a
later, larger rules store) adds only new cards. `--dry` reports the plan without writing.

## After import

- `bigin coverage --stage file --id-pattern '<pattern>' --universe <cards>` (or set `coverage_id_pattern` in
  project.md) proves every card id reached a hub row.
- Transform is identical to communication mode, plus adjudication: a `conflict`/`held` row is refereed against the
  code by `code-adjudicator` (`workflows/adjudicate.js`). `conflict_policy: code-first` lets the code settle a
  factual disagreement; `ask` settles the facts and gates the decision on a human question. Intent is never
  settled by code. `repos/` is read-only throughout.

---

## Worked Example — Agoyu Multi-Surface Marketplace

Agoyu is an in-production moving marketplace spanning five surfaces:
- `backend-api`: Laravel 5.6 modular monolith (`repos/backend/Packages`)
- `console-vue`: Mover/admin Vue SPA embedded in Blade (`repos/backend/frontend`)
- `blade`: Server-rendered admin and public views (`repos/backend/Themes/KOSMO`, `resources/views`)
- `fe-web`: Nuxt consumer portal (`repos/fe-web`)
- `fe-mobile`: React Native mobile application (`repos/fe-mobile`)

The Agoyu BA vault reverse-engineers requirements directly from the source repositories without correspondence intake.
Here is how the complete 5-step codebase intake flow was executed.

### 1. Rule extraction & rule store

The `code-modernization:modernize-extract-rules` skill inspected ASTs and business logic across `repos/`, emitting
1,114 rules into `analysis/_rules-store.json`:

```json
{
  "rules": {
    "XR-CALC-001": {
      "name": "Mover minimum tariff calculation",
      "category": "pricing",
      "priority": "high",
      "source": "repos/backend/Packages/Tariff/Services/TariffCalculator.php:142",
      "plainEnglish": "If distance is under 15 miles, apply the flat minimum tariff rate.",
      "given": "Move distance is 12 miles",
      "when": "Quote is calculated",
      "then": "Base price equals $150 minimum",
      "confidence": 0.95
    }
  }
}
```

### 2. Rule assignment & surface tagging

Because Agoyu has diverged components (e.g. `MoverOffers.vue` exists in both `repos/fe-web` and `repos/backend/frontend`
with different lineages), rules are tagged with their owning surface and mapped to one of 50 capabilities:

```json
{
  "XR-CALC-001": {
    "slug": "address-distance",
    "cap": "C1.3",
    "group": "G1",
    "lane": "BR",
    "surface": "backend-api",
    "conf": "high",
    "basis": "TariffCalculator.php"
  }
}
```

Stored in `analysis/ba/rule-assignment.json`. Any rule with conflicting candidate slugs records an `alt` field to avoid
guessing.

### 3. Deterministic intake run

Run `bigin intake codebase` to import all cards into the vault without calling an LLM:

```bash
bigin intake codebase \
    --cards analysis/_rules-store.json \
    --assignment analysis/ba/rule-assignment.json \
    --group-by capability \
    --title "Agoyu Codebase Rule Intake" \
    --unmapped-out _runs/intake-001/tasks/unmapped.file.in.json
```

**Results:**
- Generated `INT-001` through `INT-010` in `00-Inbox/`, each anchored to a capability group.
- Attached rule packs in `00-Inbox/_attachments/INT-###/rule-pack.md`.
- Populated `## Extracted signals` tables with exact citations (`SRC-1 · rule pack · repos/backend/...`).
- Filed 1,114 signals into 50 feature hubs under `01-Requirements/_features/<slug>.md`.
- Unmapped cards routed to `unmapped.file.in.json` for explicit human triage or targeted routing.

### 4. Verification & coverage audit

Before transforming any signals into use cases, run the audit suite to verify zero rule loss:

```bash
# Verify all 1,114 rule cards reached feature hubs
bigin coverage --stage file --universe analysis/_rules-store.json

# Run the veracity audit against the baseline snapshot
bigin audit --baseline analysis/ba/snapshots/vault-baseline.tgz
```

The audit checks:
1. `check_xr_coverage`: 1,114 rules in store == 1,114 rules on hubs (100% recall).
2. `check_orphaned_rules`: No hub rows cite unassigned rule cards.
3. `check_asymmetry_warnings`: Multi-surface warnings preserved on INT notes.
4. `check_no_lost_questions`: No existing questions or gates were dropped.

### 5. Transform & code adjudication

With all rules filed, run `workflows/transform.js` to draft and apply change sets:

1. **Route (uc-router Phase A):** Inspects each qualified row on the hub and routes it to an existing UC, a new UC,
   or a BR. Proposes new UCs with clean keys (e.g. `new:calculate-tariff`).
2. **Mint:** Engine locks the vault and mints real UC IDs (`UC-001`..`UC-101`).
3. **Draft (uc-router Phase B):** Emits final-text change sets referencing exact anchor SHAs:
   ```json
   {
     "id": "cs-calc-01",
     "target": {"kind": "UC", "id": "UC-012", "section": "2"},
     "op": "new_step_after",
     "anchor": {"ref": "S2", "sha": "e2a1b94c"},
     "cells": {
       "actor": "System validates distance under 15 miles",
       "system": "System applies flat minimum tariff rate per BR-004."
     }
   }
   ```
4. **Apply:** `bigin apply` atomically updates `UC-012.md` and `BR-004.md` in place, updating `## Changelog`.
5. **Adjudicate (`workflows/adjudicate.js`):** When code conflicts with an existing requirement, `code-adjudicator`
   reads `repos/` (read-only), verifies the live implementation, and either:
   - Sets factual text if `conflict_policy: code-first`.
   - Stages an open question in `## Open Questions / Gates` if business intent is ambiguous.

