"""Jira capture for /bigin-intake (``source: jira``): one living INT note per ticket.

The skill fetches the ticket through the Atlassian MCP and dumps the raw responses to
``00-Inbox/_raw/jira/<KEY>.json``; everything after that is deterministic and lives here:

  * ADF (Atlassian Document Format) → markdown, verbatim — no paraphrase.
  * each author → a side (onshore / offshore / unknown) from project.md.
  * the delta against what the note already holds. ``source_ids`` is the high-water mark:
        jira:KEY                 the ticket itself
        jira:KEY#c<id>@<ts>      one comment at one edit time (a new <ts> = an edited comment)
        jira:KEY#desc@<hash>     one revision of the summary + description
        jira:KEY#chg<id>         one changelog entry
    Only events whose id is not there yet become new ``### SRC-n`` blocks, in chronological order.
    Existing blocks are never edited (``intake.md`` § Raw: append newest content as a NEW block).
  * the phase from project.md's ``## Jira status mapping`` table (per Jira project). The phase is
    informational — it gates nothing — except ``ignore`` (never captured) and ``done`` (a note
    already closed is not re-opened while the ticket stays done).

A note that gains blocks goes back to ``status: raw`` so /extract-signal picks it up, the same way a
re-captured email thread does.

raw.json — either the bare ``getJiraIssue`` response, or
    {"issue": {...}, "comments": [...] | {"comments"|"values": [...]},
     "changelog": [...] | {"histories"|"values": [...]}}
Comments and changelog may also sit inside the issue (``fields.comment.comments``,
``changelog.histories``) when the issue was fetched with them expanded.
"""
import hashlib
import os
import re

from ..ids import mint_int
from ..util import EngineError, load_json, today

PHASES = ("active", "scope-agreed", "done", "ignore")
# changelog fields worth a block; summary/description revisions arrive as description blocks instead
FIELDS = {"status", "issuetype", "parent", "labels", "priority", "fixversions", "resolution",
          "assignee", "epic link", "epic child", "sprint", "components"}


# ---------------------------------------------------------------------------- ADF → markdown

def adf_to_md(node):
    """Render an ADF document (or a plain string) as markdown. Unknown nodes keep their text."""
    if node is None:
        return ""
    if isinstance(node, str):
        return node.strip()
    out = _blocks(node.get("content") or []) if node.get("type") == "doc" else _block(node, 0)
    return re.sub(r"\n{3,}", "\n\n", out).strip()


def _blocks(nodes, depth=0):
    return "\n\n".join(b for b in (_block(n, depth) for n in nodes) if b.strip())


def _block(n, depth):
    t = n.get("type")
    c = n.get("content") or []
    if t == "paragraph":
        return _inline(c)
    if t == "heading":
        return "#" * min(int((n.get("attrs") or {}).get("level", 3)), 6) + " " + _inline(c)
    if t in ("bulletList", "orderedList"):
        lines = []
        for i, item in enumerate(c, 1):
            mark = f"{i}." if t == "orderedList" else "-"
            body = _blocks(item.get("content") or [], depth + 1).split("\n")
            lines.append("  " * depth + f"{mark} {body[0]}")
            lines += ["  " * depth + "  " + x if x.strip() else x for x in body[1:]]
        return "\n".join(lines)
    if t == "codeBlock":
        lang = (n.get("attrs") or {}).get("language") or ""
        return f"```{lang}\n" + "".join(x.get("text", "") for x in c) + "\n```"
    if t == "blockquote":
        return "\n".join("> " + x for x in _blocks(c, depth).split("\n"))
    if t == "rule":
        return "---"
    if t == "table":
        rows = [[_blocks(cell.get("content") or []).replace("\n", " ").replace("|", "/")
                 for cell in (r.get("content") or [])] for r in c]
        if not rows:
            return ""
        width = max(len(r) for r in rows)
        rows = [r + [""] * (width - len(r)) for r in rows]
        return "\n".join(["| " + " | ".join(rows[0]) + " |", "|" + "---|" * width] +
                         ["| " + " | ".join(r) + " |" for r in rows[1:]])
    if t in ("panel", "expand", "nestedExpand", "layoutSection", "layoutColumn", "listItem", "doc"):
        return _blocks(c, depth)
    if t in ("mediaSingle", "mediaGroup", "media"):
        return "[attachment]"
    return _inline([n]) if "text" in n or t in _INLINE else _blocks(c, depth)


_INLINE = {"text", "hardBreak", "mention", "emoji", "inlineCard", "date", "status"}


def _inline(nodes):
    out = []
    for n in nodes:
        t = n.get("type")
        a = n.get("attrs") or {}
        if t == "text":
            s = n.get("text", "")
            for m in n.get("marks") or []:
                mt = m.get("type")
                if mt == "code":
                    s = f"`{s}`"
                elif mt == "strong":
                    s = f"**{s}**"
                elif mt == "em":
                    s = f"*{s}*"
                elif mt == "strike":
                    s = f"~~{s}~~"
                elif mt == "link":
                    s = f"[{s}]({(m.get('attrs') or {}).get('href', '')})"
            out.append(s)
        elif t == "hardBreak":
            out.append("\n")
        elif t == "mention":
            out.append(a.get("text") or "@" + str(a.get("id", "")))
        elif t == "emoji":
            out.append(a.get("text") or a.get("shortName", ""))
        elif t == "inlineCard":
            out.append(a.get("url", ""))
        elif t == "date":
            out.append(str(a.get("timestamp", "")))
        elif t == "status":
            out.append(f"[{a.get('text', '')}]")
        else:
            out.append(_block(n, 0))
    return "".join(out)


# ---------------------------------------------------------------------------- normalize

def _list(v, *keys):
    if v is None:
        return []
    if isinstance(v, list):
        return v
    for k in keys:
        if isinstance(v.get(k), list):
            return v[k]
    return []


def _person(p):
    p = p or {}
    if isinstance(p, str):
        return {"name": p, "ids": {p.lower()}}
    name = p.get("displayName") or p.get("name") or p.get("emailAddress") or p.get("accountId") or "unknown"
    ids = {str(x).lower() for x in (p.get("displayName"), p.get("emailAddress"), p.get("accountId"), p.get("name")) if x}
    return {"name": name, "ids": ids}


def _name(v):
    if isinstance(v, dict):
        return v.get("name") or v.get("value") or v.get("key") or ""
    return v or ""


def normalize(raw):
    """Any accepted raw shape → one flat ticket dict."""
    issue = raw.get("issue", raw) if isinstance(raw, dict) else None
    if not isinstance(issue, dict) or not issue.get("key"):
        raise EngineError("jira raw: no issue key — expected getJiraIssue's response (or {\"issue\": …})")
    f = issue.get("fields") or {}
    comments = _list(raw.get("comments"), "comments", "values") if "comments" in raw else \
        _list(f.get("comment"), "comments", "values")
    changes = _list(raw.get("changelog"), "histories", "values") if "changelog" in raw and raw is not issue else \
        _list(issue.get("changelog"), "histories", "values")
    key = issue["key"]
    parent = f.get("parent") or {}
    return {
        "key": key,
        "project": (f.get("project") or {}).get("key") or key.rsplit("-", 1)[0],
        "type": _name(f.get("issuetype")),
        "status": _name(f.get("status")),
        "summary": (f.get("summary") or "").strip(),
        "description": adf_to_md(f.get("description")),
        "parent": parent.get("key", "") if isinstance(parent, dict) else str(parent),
        "labels": list(f.get("labels") or []),
        "priority": _name(f.get("priority")),
        "reporter": _person(f.get("reporter") or f.get("creator")),
        "assignee": _person(f.get("assignee")) if f.get("assignee") else None,
        "created": f.get("created") or "",
        "updated": f.get("updated") or f.get("created") or "",
        "comments": sorted(({"id": str(c.get("id")), "author": _person(c.get("author")),
                             "created": c.get("created") or "", "updated": c.get("updated") or c.get("created") or "",
                             "body": adf_to_md(c.get("body"))} for c in comments), key=lambda c: (c["created"], c["id"])),
        "changes": sorted(({"id": str(h.get("id")), "author": _person(h.get("author")), "created": h.get("created") or "",
                            "items": [{"field": (i.get("field") or i.get("fieldId") or "").strip(),
                                       "from": i.get("fromString") or "", "to": i.get("toString") or ""}
                                      for i in (h.get("items") or [])]} for h in changes),
                          key=lambda h: (h["created"], h["id"])),
    }


# ---------------------------------------------------------------------------- config

def _cfg_list(vault, key):
    return [str(x).strip().lower() for x in (vault.project().fm_list(key) or []) if str(x).strip()]


def side_of(vault, person):
    """onshore | offshore | unknown. jira_onshore/jira_offshore first, then client_emails/team_emails.
    An entry matches an account id, an email or a display name exactly, or an email's domain
    when the entry is a bare domain (``acme.com`` / ``@acme.com``)."""
    ids = person["ids"]
    for side, keys in (("onshore", ("jira_onshore", "client_emails")), ("offshore", ("jira_offshore", "team_emails"))):
        for key in keys:
            for entry in _cfg_list(vault, key):
                if entry in ids:
                    return side
                dom = entry.lstrip("@")
                if "@" not in dom and "." in dom and any(i.endswith("@" + dom) for i in ids):
                    return side
    return "unknown"


def status_map(vault):
    """project.md ``## Jira status mapping`` → [(project, {types}|None, status, phase)]."""
    doc = vault.project()
    t = doc.table("Jira status mapping") if doc.lines else None
    out = []
    if t is None:
        return out
    cp, ct, cs, cph = (t.col(x) for x in ("Project", "Issue type", "Jira status", "Phase"))
    if None in (cp, cs, cph):
        raise EngineError("project.md ## Jira status mapping: needs Project | Issue types | Jira status | Phase columns")
    for r in t.rows():
        r = r + [""] * 4
        proj, status, phase = r[cp].strip(), r[cs].strip(), r[cph].strip().lower()
        if not proj or not status:
            continue
        if phase not in PHASES:
            raise EngineError(f"project.md ## Jira status mapping: phase '{phase}' is not one of {', '.join(PHASES)}")
        types = r[ct].strip() if ct is not None else ""
        tset = None if types in ("", "*", "any") else {x.strip().lower() for x in types.split(",") if x.strip()}
        out.append((proj.upper(), tset, status.lower(), phase))
    return out


def phase_for(vault, t):
    """(phase, mapped). An unmapped status counts as ``active`` and is reported, never guessed."""
    for proj, tset, status, phase in status_map(vault):
        if proj not in (t["project"].upper(), "*"):
            continue
        if tset is not None and t["type"].lower() not in tset:
            continue
        if status in (t["status"].lower(), "*"):
            return phase, True
    return "active", False


# ---------------------------------------------------------------------------- delta

def _ts(s):
    """Jira timestamp → compact UTC-ish ISO for refs (2026-10-02T03:10:00.000+0700 → 2026-10-02T03:10+0700)."""
    m = re.match(r"^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2})(?::\d{2}(?:\.\d+)?)?(Z|[+-]\d{2}:?\d{2})?", s or "")
    return f"{m.group(1)}T{m.group(2)}{m.group(3) or ''}" if m else (s or "")


def _desc_hash(t):
    return hashlib.sha1((t["summary"] + "\n" + t["description"]).encode("utf-8")).hexdigest()[:10]


def _who(vault, person, seen):
    side = side_of(vault, person)
    seen.setdefault(person["name"], side)
    return f"{person['name']} ({side})"


def events(vault, t, have):
    """New (sort key, block, source_id) triples for everything ``have`` (the note's source_ids) lacks."""
    key = t["key"]
    have = set(have)
    sides = {}
    out = []
    first = f"jira:{key}" not in have
    dh = _desc_hash(t)
    if first:
        head = [f"Type: {t['type'] or '—'} · Status: {t['status'] or '—'} · Priority: {t['priority'] or '—'}"
                + (f" · Parent: {t['parent']}" if t["parent"] else "")
                + (f" · Labels: {', '.join(t['labels'])}" if t["labels"] else "")]
        if t["assignee"]:
            head.append(f"Assignee: {_who(vault, t['assignee'], sides)}")
        text = "\n".join(head) + f"\n\n**{t['summary']}**\n\n" + (t["description"] or "_(no description)_")
        ref = f"{key} — {_who(vault, t['reporter'], sides)} {_ts(t['created'])}"
        out.append(((t["created"], "0"), {"kind": "ticket", "ref": ref, "text": text}, [f"jira:{key}", f"jira:{key}#desc@{dh}"]))
    elif f"jira:{key}#desc@{dh}" not in have:
        when, by = t["updated"], None
        for h in t["changes"]:
            if any(i["field"].lower() in ("description", "summary") for i in h["items"]):
                when, by = h["created"], h["author"]
        ref = f"{key}#desc — " + (f"{_who(vault, by, sides)} " if by else "") + _ts(when)
        out.append(((when, "1"), {"kind": "description", "ref": ref,
                                  "text": f"**{t['summary']}**\n\n" + (t["description"] or "_(no description)_")},
                    [f"jira:{key}#desc@{dh}"]))
    for c in t["comments"]:
        sid = f"jira:{key}#c{c['id']}@{_ts(c['updated'])}"
        if sid in have:
            continue
        edited = any(h.startswith(f"jira:{key}#c{c['id']}@") for h in have)
        ref = f"{key}#c{c['id']} — {_who(vault, c['author'], sides)} {_ts(c['created'])}" + \
            (f" (edited {_ts(c['updated'])})" if edited else "")
        out.append(((c["updated"] if edited else c["created"], "2" + c["id"]),
                    {"kind": "comment", "ref": ref, "text": c["body"] or "_(empty comment)_"}, [sid]))
    for h in t["changes"]:
        sid = f"jira:{key}#chg{h['id']}"
        if sid in have:
            continue
        items = [i for i in h["items"] if i["field"].lower() in FIELDS]
        if not items:
            out.append(((h["created"], "3" + h["id"]), None, [sid]))  # remembered, never a block
            continue
        text = "\n".join(f"- {i['field']}: {i['from'] or '—'} → {i['to'] or '—'}" for i in items)
        ref = f"{key}#chg{h['id']} — {_who(vault, h['author'], sides)} {_ts(h['created'])}"
        out.append(((h["created"], "3" + h["id"]), {"kind": "fields", "ref": ref, "text": text}, [sid]))
    out.sort(key=lambda e: e[0])
    return out, sides


# ---------------------------------------------------------------------------- capture

def find_note(vault, key):
    for p in vault.note_paths():
        d = vault.load(p)
        if d.fm_get("jira_key") == key or f"jira:{key}" in d.fm_list("source_ids"):
            return d
    return None


def _inherited_features(vault, parent):
    if not parent:
        return []
    d = find_note(vault, parent)
    if d is None:
        return []
    feat = (d.fm_get("feature") or "").strip()
    return [feat] if feat and not feat.startswith("unresolved") else list(d.fm_list("declared_features"))


def _kind(t):
    return "feedback" if t["type"].lower() == "bug" else "requirement"


def capture(vault, raw_path, dry=False):
    t = normalize(load_json(raw_path))
    key = t["key"]
    phase, mapped = phase_for(vault, t)
    note = find_note(vault, key)
    warnings = [] if mapped else [f"{key}: status '{t['status']}' ({t['project']} {t['type']}) is not in "
                                   f"## Jira status mapping — treated as active"]
    res = {"key": key, "type": t["type"], "status": t["status"], "phase": phase, "warnings": warnings,
           "new_blocks": 0, "unknown_authors": []}
    if note is None and phase == "ignore":
        return dict(res, action="ignored", id=None, path=None)
    have = note.fm_list("source_ids") if note is not None else []
    evs, sides = events(vault, t, have)
    blocks = [e[1] for e in evs if e[1]]
    sids = [s for e in evs for s in e[2]]
    res["unknown_authors"] = sorted(n for n, s in sides.items() if s == "unknown")
    res["new_blocks"] = len(blocks)
    jira_fm = {"jira_key": key, "jira_type": t["type"], "jira_parent": t["parent"], "jira_status": t["status"],
               "jira_phase": phase, "jira_updated": _ts(t["updated"])}

    if note is None:
        spec = {
            "title": f"{key} {t['summary']}".strip(), "kind": _kind(t), "source": "jira",
            "source_ref": f"{key} — {t['summary']}", "source_ids": [f'"{s}"' for s in sids], "blocks": blocks,
            "declared_features": _inherited_features(vault, t["parent"]),
            "fm": dict(jira_fm, participants=[f'"{n} ({s})"' for n, s in sorted(sides.items())],
                       tags=["needs-review"] if res["unknown_authors"] else []),
        }
        if dry:
            return dict(res, action="mint", id="INT-(next)", path="(dry)")
        nid, path = mint_int(vault, spec)
        vault.forget(path)
        d = vault.load(path)
        _history(d, f"captured {key} ({t['type']}, {t['status']} → phase {phase}): {len(blocks)} block(s)")
        vault.write(d)
        return dict(res, action="minted", id=nid, path=vault.rel(path))

    nid = note.fm_get("id") or note.id
    closed = (note.fm_get("jira_phase") or "") == "done" and phase == "done"
    if closed:
        return dict(res, action="closed", id=nid, path=vault.rel(note.path), new_blocks=0)
    if not sids and all((note.fm_get(k) or "") == str(v) for k, v in jira_fm.items()):
        return dict(res, action="unchanged", id=nid, path=vault.rel(note.path))
    if dry:
        return dict(res, action="append", id=nid, path=vault.rel(note.path))
    append_blocks(note, blocks)
    note.fm_set("source_ids", have + sids)
    for k, v in jira_fm.items():
        note.fm_set(k, v)
    people = note.fm_list("participants")
    for n, s in sorted(sides.items()):
        if f"{n} ({s})" not in people:
            people.append(f"{n} ({s})")
    note.fm_set("participants", people)
    if res["unknown_authors"] and "needs-review" not in note.fm_list("tags"):
        note.fm_set("tags", note.fm_list("tags") + ["needs-review"])
    if blocks and (note.fm_get("kind") or "") != "info":
        note.fm_set("status", "raw")
    note.fm_set("updated", today())
    _history(note, f"jira sweep {key} ({t['status']} → phase {phase}): {len(blocks)} new block(s)"
             + ("; note re-opened (status: raw)" if blocks else ""))
    vault.write(note)
    return dict(res, action="appended" if blocks else "updated", id=nid, path=vault.rel(note.path))


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


def render(res):
    lines = [f"{res['key']}  {res['action']}  {res.get('id') or '—'}  phase={res['phase']}  "
             f"new_blocks={res['new_blocks']}" + (f"  unknown={', '.join(res['unknown_authors'])}" if res["unknown_authors"] else "")]
    lines += [f"  ! {w}" for w in res["warnings"]]
    return "\n".join(lines)
