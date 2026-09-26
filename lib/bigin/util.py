"""Small shared helpers: dates, id ordering, JSON I/O, output."""
import datetime
import hashlib
import json
import os
import re
import sys

ID_RE = re.compile(r"\b(UC|BR|INT|EN|PP|UX|PRD|FR|SCN)-(\d+)\b")


def today():
    """ISO date. BIGIN_TODAY overrides it so tests and replays are reproducible."""
    return os.environ.get("BIGIN_TODAY") or datetime.date.today().isoformat()


def now_stamp():
    return datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")


def num_key(ident):
    """Sort key for ids like UC-007, BR-2550, S12, '12a'."""
    m = re.search(r"(\d+)", str(ident))
    return (str(ident).split("-")[0] if "-" in str(ident) else "", int(m.group(1)) if m else 0, str(ident))


def sort_ids(ids):
    return sorted(dict.fromkeys(ids), key=num_key)


def sha(text):
    """Anchor fingerprint: sha1 of whitespace-normalised text (first 12 hex chars)."""
    norm = re.sub(r"\s+", " ", (text or "")).strip()
    return hashlib.sha1(norm.encode("utf-8")).hexdigest()[:12]


def norm_ws(text):
    return re.sub(r"\s+", " ", text or "").strip()


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def dump_json(obj, path=None):
    text = json.dumps(obj, indent=2, ensure_ascii=False) + "\n"
    if path:
        d = os.path.dirname(os.path.abspath(path))
        os.makedirs(d, exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, path)
    return text


def load_jsonl(path):
    out = []
    if not os.path.exists(path):
        return out
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def append_jsonl(path, obj):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def batch_mode():
    return os.environ.get("BIGIN_BATCH") == "1"


class EngineError(Exception):
    """A refusal the caller should see as one line, not a traceback."""


def say(*parts):
    print(*parts)
    sys.stdout.flush()
