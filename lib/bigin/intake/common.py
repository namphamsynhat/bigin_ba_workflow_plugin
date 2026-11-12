"""Helpers shared by the living-note intakes (Jira tickets, Confluence pages): append source blocks to a note's
``## Raw`` and keep its ``## Capture history``. Neither ever touches an existing block."""
import re

from ..util import EngineError, today


def append_blocks(doc, blocks):
    """Append ``### SRC-n`` blocks to ## Raw (after the last existing block) and to ``raw_sources``.
    Never touches an existing block."""
    if not blocks:
        return []
    s = doc.section("Raw")
    if s is None:
        raise EngineError(f"{doc.name}: no ## Raw section")
    nums = [int(m.group(1)) for m in (re.match(r"^### SRC-(\d+)\b", x) for x in doc.lines[s.start:s.end]) if m]
    n = max(nums or [0])
    lines, manifest = [], doc.fm_list("raw_sources")
    for b in blocks:
        n += 1
        lines += [f"### SRC-{n} · {b['kind']} · {b['ref']}", "", b["text"].rstrip(), ""]
        manifest.append(f"SRC-{n} · {b['kind']} · {b['ref']}")
    pos = s.end
    while pos > s.start and not doc.lines[pos - 1].strip():
        pos -= 1
    doc.splice(pos, pos, [""] + lines[:-1])
    doc.fm_set("raw_sources", manifest)
    return list(range(n - len(blocks) + 1, n + 1))


def _history(doc, line):
    s = doc.section("Capture history")
    entry = f"- {today()} — {line}"
    if s is None:
        doc.insert_section("Capture history", [entry], after="Raw")
        return
    pos = s.end
    while pos > s.start and not doc.lines[pos - 1].strip():
        pos -= 1
    doc.splice(pos, pos, [entry])
