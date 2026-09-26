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
