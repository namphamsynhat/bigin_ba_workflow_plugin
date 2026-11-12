"""Quote grounding — does a signal's quote exist in the note's ``## Raw``, and what source text no signal touched.

The extractor copies a short verbatim ``quote`` onto every new row. The engine looks for it in the cited note
(whitespace, case, curly quotes and dashes normalised) so a paraphrase or an invention is caught by code, not by
a second model. Verified quotes also give a measure of RECALL: source runs of at least ``MIN_RUN`` non-empty lines
that sit farther than ``NEAR`` lines from any verified quote were never read into a row.

Verified line spans are kept on the note as ``quoted_lines: 12-14,20-22`` (1-based file lines) so the figures can
be recomputed any time (``bigin coverage --stage extract``) without storing the quotes. Rows from before this
feature carry no quote and are never judged.
"""
import bisect
import re

NEAR = 3          # a source line within this many lines of a verified quote counts as read
MIN_RUN = 5       # an unread run shorter than this is noise (a greeting, a sign-off)
_FOLD = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", "—": "-",
                       " ": " ", "…": "..."})
_SRC_HEAD = re.compile(r"^###\s+SRC-\d+")


def norm(text):
    t = (text or "").translate(_FOLD).lower()
    return re.sub(r"\s+", " ", t).strip()


class RawIndex:
    """The note's Raw text as one normalised string, with the file line each character came from."""

    def __init__(self, doc):
        self.text = ""
        self._starts, self._lines = [], []
        s = doc.section("Raw")
        self.base = s.start if s is not None else 0
        parts = []
        if s is not None:
            for i in range(s.start, s.end):
                line = doc.lines[i]
                if _SRC_HEAD.match(doc.masked[i]):
                    continue
                line = re.sub(r"^\s*>+\s?", "", line)        # blockquote markers are not part of the words
                n = norm(line)
                if not n:
                    continue
                self._starts.append(sum(len(p) + 1 for p in parts))
                self._lines.append(i - self.base)          # relative to ## Raw: front-matter edits never move it
                parts.append(n)
        self.text = " ".join(parts)

    def _line_at(self, off):
        k = bisect.bisect_right(self._starts, off) - 1
        return self._lines[max(k, 0)] if self._lines else 0

    def locate(self, quote):
        """(first_line, last_line) of the quote in the Raw, or None. ``...`` inside a quote joins fragments
        that must each be present."""
        frags = [f for f in (norm(x) for x in re.split(r"\.{3}", norm(quote))) if len(f) >= 6]
        if not frags:
            frags = [norm(quote)] if norm(quote) else []
        if not frags:
            return None
        lo = hi = None
        for f in frags:
            at = self.text.find(f)
            if at < 0:
                return None
            a, b = self._line_at(at), self._line_at(at + len(f) - 1)
            lo = a if lo is None else min(lo, a)
            hi = b if hi is None else max(hi, b)
        return lo, hi


def spans_of(doc):
    """Verified spans, in lines RELATIVE to the ## Raw heading (so adding a front-matter key cannot shift them)."""
    out = []
    for part in str(doc.fm_get("quoted_lines") or "").replace(" ", "").split(","):
        m = re.match(r"^(\d+)-(\d+)$", part)
        if m:
            out.append((int(m.group(1)), int(m.group(2))))
    return out


def merge(spans):
    out = []
    for a, b in sorted(spans):
        if out and a <= out[-1][1] + 1:
            out[-1] = (out[-1][0], max(out[-1][1], b))
        else:
            out.append((a, b))
    return out


def fmt_spans(spans):
    return ",".join(f"{a}-{b}" for a, b in merge(spans))


def uncovered(doc, spans, after_src=0):
    """Runs of unread source: [{src, lines:[first,last]}] over the blocks numbered above ``after_src`` (a living
    note re-judges only its new blocks). A line is read when within NEAR lines of a verified quote."""
    from .worklist import _src_blocks
    spans = merge(spans)

    rs = doc.section("Raw")
    base = rs.start if rs is not None else 0

    def near(ln):
        r = ln - 1 - base
        return any(a - NEAR <= r <= b + NEAR for a, b in spans)

    out, total, in_runs = [], 0, 0
    for b in _src_blocks(doc):
        num = int(b["src"].split("-")[1]) if "-" in b["src"] else 0
        if num <= after_src:
            continue
        first, last = b["lines"]
        run = []

        def close():
            nonlocal in_runs
            if len(run) >= MIN_RUN:
                out.append({"src": b["src"], "lines": [run[0], run[-1]]})
                in_runs += len(run)
            run.clear()

        for ln in range(first + 1, last + 1):                # first is the ### header line
            if not doc.lines[ln - 1].strip():
                continue
            total += 1
            if near(ln):
                close()
            else:
                run.append(ln)
        close()
    return out, (round(100.0 * in_runs / total, 1) if total else 0.0)


def unverified_rows(doc):
    """Row numbers whose Notes carry the ``[unverified]`` flag."""
    from . import model
    return [int(r.num) for r in model.note_rows(doc) if "[unverified]" in (r.get("Notes") or "")]
