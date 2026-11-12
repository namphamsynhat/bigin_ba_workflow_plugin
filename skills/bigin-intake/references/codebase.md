# Codebase mode — provider detail for `/bigin-intake` Stage 2C

```text
input: a rule-card file — the modernize-extract-rules store (analysis/_rules-store.json), a JSON list of
       generic cards, or a CSV (docs/CODEBASE-INTAKE.md) — plus, optionally, a card → feature assignment map

bigin intake codebase --cards <path> [--assignment <map.json>] [--group-by capability|feature|group|none]
                    [--unmapped-out _runs/<run>/tasks/codebase.file.in.json]
```

What the engine does, with no LLM call: one INT note per group (`source: codebase`, `grounding: codebase`,
the provenance header and the asymmetry warning, the rule pack saved as its attachment) · one `decision` row per
card with its id verbatim and its citation as Source, plus a separate `problem` row per suspected defect and a
`question` row per SME question · filing by (feature, card theme) straight onto the hubs · the note's status.
Re-running skips cards already imported (idempotent).

Features come from `--assignment` first, then the card's own feature/capability, then path heuristics. Only
rows it cannot map (or maps ambiguously) are left `unresolved — …` with a question, and written to
`--unmapped-out` as ONE `signal-filer` classification task: dispatch the filer with that input
(`cards/filer.md`), `bigin ingest <out> --kind filing`, `bigin file apply <out>`. Finish with `bigin lint --full` and
`bigin coverage --stage file --id-pattern '<card id regex>' --universe <cards>` — every card id must be filed.

Codebase mode never edits `repos/` and never reproduces secrets, credentials, e-mail addresses or internal
hostnames a card quotes — the engine copies card text as given, so check the report and raise any such text with
the human instead of filing it on.

