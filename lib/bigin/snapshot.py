"""Before / After per intake note: what ONE ticket (or email, or meeting) changed in each UC / BR.

A UC is shaped by many tickets, so its own file can only show where it ended up. ``bigin apply`` records,
for every change set it lands, the intake note(s) in the set's trace; this module keeps, per note:

    00-Inbox/_snapshots/INT-###/UC-###.before.md   the UC as it was before this note first changed it
                                                    (written once; absent for a UC this note created)
    00-Inbox/_snapshots/INT-###/UC-###.after.md    the UC after this note's latest change (rewritten)
    00-Inbox/_snapshots/INT-###/changes.json       every change this note made, one entry per change set:
                                                    the lines it removed and the lines it added

and regenerates the note's engine-owned ``## Before / After`` section from changes.json: per UC / BR the
versions, links to both snapshots, and a Before | After table of this note's own changes only. The
"after" snapshot is the whole UC at that moment, so it can carry another note's later edits; the table
never does.
"""
import difflib
import json
import os
import re

from .util import today

SECTION = "Before / After"


def body(doc):
    """The doc's content lines a change set can touch: no frontmatter, no Changelog, no blanks."""
    lines = doc.lines[doc.body_start:]
    out, skip = [], False
    for x in lines:
        if x.startswith("## "):
            skip = x[3:].strip().lower().startswith("changelog")
        if not skip and x.strip():
            out.append(x.rstrip())
    return out


def delta(before, after):
    """(removed, added) lines between two body() snapshots."""
    rem, add = [], []
    for op, a1, a2, b1, b2 in difflib.SequenceMatcher(a=before, b=after, autojunk=False).get_opcodes():
        if op in ("replace", "delete"):
            rem += before[a1:a2]
        if op in ("replace", "insert"):
            add += after[b1:b2]
    return rem, add


def ints_of(trace):
    tr = trace or {}
    return sorted({x for x in ([tr.get("int")] if tr.get("int") else []) + list(tr.get("ints") or []) if x})


class Recorder:
    """Collects one apply batch: Recorder.change() per landed change set, .done() per written doc."""

    def __init__(self):
        self.items = {}  # (int, tid) -> {"before", "before_ver", "after", "after_ver", "title", "created", "changes"}

    def _slot(self, nid, tid):
        return self.items.setdefault((nid, tid), {"before": None, "before_ver": None, "after": None,
                                                  "after_ver": None, "title": "", "created": False, "changes": []})

    def change(self, trace, tid, cs, pre, post, before_text, before_ver):
        rem, add = delta(pre, post)
        if not rem and not add:
            return
        for nid in ints_of(trace):
            s = self._slot(nid, tid)
            if s["before"] is None and not s["created"]:
                s["before"], s["before_ver"] = before_text, before_ver
            s["changes"].append({"cs": cs["id"], "op": cs["op"],
                                 "ref": str((cs.get("anchor") or {}).get("ref") or cs["target"].get("section") or ""),
                                 "removed": rem, "added": add, "date": today()})

    def created(self, trace, tid, cs):
        for nid in ints_of(trace):
            s = self._slot(nid, tid)
            s["created"] = True
            s["changes"].append({"cs": cs["id"], "op": cs["op"], "ref": "", "removed": [],
                                 "added": [f"(new {tid.split('-')[0]} created by this note)"], "date": today()})

    def done(self, tid, doc):
        for (nid, t), s in self.items.items():
            if t == tid:
                s["after"], s["after_ver"] = doc.text, str(doc.fm_get("version") or "")
                s["title"] = doc.fm_get("title") or ""

    def write(self, vault):
        """Persist every touched note's snapshots + changes.json and regenerate its section. Returns notes."""
        by_note = {}
        for (nid, tid), s in self.items.items():
            by_note.setdefault(nid, {})[tid] = s
        written = []
        for nid, targets in sorted(by_note.items()):
            p = vault.find(nid)
            if not p:
                continue
            d = os.path.join(vault.inbox, "_snapshots", nid)
            os.makedirs(d, exist_ok=True)
            log_p = os.path.join(d, "changes.json")
            log = json.load(open(log_p, encoding="utf-8")) if os.path.exists(log_p) else {}
            for tid, s in targets.items():
                e = log.setdefault(tid, {"title": "", "before_ver": None, "after_ver": None, "created": False,
                                         "changes": []})
                bp = os.path.join(d, f"{tid}.before.md")
                if s["before"] is not None and not os.path.exists(bp) and not e["created"]:
                    with open(bp, "w", encoding="utf-8") as f:
                        f.write(s["before"])
                    e["before_ver"] = s["before_ver"]
                e["created"] = e["created"] or s["created"]
                if s["after"] is not None:
                    with open(os.path.join(d, f"{tid}.after.md"), "w", encoding="utf-8") as f:
                        f.write(s["after"])
                    e["after_ver"], e["title"] = s["after_ver"], s["title"] or e["title"]
                seen = {c["cs"] for c in e["changes"]}
                e["changes"] += [c for c in s["changes"] if c["cs"] not in seen]
            with open(log_p, "w", encoding="utf-8") as f:
                json.dump(log, f, indent=2, ensure_ascii=False)
                f.write("\n")
            note = vault.load(p)
            lines = section_lines(nid, log)
            if note.section(SECTION) is not None:
                note.replace_body(SECTION, [""] + lines + [""])
            else:
                note.insert_section(SECTION, lines + [""], after="Open Questions")
            vault.write(note)
            written.append(nid)
        return written


def _cell(lines):
    out = []
    for x in lines:
        x = x.strip()
        if x.startswith("|"):
            x = " · ".join(c.strip() for c in x.strip("|").split("|") if c.strip())
        out.append(x.replace("|", "\\|"))
    t = "<br>".join(out) or "—"
    return t if len(t) <= 400 else t[:397] + "…"


def section_lines(nid, log):
    out = [f"<!-- engine-owned (bigin apply): what {nid} changed in each use case / rule — this note's changes "
           f"only. Full text before and after: 00-Inbox/_snapshots/{nid}/. Never edit by hand. -->"]
    for tid in sorted(log):
        e = log[tid]
        was = "new" if e["created"] else f"v{e['before_ver'] or '?'}"
        out += ["", f"### {tid} {e['title']} · {was} → v{e['after_ver'] or '?'}".rstrip(), ""]
        links = []
        if not e["created"]:
            links.append(f"Before: [[_snapshots/{nid}/{tid}.before.md|{tid} before]]")
        links.append(f"After: [[_snapshots/{nid}/{tid}.after.md|{tid} after]]")
        out += [" · ".join(links), "", "| Change | Before | After |", "|---|---|---|"]
        for c in e["changes"]:
            label = f"{c['op']} {c['ref']}".strip() + f" ({c['cs']})"
            out.append(f"| {label} | {_cell(c['removed'])} | {_cell(c['added'])} |")
    return out
