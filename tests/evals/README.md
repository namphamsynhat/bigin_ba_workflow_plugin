# Golden set

One folder per case: `note.md` (the source note, `## Raw` filled, no extracted rows), `extract.in.json` (the
extractor's task input for it), `signals.expected.json` (the BA-corrected rows: `type`, `signal`, `quote`,
optional `polarity`), and optionally `route.in.json` + `routing.expected.json` (`[{row, lane, target}]`).

`appeals-email` is a **synthetic seed** to prove the harness. The plan calls for ~20 cases taken from real,
BA-corrected, anonymised notes: add each as a new folder (copy the note, run `bigin worklist extract` for
`extract.in.json`, paste the corrected rows). Cases are graded by code only (`lib/bigin/evalgrade.py`).

Run before releasing any card, schema or model change: `workflows/eval.js` (args `{run, plugin_root, vault}`),
then `bigin eval grade <run>`; record the scores in the release note.
