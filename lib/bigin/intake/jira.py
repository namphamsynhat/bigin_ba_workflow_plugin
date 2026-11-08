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
  * the phase from project.md's ``## Jira status mapping`` table (per Jira project). Phases inform
    extraction, with three exceptions: ``ignore`` (never captured), ``done`` (a note already closed is
    not re-opened while the ticket stays done) and ``dev`` — the status the team moves a ticket to once
    it is clear. Use cases and designs are drafted from a ticket long before that, so the dev team can
    review the flow and the PM a quick design while the questions go back and forth in Jira. While a
    project maps any status to ``dev``, a UC built from its tickets cannot be APPROVED until every one of
    them reaches a ``dev`` (or ``done``) status (``approval_gate()`` below, ``bigin intake jira-gate``).

A note that gains blocks goes back to ``status: raw`` so /extract-signal picks it up, the same way a
re-captured email thread does.

Sprint watch list (``sprint_start`` below, ``bigin intake jira-sprint``). At sprint start the team hands over
the sprint's ticket keys; project.md ``jira_sprint`` / ``jira_watch`` record them, and the sweep fetches only
those tickets plus their children (an Epic's new Stories join automatically). Every other ticket note is
closed — ``jira_watch: false``, ``jira_sprint_closed: <sprint>`` — and no sweep fetches it again. Nothing
is closed in Jira itself: Jira stays read-only. A ticket listed again in a later sprint is re-opened.

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

PHASES = ("active", "scope-agreed", "dev", "done", "ignore")
RELEASED = ("dev", "done")  # a ticket in these phases is clear: a UC built from it may be approved
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


def gated_projects(vault):
    """Jira projects whose status mapping names a ``dev`` phase — only these hold approval back (opt-in, so
    a vault with no ``dev`` row approves as before). ``*`` gates every project."""
    return {proj for proj, _, _, phase in status_map(vault) if phase == "dev"}


def waiting(vault, doc, gated=None):
    """None when ``doc`` holds nothing back, else ``{int, key, status, phase}``: a ``source: jira`` note
    whose project maps a ``dev`` status and whose ticket is not in a ``dev`` / ``done`` phase yet."""
    if doc is None or (doc.fm_get("source") or "") != "jira":
        return None
    key = (doc.fm_get("jira_key") or "").strip()
    phase = (doc.fm_get("jira_phase") or "active").strip()
    gated = gated_projects(vault) if gated is None else gated
    proj = key.split("-")[0].upper() if "-" in key else ""
    if phase in RELEASED or not (proj in gated or "*" in gated):
        return None
    return {"int": doc.fm_get("id") or doc.id, "key": key, "status": doc.fm_get("jira_status") or "", "phase": phase}


def ucs_from(vault, nid):
    """[(UC id, status, version)] of the live UCs whose ``sources:`` cite intake note ``nid``."""
    out = []
    for p in vault.uc_paths():
        d = vault.load(p)
        if nid in d.fm_list("sources") and (d.fm_get("status") or "") not in ("removed", "consolidated"):
            out.append((d.fm_get("id") or d.id, d.fm_get("status") or "", str(d.fm_get("version") or "")))
    return out


def designs(vault):
    """{UC id: (UX id, absorbed version)} — the UX specs built from each UC."""
    out = {}
    for p in vault.ux_paths():
        d = vault.load(p)
        for a in d.fm_list("absorbed"):
            m = re.match(r"^(UC-\d+)@(.+)$", str(a).strip())
            if m:
                out.setdefault(m.group(1), (d.fm_get("id") or d.id, m.group(2).strip()))
    return out


def approval_gate(vault, uc):
    """``{uc, ok, waiting: [{int, key, status, phase}]}`` — ok unless the UC cites a Jira ticket that has
    not reached the team's ``dev`` status. /approve-uc stops on ``ok: false``."""
    p = vault.find(uc)
    if not p:
        raise EngineError(f"intake jira-gate: {uc} not found")
    d = vault.load(p)
    gated = gated_projects(vault)
    held = []
    if gated:
        for nid in d.fm_list("sources"):
            np = vault.find(nid)
            w = waiting(vault, vault.load(np), gated) if np else None
            if w:
                held.append(w)
    return {"uc": uc, "ok": not held, "waiting": held}


def render_gate(res):
    if res["ok"]:
        return f"{res['uc']}: ok — no source ticket is waiting on Ready for Dev"
    return "\n".join([f"{res['uc']}: NOT READY — approve once these tickets reach the team's dev status:"]
                     + [f"  {w['key']} ({w['int']}) is '{w['status'] or w['phase']}'" for w in res["waiting"]])


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


# ---------------------------------------------------------------------------- sprint watch list

KEY_RE = re.compile(r"^[A-Z][A-Z0-9_]*-\d+$")


def watchlist(vault):
    """(sprint, [keys]) from project.md ``jira_sprint`` / ``jira_watch``; ([] = no sprint: the sweep query
    decides, as before the watch list existed)."""
    proj = vault.project()
    keys = [str(k).strip().upper() for k in (proj.fm_list("jira_watch") or []) if str(k).strip()]
    return (proj.fm_get("jira_sprint") or "").strip(), keys


def watched(vault, key, parent, wl=None):
    """True when the ticket, or its parent, is on the current sprint's watch list."""
    _, keys = wl if wl is not None else watchlist(vault)
    return bool(keys) and (key in keys or (parent or "").upper() in keys)


def _jira_notes(vault):
    for p in vault.note_paths():
        d = vault.load(p)
        if (d.fm_get("source") or "") == "jira" and (d.fm_get("jira_key") or "").strip():
            yield d


def sprint_start(vault, sprint, keys, dry=False):
    """Start a sprint: ``keys`` become the watch list, every other ticket note is closed (not watched any
    more). A child of a listed ticket (an Epic's Story) stays watched. Returns what changed plus the keys
    with no note yet — the skill fetches and captures those next."""
    sprint = (sprint or "").strip()
    if not sprint:
        raise EngineError("intake jira-sprint: --sprint <name> is required")
    keys = list(dict.fromkeys(k.strip().upper() for k in keys if k.strip()))
    bad = [k for k in keys if not KEY_RE.match(k)]
    if bad:
        raise EngineError(f"intake jira-sprint: not Jira keys: {', '.join(bad)}")
    if not keys:
        raise EngineError("intake jira-sprint: --keys is empty — list the sprint's tickets")
    old_sprint, _ = watchlist(vault)
    wl = (sprint, keys)
    res = {"sprint": sprint, "previous_sprint": old_sprint, "watch": keys, "kept": [], "reopened": [],
           "closed": [], "to_fetch": [], "warnings": []}
    gated = gated_projects(vault)
    seen = set()
    for d in _jira_notes(vault):
        key = d.fm_get("jira_key").strip().upper()
        seen.add(key)
        was_on = (d.fm_get("jira_watch") or "").strip().lower() != "false"
        nid = d.fm_get("id") or d.id
        if watched(vault, key, d.fm_get("jira_parent"), wl):
            (res["kept"] if was_on else res["reopened"]).append(f"{key} {nid}")
            changed = [d.fm_set("jira_watch", True), d.fm_set("jira_sprint", sprint)] if not dry else []
            if not dry and not was_on:
                _history(d, f"sprint {sprint} started: {key} is on the watch list again — sweeps resume")
            if any(changed) or (not dry and not was_on):
                vault.write(d)
        elif was_on:
            res["closed"].append(f"{key} {nid}")
            w = waiting(vault, d, gated)
            if w:
                res["warnings"].append(f"{key} ({nid}) closed while still waiting on a dev status "
                                       f"({w['status'] or w['phase']}) — its use cases cannot be approved")
            if not dry:
                d.fm_set("jira_watch", False)
                d.fm_set("jira_sprint_closed", old_sprint or sprint)
                _history(d, f"sprint {sprint} started: {key} is not on it — closed, no further sweeps")
                vault.write(d)
    res["to_fetch"] = [k for k in keys if k not in seen]
    if not dry:
        proj = vault.project()
        if not proj.fm:
            raise EngineError("project.md has no frontmatter")
        proj.fm_set("jira_sprint", sprint)
        proj.fm_set("jira_watch", keys)
        vault.write(proj)
    return res


def _feature_map(vault):
    """FEATURES.md → {slug: {status, sources:set(INT)}}."""
    from ..vault import find_tables
    out = {}
    if not os.path.exists(vault.features_file):
        return out
    fd = vault.load(vault.features_file)
    for t in find_tables(fd, fd.body_start, len(fd.lines)):
        sc, st, so = t.col("Slug"), t.col("Status"), t.col("Sources")
        if sc is None:
            continue
        for r in t.rows():
            r = r + [""] * len(t.header)
            if r[sc].strip():
                out[r[sc].strip()] = {"status": r[st].strip() if st is not None else "",
                                      "sources": set(re.findall(r"\bINT-\d+\b", r[so] if so is not None else ""))}
    return out


def classify(vault, doc, fmap, sprint_ints):
    """One sprint ticket → {key, int, type, kind, features, detail}. ``kind``:
        bug          a Bug ticket (on whichever feature it anchored to)
        new-feature  anchored to a feature every source of which is a ticket of this sprint, or extraction
                     found no feature and drafted a new-scope question (a human confirms the slug)
        update       anchored to a feature that existed before this sprint
        needs-anchor more than one existing feature fits — the open question asks which
        pending      not extracted yet; ``detail`` gives the hint from the ticket type, never a decision"""
    from .. import model
    nid = doc.fm_get("id") or doc.id
    jtype = (doc.fm_get("jira_type") or "").strip()
    res = {"key": doc.fm_get("jira_key"), "int": nid, "type": jtype, "features": [], "detail": ""}
    cells = [r.get("Feature").strip() for r in model.note_rows(doc)]
    slugs = [c for c in cells if c and not c.lower().startswith(("unresolved", "not stated", "—", "-"))]
    for s in [doc.fm_get("feature") or ""] + list(doc.fm_list("declared_features")):
        s = s.strip()
        if s and not s.lower().startswith("unresolved") and s not in slugs:
            slugs.append(s)
    slugs = list(dict.fromkeys(slugs))
    res["features"] = slugs
    ux = designs(vault)
    res["ucs"] = [{"id": u, "status": st,
                   "design": ("none" if u not in ux else ("current" if ux[u][1] == ver else "stale")),
                   "ux": ux[u][0] if u in ux else None} for u, st, ver in ucs_from(vault, nid)]
    w = waiting(vault, doc)
    res["ready_for_dev"] = w is None
    none_found = any(c.lower().startswith("unresolved — none found") or c.lower().startswith("unresolved - none found")
                     for c in cells)
    ambiguous = any(c.lower().startswith("unresolved") and "candidates" in c.lower() for c in cells)
    new = [s for s in slugs if s in fmap and fmap[s]["sources"] and fmap[s]["sources"] <= sprint_ints]
    unknown = [s for s in slugs if s not in fmap]
    if jtype.lower() == "bug":
        res["kind"] = "bug"
        res["detail"] = ("on " + ", ".join(slugs)) if slugs else "feature not resolved yet"
    elif none_found or new or unknown:
        res["kind"] = "new-feature"
        res["detail"] = (", ".join(new + unknown) + " — new this sprint") if (new or unknown) else \
            "no existing feature fits — confirm the drafted slug on the note's open question"
    elif slugs:
        res["kind"] = "update"
        res["detail"] = "changes " + ", ".join(slugs)
    elif ambiguous:
        res["kind"] = "needs-anchor"
        res["detail"] = "more than one feature fits — answer the note's open question"
    else:
        res["kind"] = "pending"
        res["detail"] = {"epic": "Epic — likely a new feature"}.get(jtype.lower(), f"{jtype or 'ticket'} — likely an update")
    return res


def sprint_report(vault):
    """Every watched ticket of the current sprint, classified (``classify``)."""
    sprint, keys = watchlist(vault)
    if not keys:
        raise EngineError("intake jira-sprint --report: no sprint watch list — start one with --sprint/--keys")
    notes = [d for d in _jira_notes(vault) if (d.fm_get("jira_watch") or "").lower() != "false"
             and watched(vault, d.fm_get("jira_key").strip().upper(), d.fm_get("jira_parent"), (sprint, keys))]
    ints = {d.fm_get("id") or d.id for d in notes}
    fmap = _feature_map(vault)
    tickets = [classify(vault, d, fmap, ints) for d in notes]
    have = {t["key"] for t in tickets}
    counts = {}
    for t in tickets:
        counts[t["kind"]] = counts.get(t["kind"], 0) + 1
    return {"sprint": sprint, "tickets": tickets, "counts": counts,
            "not_fetched": [k for k in keys if k not in have]}


ORDER = ("new-feature", "update", "bug", "needs-anchor", "pending")


def render_report(res):
    c = res["counts"]
    lines = [f"sprint {res['sprint']}: " + ", ".join(f"{c[k]} {k}" for k in ORDER if c.get(k)) or "no tickets"]
    for k in ORDER:
        for t in (x for x in res["tickets"] if x["kind"] == k):
            lines.append(f"  {k:<12} {t['key']:<10} {t['int']:<8} {t['type']:<6} {t['detail']}")
            for u in t.get("ucs", []):
                lines.append(f"  {'':<12} └ {u['id']} {u['status']} · design {u['design']}"
                             + (f" ({u['ux']})" if u["ux"] else "")
                             + ("" if t["ready_for_dev"] else " · approval waits for Ready for Dev"))
    if res["not_fetched"]:
        lines.append(f"  not fetched yet: {', '.join(res['not_fetched'])}")
    return "\n".join(lines)


def render_sprint(res):
    lines = [f"sprint {res['sprint']}" + (f" (was {res['previous_sprint']})" if res["previous_sprint"] else "")
             + f": watching {len(res['watch'])} ticket(s)"]
    for k in ("kept", "reopened", "closed"):
        if res[k]:
            lines.append(f"  {k}: {', '.join(res[k])}")
    if res["to_fetch"]:
        lines.append(f"  to_fetch (no note yet — fetch + capture now): {', '.join(res['to_fetch'])}")
    lines += [f"  ! {w}" for w in res["warnings"]]
    return "\n".join(lines)


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
    wl = watchlist(vault)
    on_list = watched(vault, key, t["parent"], wl)
    if wl[1] and note is not None and not on_list and (note.fm_get("jira_watch") or "").lower() == "false":
        warnings.append(f"{key}: not on sprint {wl[0]}'s watch list (closed) — captured only because it was "
                        f"fetched explicitly; it stays closed")

    if note is None:
        spec = {
            "title": f"{key} {t['summary']}".strip(), "kind": _kind(t), "source": "jira",
            "source_ref": f"{key} — {t['summary']}", "source_ids": [f'"{s}"' for s in sids], "blocks": blocks,
            "declared_features": _inherited_features(vault, t["parent"]),
            "fm": dict(jira_fm, **({"jira_watch": "true", "jira_sprint": f'"{wl[0]}"'} if on_list else {}),
                       participants=[f'"{n} ({s})"' for n, s in sorted(sides.items())],
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
    was = (note.fm_get("jira_phase") or "active").strip()
    if was != phase:
        res["previous_phase"] = was
        if phase in RELEASED and was not in RELEASED and gated_projects(vault) & {t["project"].upper(), "*"}:
            res["released"] = True  # the ticket just reached dev: the UCs built from it may now be approved
            res["ready_ucs"] = [u for u, _, _ in ucs_from(vault, note.fm_get("id") or note.id)]
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
    if on_list and (note.fm_get("jira_watch") or "").lower() != "false":
        note.fm_set("jira_watch", True)
        note.fm_set("jira_sprint", wl[0])
    if res["unknown_authors"] and "needs-review" not in note.fm_list("tags"):
        note.fm_set("tags", note.fm_list("tags") + ["needs-review"])
    if blocks and (note.fm_get("kind") or "") != "info":
        note.fm_set("status", "raw")
    note.fm_set("updated", today())
    _history(note, f"jira sweep {key} ({t['status']} → phase {phase}): {len(blocks)} new block(s)"
             + ("; note re-opened (status: raw)" if blocks else "")
             + ("; ticket reached dev — its use cases may now be approved" if res.get("released") else ""))
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
             f"new_blocks={res['new_blocks']}" + (f"  unknown={', '.join(res['unknown_authors'])}" if res["unknown_authors"] else "")
             + (f"  (was {res['previous_phase']})" if res.get("previous_phase") else "")
             + (("  READY FOR DEV → approve " + (", ".join(res["ready_ucs"]) or "(no use case drafted yet)"))
                if res.get("released") else "")]
    lines += [f"  ! {w}" for w in res["warnings"]]
    return "\n".join(lines)
