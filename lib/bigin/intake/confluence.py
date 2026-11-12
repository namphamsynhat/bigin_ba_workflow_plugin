"""Confluence / shared docs as a living intake note (``bigin intake confluence --page <raw.json>``).

One INT note per page, for the page's life — the Jira living-note pattern. The skill fetches (read tools only) and
dumps the raw page; the engine does the delta:

  raw.json  {"id": "12345", "title": "...", "version": 7, "space": "ACME", "url": "...", "updated": "2026-10-03",
             "author": "Jane Roe", "body": "<markdown>"  |  <ADF document>}

First capture mints the note (``source: confluence``) with one ``### SRC-n · section · <heading>`` block per
heading section. The high-water mark is ``conf:<pageId>@v<version>`` in ``source_ids``; the last captured body is
kept in ``00-Inbox/_raw/confluence/<pageId>.json``. On a newer version the page is diffed by heading section:
changed and added sections are appended as one block each, a removed section as one block of kind ``removed``
(so the extractor writes a ``supersedes`` row), and the note returns to ``status: raw``. An older or equal
version is a no-op.
"""
import json
import os
import re

from ..ids import mint_int
from ..util import EngineError, load_json, norm_ws, today
from .common import _history, append_blocks
from .jira import adf_to_md

HEAD = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
INTRO = "(intro)"


def sections(body):
    """[(key, heading line or '', text)] in page order. Text before the first heading is the intro; a repeated
    heading gets ``#2``, ``#3`` so every key is unique and stable."""
    out, seen = [], {}
    cur_key, cur_head, cur = INTRO, "", []
    fence = False

    def flush():
        text = "\n".join(cur).strip("\n")
        if text.strip() or cur_head:
            out.append((cur_key, cur_head, text))

    for ln in (body or "").splitlines():
        if ln.lstrip().startswith("```"):
            fence = not fence
        m = None if fence else HEAD.match(ln)
        if m:
            flush()
            title = m.group(2).strip() or "(untitled)"
            seen[title] = seen.get(title, 0) + 1
            cur_key = title if seen[title] == 1 else f"{title} #{seen[title]}"
            cur_head, cur = ln.strip(), [ln.rstrip()]
        else:
            cur.append(ln.rstrip())
    flush()
    return out


def _safe(text):
    """A heading inside ``## Raw`` must not read as a note section or a ``### SRC-n`` block: every heading line in
    the page text is written as a level-4 heading."""
    out, fence = [], False
    for ln in text.splitlines():
        if ln.lstrip().startswith("```"):
            fence = not fence
        m = None if fence else HEAD.match(ln)
        out.append(f"#### {m.group(2).strip()}" if m else ln)
    return "\n".join(out)


def _page(raw):
    if not isinstance(raw, dict) or not raw.get("id") or raw.get("version") in (None, ""):
        raise EngineError("intake confluence: the page JSON needs at least {id, version, body}")
    body = raw.get("body")
    if isinstance(body, dict):
        body = adf_to_md(body)
    try:
        version = int(raw["version"])
    except (TypeError, ValueError):
        raise EngineError(f"intake confluence: version '{raw['version']}' is not a number") from None
    return {"id": str(raw["id"]).strip(), "title": (raw.get("title") or "").strip(), "version": version,
            "space": (raw.get("space") or "").strip(), "url": (raw.get("url") or "").strip(),
            "updated": str(raw.get("updated") or today())[:10], "author": (raw.get("author") or "").strip(),
            "body": body or ""}


def find_note(vault, page_id):
    for p in vault.note_paths():
        d = vault.load(p)
        if (d.fm_get("source") or "") == "confluence" and (str(d.fm_get("confluence_id") or "").strip().strip('"') == page_id
                                                           or any(str(s).startswith(f"conf:{page_id}@") for s in d.fm_list("source_ids"))):
            return d
    return None


def _version_of(doc, page_id):
    for s in doc.fm_list("source_ids"):
        m = re.match(rf'^"?conf:{re.escape(page_id)}@v(\d+)"?$', str(s).strip())
        if m:
            return int(m.group(1))
    return 0


def _store_path(vault, page_id):
    return os.path.join(vault.inbox, "_raw", "confluence", f"{page_id}.json")


def _stored(vault, page_id):
    p = _store_path(vault, page_id)
    try:
        return load_json(p) if os.path.exists(p) else None
    except (OSError, ValueError):
        return None


def _save(vault, pg, secs):
    p = _store_path(vault, pg["id"])
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump({"id": pg["id"], "version": pg["version"], "title": pg["title"], "updated": pg["updated"],
                   "sections": {k: t for k, _h, t in secs}, "order": [k for k, _h, _t in secs]}, f, indent=2, ensure_ascii=False)


def _ref(pg, key):
    who = f" {pg['author']}" if pg["author"] else ""
    return f"{pg['title'] or pg['id']} › {key} — v{pg['version']}{who} {pg['updated']}"


def _delta(pg, secs, old):
    """Blocks for what changed against the stored copy; the whole page when there is none."""
    if old is None:
        return [{"kind": "section", "ref": _ref(pg, k), "text": _safe(t)} for k, _h, t in secs if t.strip()], []
    prev = old.get("sections") or {}
    blocks, removed = [], []
    for k, _h, t in secs:
        if norm_ws(prev.get(k)) != norm_ws(t) and t.strip():
            blocks.append({"kind": "section", "ref": _ref(pg, k), "text": _safe(t)})
    now = {k for k, _h, _t in secs}
    for k in old.get("order") or list(prev):
        if k not in now:
            removed.append(k)
            blocks.append({"kind": "removed", "ref": _ref(pg, k),
                           "text": f"This section was removed from the page in v{pg['version']}: **{k}**. "
                                   f"Nothing under this heading is current any more."})
    return blocks, removed


def capture(vault, raw_path, dry=False):
    pg = _page(load_json(raw_path))
    secs = sections(pg["body"])
    note = find_note(vault, pg["id"])
    res = {"page": pg["id"], "title": pg["title"], "version": pg["version"], "new_blocks": 0, "removed": []}
    sid = f'"conf:{pg["id"]}@v{pg["version"]}"'
    fm = {"confluence_id": f'"{pg["id"]}"', "confluence_version": pg["version"]}
    if pg["url"]:
        fm["confluence_url"] = f'"{pg["url"]}"'
    if note is None:
        blocks, _ = _delta(pg, secs, None)
        res["new_blocks"] = len(blocks)
        if dry:
            return dict(res, action="mint", id="INT-(next)", path="(dry)")
        spec = {"title": pg["title"] or f"Confluence page {pg['id']}", "kind": "requirement", "source": "confluence",
                "source_ref": f"{pg['title']} (Confluence {pg['space'] or pg['id']})".strip(), "source_ids": [sid],
                "blocks": blocks, "fm": fm}
        nid, path = mint_int(vault, spec)
        vault.forget(path)
        d = vault.load(path)
        _history(d, f"captured Confluence page {pg['id']} v{pg['version']}: {len(blocks)} section block(s)")
        vault.write(d)
        _save(vault, pg, secs)
        return dict(res, action="minted", id=nid, path=vault.rel(path))

    nid = note.fm_get("id") or note.id
    have = _version_of(note, pg["id"])
    if pg["version"] <= have:
        return dict(res, action="unchanged", id=nid, path=vault.rel(note.path))
    blocks, removed = _delta(pg, secs, _stored(vault, pg["id"]))
    res.update(new_blocks=len(blocks), removed=removed)
    if dry:
        return dict(res, action="append", id=nid, path=vault.rel(note.path))
    if blocks:
        nums = append_blocks(note, blocks)
        from .. import questions
        questions.prematch(vault, note, [(f"SRC-{n}", b["text"]) for n, b in zip(nums, blocks)])
    keep = [s for s in note.fm_list("source_ids") if not str(s).strip().strip('"').startswith(f"conf:{pg['id']}@")]
    note.fm_set("source_ids", keep + [sid])
    for k, v in fm.items():
        note.fm_set(k, v)
    if blocks and (note.fm_get("status") or "") != "withdrawn":
        note.fm_set("status", "raw")
    note.fm_set("updated", today())
    _history(note, f"Confluence page {pg['id']} v{have} → v{pg['version']}: {len(blocks)} new block(s)"
             + (f", {len(removed)} section(s) removed" if removed else "")
             + ("; note re-opened (status: raw)" if blocks else ""))
    vault.write(note)
    _save(vault, pg, secs)
    return dict(res, action="appended" if blocks else "updated", id=nid, path=vault.rel(note.path))


def render(res):
    return (f"{res['page']}  {res['action']}  {res.get('id') or '—'}  v{res['version']}  new_blocks={res['new_blocks']}"
            + (f"  removed: {', '.join(res['removed'])}" if res.get("removed") else ""))
