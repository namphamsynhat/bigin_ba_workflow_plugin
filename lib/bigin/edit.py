"""Write-side helpers shared by every engine command. All operate on a Doc in memory; the caller
writes once through ``Vault.write``."""
import re

from .util import norm_ws, today
from .vault import Q_RE


def append_changelog(doc, line):
    """Append ``line`` as the last bullet of ``## Changelog`` (oldest-first, core.md § Changelog)."""
    s = doc.section("Changelog")
    if s is None:
        doc.insert_section("Changelog", [line], before=None)
        return True
    end = s.end
    while end > s.start and not doc.lines[end - 1].strip():
        end -= 1
    return doc.splice(end, end, [line])


def changelog_has(doc, token):
    s = doc.section("Changelog")
    return bool(s) and any(token in x for x in doc.lines[s.start:s.end])


def bump_version(doc):
    v = str(doc.fm_get("version") or "1.0")
    m = re.match(r"^(\d+)\.(\d+)$", v)
    new = f"{m.group(1)}.{int(m.group(2)) + 1}" if m else "1.1"
    doc.fm_set("version", new)
    return new


def touch_updated(doc):
    if doc.fm and "updated" in doc.fm:
        doc.fm_set("updated", today())


def question_block(text, owner=None, ref=None, answer="", indent="", checked=False):
    q = text.strip()
    if owner and "(owner:" not in q:
        q += f" (owner: {owner})"
    if ref and "(ref:" not in q:
        q += f" (ref: {ref})"
    box = "x" if checked else " "
    return [f"{indent}- [{box}] Q: {q}", f"{indent}  A: {answer}".rstrip()]


def q_core(text):
    """Question text without its trailing (owner:…)(ref:…) tags, whitespace-normalised, lowercased."""
    t = re.sub(r"\((owner|ref):[^)]*\)", "", text or "")
    t = re.sub(r"↦\s*\S+", "", t)
    return norm_ws(t).lower()


def shingles(s):
    w = re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).split()
    return set(zip(*[w[i:] for i in range(6)]))


def same_question(a, b):
    """Ported from mirror_br_questions: same first 60 chars, or >50% shared 6-word shingles."""
    ca, cb = q_core(a), q_core(b)
    if not ca or not cb:
        return False
    if ca[:60] == cb[:60]:
        return True
    sa, sb = shingles(ca), shingles(cb)
    if sa and sb:
        ua, ub = set(re.findall(r"UC-\d+", a)), set(re.findall(r"UC-\d+", b))
        if ua and ub and ua != ub:
            return False
        return len(sa & sb) / min(len(sa), len(sb)) > 0.5
    return False


def insert_lines_at_end_of(doc, start, end, lines):
    """Insert ``lines`` after the last non-blank, non-comment-only line in [start, end)."""
    pos = end
    while pos > start and not doc.masked[pos - 1].strip():
        pos -= 1
    # never inside a trailing comment block
    block = list(lines)
    if pos > start and doc.lines[pos - 1].strip():
        pass
    return doc.splice(pos, pos, block)


def is_question_line(line):
    return bool(Q_RE.match(line))
