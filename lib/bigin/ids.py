"""Id minting under a file lock, and template instantiation.

Ported from Agoyu ``mint_uc.py``: next id = highest id already in use (read from every file's
``id:`` and file name, not just file names) + 1; a UC with the same title is refused; the new id
is pointed at from its hubs and FEATURES.md. Parallel-safe: every mint holds an exclusive
``fcntl`` lock on ``01-Requirements/.ids.lock`` from "read the highest id" to "file written".
"""
import contextlib
import glob
import os
import re

from .util import EngineError, load_json, today
from .vault import Doc, strip_comments

try:
    import fcntl
except ImportError:  # pragma: no cover - non-POSIX
    fcntl = None

WIDTH = 3


@contextlib.contextmanager
def id_lock(vault):
    os.makedirs(vault.req, exist_ok=True)
    path = os.path.join(vault.req, ".ids.lock")
    with open(path, "a+") as f:
        if fcntl:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            if fcntl:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def _scan_numbers(paths, kind):
    nums = []
    for p in paths:
        m = re.match(rf"^{kind}-(\d+)", os.path.basename(p))
        if m:
            nums.append(int(m.group(1)))
        try:
            with open(p, "r", encoding="utf-8") as f:
                head = f.read(4096)
        except OSError:
            continue
        m = re.search(rf"^id:\s*{kind}-(\d+)", head, re.M)
        if m:
            nums.append(int(m.group(1)))
    return nums


def highest(vault, kind):
    if kind == "UC":
        nums = _scan_numbers(glob.glob(os.path.join(vault.uc_dir, "*.md")), "UC")
    elif kind == "BR":
        nums = _scan_numbers(glob.glob(os.path.join(vault.br_dir, "*.md")), "BR")
    elif kind in ("EP", "US"):
        # vault-global: every epic folder, plus anything left under 03-Epics-Stories by hand
        nums = _scan_numbers(glob.glob(os.path.join(vault.stories_dir, "**", f"{kind}-*.md"), recursive=True), kind)
    elif kind == "INT":
        nums = _scan_numbers(glob.glob(os.path.join(vault.inbox, "INT-*.md")), "INT")
    elif kind in ("PP", "EN"):
        reg = os.path.join(vault.req, "PAIN-POINTS.md" if kind == "PP" else "ENTITIES.md")
        text = open(reg, encoding="utf-8").read() if os.path.exists(reg) else ""
        nums = [int(x) for x in re.findall(rf"\b{kind}-(\d+)\b", text)]
        if kind == "EN":
            nums += _scan_numbers(glob.glob(os.path.join(vault.entity_dir, "*.md")), "EN")
    else:
        raise EngineError(f"cannot mint {kind}")
    return max(nums or [0])


def fmt(kind, n):
    return f"{kind}-{n:0{WIDTH}d}"


def safe_title(title):
    return re.sub(r"\s+", " ", re.sub(r'[\\/:*?"<>|#^\[\]]', "-", title)).strip()[:120]


# ---------------------------------------------------------------------------- templates

def _fm_default(raw_value):
    v = re.sub(r"\s+#.*$", "", raw_value).strip()
    return v


def instantiate(vault, template, values, heading, body_hook=None):
    """Instantiate ``template`` (a _bigin/templates name) with frontmatter ``values``.

    Copies the structure, not the guidance (paths.md § Templates): frontmatter comments and every
    ``<!-- -->`` block are dropped, except a single ``<!-- guide: … -->`` pointer if the template
    carries one. Keys not in ``values`` keep the template's default."""
    tpl = open(vault.template_path(template), encoding="utf-8").read()
    doc = Doc(tpl)
    fm_lines = ["---"]
    seen = set()
    for key in doc.fm.keys():
        a, b = doc.fm.entries[key]
        raw = doc.lines[1 + a].split(":", 1)[1]
        seen.add(key)
        if key in values:
            fm_lines.append(_render_kv(key, values[key]))
        else:
            fm_lines.append(f"{key}: {_fm_default(raw)}".rstrip())
    for key, v in values.items():
        if key not in seen:
            fm_lines.append(_render_kv(key, v))
    fm_lines.append("---")
    body = "\n".join(doc.lines[doc.body_start:])
    guides = re.findall(r"<!--\s*guide:.*?-->", body)
    body = strip_comments(body)
    body = re.sub(r"^# .*$", f"# `{heading}`", body, count=1, flags=re.M)
    body = re.sub(r"\n> \[!summary\]-.*?(?=\n## |\n[^>])", "\n", body, count=1, flags=re.S)
    if guides:
        body = re.sub(r"^(# .*)$", lambda m: m.group(1) + "\n" + guides[0], body, count=1, flags=re.M)
    if body_hook:
        body = body_hook(body)
    body = re.sub(r"[ \t]+\n", "\n", body)
    body = re.sub(r"\n{3,}", "\n\n", body).strip("\n")
    return "\n".join(fm_lines) + "\n\n" + body + "\n"


def _render_kv(key, v):
    if isinstance(v, bool):
        return f"{key}: {'true' if v else 'false'}"
    if isinstance(v, (list, tuple)):
        return f"{key}: [" + ", ".join(str(x) for x in v) + "]"
    s = "" if v is None else str(v)
    if key == "title" or re.search(r"[:#\[\]{},&*?|<>=!%@`]", s):
        return f'{key}: "' + s.replace('"', '\\"') + '"'
    return f"{key}: {s}".rstrip()


def _created_line(sources):
    src = ", ".join(sources) if sources else "direct input"
    return f"- 1.0 ({today()}) — created from {src}"


def _replace_changelog(body, sources):
    return re.sub(r"(## Changelog\n)(?:- .*\n?)*", lambda m: m.group(1) + _created_line(sources) + "\n", body, count=1)


# ---------------------------------------------------------------------------- mint

def mint_uc(vault, spec, refresh=True):
    """Create one UC skeleton. ``spec``: title, primary_feature, features[], level, scope,
    sources[], attachments[]. Returns (id, path)."""
    title = (spec.get("title") or "").strip()
    if not title or not spec.get("primary_feature"):
        raise EngineError("mint uc: spec needs title and primary_feature")
    feats = list(dict.fromkeys([spec["primary_feature"]] + list(spec.get("features") or [])))
    with id_lock(vault):
        for p in vault.uc_paths():
            d = vault.load(p)
            if (d.fm_get("title") or "").strip().lower() == title.lower():
                raise EngineError(f"REFUSED: a UC titled '{title}' already exists ({d.name})")
        uid = fmt("UC", highest(vault, "UC") + 1)
        values = {
            "id": uid, "type": "use-case", "title": title, "status": "draft", "version": "1.0",
            "synced": True, "level": spec.get("level", "user-goal"),
            "scope": spec.get("scope") or vault.config("client", ""),
            "primary_feature": spec["primary_feature"], "features": feats, "brs": [], "entities": [],
            "pain_points": list(spec.get("pain_points") or []), "sources": list(spec.get("sources") or []),
            "links": [], "attachments": list(spec.get("attachments") or []), "absorbs": [],
            "owner": spec.get("owner", "team"), "updated": today(),
        }

        def hook(body):
            # § 3 starts empty: the template's A1/E1 examples would otherwise read as real flow ids
            body = re.sub(r"(## 3\. [^\n]*\n)(.*?)(?=\n## 4\.)", r"\1", body, count=1, flags=re.S)
            return _replace_changelog(body, values["sources"])

        text = instantiate(vault, "use-case.md", values, f"{uid} {title}", hook)
        path = os.path.join(vault.uc_dir, f"{uid} {safe_title(title)}.md")
        vault.create(path, text)
        if refresh:
            # pointers inside the lock: a concurrent mint must not interleave its hub write with ours
            from . import hub, mirror
            vault.forget()
            for slug in feats:
                if os.path.exists(vault.hub_path(slug)):
                    hub.refresh(vault, slug)
            mirror.sync_features_column(vault)
    return uid, path


def mint_br(vault, spec, refresh=True):
    """Create one BR. ``spec``: title, feature, uc[], sources[], statement."""
    title = (spec.get("title") or "").strip()
    if not title or not spec.get("feature"):
        raise EngineError("mint br: spec needs title and feature")
    statement = (spec.get("statement") or "").strip() or "`not stated`"
    with id_lock(vault):
        bid = fmt("BR", highest(vault, "BR") + 1)
        values = {
            "id": bid, "type": "business-rule", "title": title, "status": "draft", "version": "1.0",
            "feature": spec["feature"], "uc": list(spec.get("uc") or []), "fr": [],
            "sources": list(spec.get("sources") or []), "links": [], "owner": spec.get("owner", "team"),
            "updated": today(),
        }

        def hook(body):
            # the template's preamble between H1 (and guide pointer) and the first ## is guidance
            body = re.sub(r"^(# [^\n]*\n(?:<!--\s*guide:.*?-->\n)?)(.*?)(?=^## )",
                          lambda m: m.group(1) + "\n" + statement + "\n\n", body, count=1, flags=re.S | re.M)
            return _replace_changelog(body, values["sources"])

        text = instantiate(vault, "br.md", values, f"{bid} {title}", hook)
        path = os.path.join(vault.br_dir, f"{bid} {safe_title(title)}.md")
        vault.create(path, text)
        if refresh and os.path.exists(vault.hub_path(spec["feature"])):
            from . import hub
            from .util import sort_ids
            vault.forget()
            d = vault.load(vault.hub_path(spec["feature"]))
            brs = d.fm_list("br")
            if bid not in brs:
                d.fm_set("br", sort_ids(brs + [bid]))
                vault.write(d)
            hub.refresh(vault, spec["feature"])
    return bid, path


def mint_int(vault, spec):
    """Create one intake note skeleton. ``spec``: title, kind, source, source_ref, blocks[{kind, ref, text}],
    attachments[], declared_features[], extra frontmatter under ``fm``."""
    with id_lock(vault):
        nid = fmt("INT", highest(vault, "INT") + 1)
        blocks = spec.get("blocks") or []
        values = {
            "id": nid, "type": "intake", "kind": spec.get("kind", "requirement"),
            "title": spec.get("title", ""), "status": spec.get("status", "raw"),
            "source": spec.get("source", "direct"), "source_ref": spec.get("source_ref", ""),
            "source_ids": list(spec.get("source_ids") or []),
            "attachments": list(spec.get("attachments") or []),
            "raw_sources": [f'"SRC-{i + 1} · {b.get("kind", "note")} · {b.get("ref", "")}"' for i, b in enumerate(blocks)],
            "participants": [], "declared_features": list(spec.get("declared_features") or []),
            "updated": today(),
        }
        values.update(spec.get("fm") or {})

        def hook(body):
            raw = "\n\n".join(f"### SRC-{i + 1} · {b.get('kind', 'note')} · {b.get('ref', '')}\n\n{b.get('text', '').rstrip()}"
                              for i, b in enumerate(blocks)) or "### SRC-1 · `note` · `ref`"
            return re.sub(r"(## Raw\n)(.*?)(?=\n## )", lambda m: m.group(1) + "\n" + raw + "\n", body, count=1, flags=re.S)

        text = instantiate(vault, "intake.md", values, nid, hook)
        # an intake note has no H1 in the template: drop the heading line instantiate() cannot place
        path = os.path.join(vault.inbox, f"{nid}.md")
        vault.create(path, text)
    return nid, path


def mint_ep(vault, spec):
    """Create one epic folder and its EP file. ``spec``: title (the feature name), feature,
    source_ucs[], snapshot. Returns (id, path). One epic per feature: a second for the same slug is
    refused."""
    title = (spec.get("title") or "").strip()
    if not title or not spec.get("feature"):
        raise EngineError("mint ep: spec needs title and feature")
    with id_lock(vault):
        for p in vault.epic_paths():
            if (vault.load(p).fm_get("feature") or "").strip() == spec["feature"]:
                raise EngineError(f"REFUSED: feature '{spec['feature']}' already has an epic ({os.path.basename(p)})")
        eid = fmt("EP", highest(vault, "EP") + 1)
        values = {
            "id": eid, "type": "epic", "title": title, "status": "draft", "version": 1,
            "feature": spec["feature"], "source_ucs": list(spec.get("source_ucs") or []), "absorbed": [],
            "snapshot": spec.get("snapshot") or "none", "stories": [], "after": [], "updated": today(),
        }
        text = instantiate(vault, "epic.md", values, f"{eid} {title}",
                           lambda body: _replace_changelog(body, values["source_ucs"]))
        name = f"{eid} {safe_title(title)}"
        path = os.path.join(vault.stories_dir, name, f"{name}.md")
        vault.create(path, text)
    return eid, path


def mint_us(vault, spec):
    """Create one story beside its epic and list it on the epic's ``stories:``. ``spec``: title, epic,
    priority, slice_of, rules[], screens[], entities[], after[], snapshot. Returns (id, path)."""
    title = (spec.get("title") or "").strip()
    if not title or not spec.get("epic"):
        raise EngineError("mint us: spec needs title and epic")
    with id_lock(vault):
        ep_path = vault.find(spec["epic"])
        if not ep_path:
            raise EngineError(f"mint us: {spec['epic']}: no such epic")
        ep = vault.load(ep_path)
        folder = os.path.dirname(ep_path)
        for p in vault.story_paths():
            if os.path.dirname(p) == folder and (vault.load(p).fm_get("title") or "").strip().lower() == title.lower():
                raise EngineError(f"REFUSED: {spec['epic']} already has a story titled '{title}' ({os.path.basename(p)})")
        sid = fmt("US", highest(vault, "US") + 1)
        slice_of = spec.get("slice_of") or ""
        values = {
            "id": sid, "type": "user-story", "title": title, "epic": spec["epic"], "status": "draft",
            "version": 1, "priority": spec.get("priority", "P2"), "slice_of": slice_of,
            "rules": list(spec.get("rules") or []), "screens": list(spec.get("screens") or []),
            "entities": list(spec.get("entities") or []), "after": list(spec.get("after") or []),
            "snapshot": spec.get("snapshot") or ep.fm_get("snapshot") or "none", "absorbed": [],
            "updated": today(),
        }
        src = slice_of if isinstance(slice_of, list) else [slice_of] if slice_of else []
        text = instantiate(vault, "user-story.md", values, f"{sid} {title}",
                           lambda body: _replace_changelog(body, src))
        path = os.path.join(folder, f"{sid} {safe_title(title)}.md")
        vault.create(path, text)
        stories = ep.fm_list("stories")
        if sid not in stories:
            ep.fm_set("stories", stories + [sid])
            vault.write(ep)
    return sid, path


def mint_route(vault, route_path):
    """Mint every `new` UC a uc-router Phase A route.json proposes (serially, under the lock) and
    write the key → id map next to it as <route>.minted.json. Idempotent: a key already minted is
    reused (same title refused → looked up)."""
    import json
    route = load_json(route_path)
    out_path = re.sub(r"\.json$", "", route_path) + ".minted.json"
    minted = load_json(out_path) if os.path.exists(out_path) else {}
    for n in route.get("new") or []:
        if n["key"] in minted:
            continue
        spec = {"title": n["title"], "primary_feature": n.get("primary_feature") or route["feature"],
                "features": n.get("features") or [], "level": n.get("level", "user-goal"),
                "sources": n.get("sources") or []}
        try:
            uid, _ = mint_uc(vault, spec)
        except EngineError as e:
            if "already exists" not in str(e):
                raise
            uid = next(vault.load(p).id for p in vault.uc_paths()
                       if (vault.load(p).fm_get("title") or "").strip().lower() == n["title"].strip().lower())
        minted[n["key"]] = uid
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(minted, f, indent=2)
    return [(k, v) for k, v in minted.items()]


def mint_from_spec(vault, kind, spec_path):
    if kind == "route":
        return mint_route(vault, spec_path)
    spec = load_json(spec_path)
    specs = spec if isinstance(spec, list) else [spec]
    fn = {"uc": mint_uc, "br": mint_br, "int": mint_int, "ep": mint_ep, "us": mint_us}[kind]
    return [fn(vault, s) for s in specs]
