"""UC/BR status from a LIVE re-count, never from what a run intended (ported from ``set_status.py``).

A UC counts only its § 5 **Still open** list (a decision-log row is answered history); a BR counts
its ## Open Questions. Any unchecked ``- [ ] Q:`` → needs-clarification; none → draft. Only ever
moves between draft and needs-clarification — approved / removed / enriched / consolidated are
human-gated (core.md § Status vocabularies) and never touched.
"""
from . import model

MOVABLE = ("draft", "needs-clarification")


def recount(vault, ids=None, dry=False):
    changes = []
    for p in vault.uc_paths() + vault.br_paths():
        d = vault.load(p)
        if not d.fm or not d.id:
            continue
        if ids and d.id not in ids:
            continue
        cur = d.fm_get("status")
        if cur not in MOVABLE:
            continue
        want = "needs-clarification" if model.open_questions(d) else "draft"
        if want != cur:
            changes.append((d.id, cur, want))
            d.fm_set("status", want)
            if dry:
                d.verify()
                vault.forget(p)
            else:
                vault.write(d)
    return changes
