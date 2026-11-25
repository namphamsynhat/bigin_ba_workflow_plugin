"""The glossary — one hand-edited table of business terms (`01-Requirements/GLOSSARY.md`).

    | Term | Meaning | Also called | Source |

``Term`` is the one name the vault writes; ``Also called`` holds every other name for the same thing
(client wording, a Vietnamese term, a code or Jira name), separated by ``;``. A human owns the file and
may add or edit any row at any time; the engine only ever appends a row, adds a name to ``Also called``,
or fills a blank ``Meaning`` — it never renames a term and never rewrites a meaning somebody wrote.

Pure standard library and no engine imports, so `lint.py` can use it from the hook.
"""
import os
import re

FILE = "GLOSSARY.md"
HEADER = ["Term", "Meaning", "Also called", "Source"]

USE = ("write `term` exactly as given wherever that thing is meant; an `also` name appears only inside a quote. "
       "`meaning` is the project's definition — never reword it into a different one; a blank one is unknown, "
       "never guessed")
PROPOSE = ("A business term in these rows that a newcomer would not know (a named thing, role, state, document "
           "or abbreviation) and that is not listed → `terms[]`: {term, meaning, also, n}. `meaning` ONLY when the "
           "source states it, else omit it. A new name for a listed term → that same `term` with the new name in "
           "`also`. Never a term per field of an entity, never a generic word")


def path_of(root):
    return os.path.join(root, "01-Requirements", FILE)


def split_names(cell):
    return [x.strip() for x in re.split(r"[;,]", cell or "") if x.strip()]


def _cells(line):
    body = line.strip()
    if not body.startswith("|"):
        return None
    return [c.replace("\x00", "|").strip() for c in body.replace(r"\|", "\x00").strip("|").split("|")]


def parse(text):
    """Rows of the first table whose header starts with `Term`: [{term, meaning, also[], source}]."""
    text = re.sub(r"<!--.*?-->", "", text or "", flags=re.S)
    rows, cols = [], None
    for line in text.splitlines():
        c = _cells(line)
        if c is None:
            if cols is not None and rows:
                break
            continue
        if cols is None:
            if c and c[0].lower() == "term":
                cols = [h.lower() for h in c]
            continue
        if all(re.match(r"^:?-{2,}:?$", x) for x in c if x):
            continue
        get = lambda name: c[cols.index(name)] if name in cols and cols.index(name) < len(c) else ""  # noqa: E731
        if get("term"):
            rows.append({"term": get("term"), "meaning": get("meaning"), "also": split_names(get("also called")),
                         "source": get("source")})
    return rows


def load(root):
    p = path_of(root)
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as f:
        return parse(f.read())


def _rx(name):
    """Whole-word, case-insensitive, tolerant of a plural `s`/`es` and of spacing."""
    body = r"\s+".join(re.escape(w) for w in name.split())
    return re.compile(r"(?<!\w)" + body + r"(?:e?s)?(?!\w)", re.I)


def key(name):
    return " ".join((name or "").lower().split())


def find(rows, text):
    """The rows whose term or any other name occurs in ``text``."""
    return [r for r in rows if any(_rx(n).search(text or "") for n in [r["term"]] + r["also"])]


def for_worklist(root, text, propose=False):
    """What an agent gets: the matching rows and the rule for using them. ``propose`` (the filer) adds the
    rule for offering new terms and is sent even when nothing matched."""
    hits = find(load(root), text)
    if not hits and not propose:
        return None
    return {"rule": USE + (". " + PROPOSE if propose else ""),
            "terms": [{k: v for k, v in (("term", r["term"]), ("meaning", r["meaning"]), ("also", r["also"])) if v}
                      for r in hits]}


def problems(rows):
    """What makes the table ambiguous: a name that leads to two terms."""
    out, owner, seen = [], {}, set()
    for r in rows:
        if key(r["term"]) in seen:
            out.append(f"'{r['term']}' has two rows — merge them")
        seen.add(key(r["term"]))
        for n in [r["term"]] + r["also"]:
            k = key(n)
            if k in owner and key(owner[k]) != key(r["term"]):
                out.append(f"'{n}' is listed under both '{owner[k]}' and '{r['term']}' — keep it in one row")
            owner.setdefault(k, r["term"])
    return out


def other_names_used(rows, text):
    """[(name used, term to write)] — an `Also called` name in ``text`` outside quotes. The terms themselves
    are masked first, so a name that is part of its own term ('account' in 'Vendor account') is not flagged."""
    text = re.sub(r"\"[^\"\n]*\"|“[^”\n]*”|`[^`\n]*`", " ", text or "")
    for r in sorted(rows, key=lambda r: -len(r["term"])):
        text = _rx(r["term"]).sub(" ", text)
    out = []
    for r in rows:
        for n in r["also"]:
            if _rx(n).search(text):
                out.append((n, r["term"]))
    return out


def merge(rows, term, also=()):
    """The existing row a proposed term belongs to (matched on any shared name), or None."""
    names = {key(term)} | {key(a) for a in also}
    for r in rows:
        if names & ({key(r["term"])} | {key(a) for a in r["also"]}):
            return r
    return None
