"""Mirrors and links — ported from Agoyu ``sync_links.py`` and the § 4 mirror part of ``foldin_mirrors.py``.

``mirror_brs``  every UC § 4 row's Statement ← the BR's current rule statement; the Enforced-at cell
                is validated against the UC's live step/flow ids; UC ``brs:`` = the § 4 ids.
``sync_links``  BR ``uc:`` ⊇ UCs mirroring it · UC ``features:`` ⊇ features of the BRs it mirrors ·
                ``sources:`` ⊇ every INT-### cited outside comments · FEATURES.md UC column.
Every link list is add-only except UC ``brs:``, which is derived from § 4 exactly.
"""
import os
import re

from . import model
from .util import EngineError, sort_ids
from .vault import cell_value, render_row, split_cells

INT_RE = re.compile(r"\bINT-\d+\b")


def _body_ints(doc):
    return set(INT_RE.findall("\n".join(doc.masked[doc.body_start:])))


def _norm(t):
    return re.sub(r"\s+", " ", (t or "").replace("\\|", "|")).strip().rstrip(".").lower()


def still_mirrors(cell, stmt):
    """A § 4 'Statement (short)' still mirrors the BR when it IS the statement, or is its leading
    sentence(s) — the short form. Anything else means the rule changed and the row is stale."""
    c, s = _norm(cell), _norm(stmt)
    # the short form must end where a sentence of the statement ends
    return bool(c) and (c == s or (s.startswith(c) and s[len(c):len(c) + 1] in (".", ";")))


_STOP = set("a an the if then of to and or in on is are be must not for by with at as it its this that "
            "when from any every each system".split())


def resemblance(cell, stmt):
    """Share of the cell's content words that appear in the statement (0..1)."""
    cw = {w for w in re.findall(r"[a-z0-9_]{3,}", _norm(cell)) if w not in _STOP}
    sw = set(re.findall(r"[a-z0-9_]{3,}", _norm(stmt)))
    return len(cw & sw) / len(cw) if cw else 1.0


def check_enforcement(uc_doc, cell):
    """None when the Enforced-at cell is valid, else a reason."""
    if not cell.strip():
        return "Enforced at is blank"
    refs = model.enforcement_refs(cell)
    if not refs:
        return None if model.ENFORCE_WORDS.search(cell) else f"Enforced at '{cell}' names no step, flow, or pre/post-condition"
    live = model.live_refs(uc_doc)
    every = model.all_refs(uc_doc)
    bad = sorted(r for r in refs if r not in every)
    dropped = sorted(r for r in refs if r in every and r not in live)
    if bad:
        return f"Enforced at cites {', '.join(bad)}, which do(es) not exist"
    if dropped:
        return f"Enforced at cites dropped {', '.join(dropped)}"
    return None


def mirror_uc(vault, uc_doc, brs_index=None):
    """Refresh one UC's § 4 statements in memory. Returns (changed_rows, findings)."""
    findings = []
    changed = 0
    for idx, cells in model.s4_rows(uc_doc):
        bid = cells[0]
        bdoc = (brs_index or {}).get(bid)
        if bdoc is None:
            p = vault.find(bid)
            bdoc = vault.load(p) if p else None
        if bdoc is None:
            findings.append(f"{uc_doc.id} § 4: {bid} has no BR file")
            continue
        stmt = model.br_statement(bdoc)
        new = list(cells) + [""] * (3 - len(cells))
        if not stmt or model.is_placeholder_statement(stmt):
            findings.append(f"{uc_doc.id} § 4 {bid}: the BR has no settled rule statement yet — mirror left as is")
        elif not still_mirrors(cell_value(new[1]), stmt):
            if cell_value(new[1]).strip() and resemblance(cell_value(new[1]), stmt) < 0.6:
                # the row reads as a DIFFERENT rule: a wrong id or a rule rewritten wholesale.
                # Overwriting would silently swap one rule for another — a human decides.
                findings.append(f"{uc_doc.id} § 4 {bid}: row text does not resemble {bid}'s statement "
                                f"(wrong id, or the rule was rewritten) — not overwritten")
            else:
                new[1] = stmt
                uc_doc.set_row(idx, new)
                changed += 1
        why = check_enforcement(uc_doc, new[2])
        if why:
            findings.append(f"{uc_doc.id} § 4 {bid}: {why}")
    want = model.s4_brs(uc_doc)
    if uc_doc.fm and "brs" in uc_doc.fm and uc_doc.fm_list("brs") != want:
        uc_doc.fm_set("brs", want)
        changed += 1
    return changed, findings


def mirror_brs(vault, ids=None, dry=False):
    brs = {}
    for p in vault.br_paths():
        d = vault.load(p)
        brs[d.id] = d
    changed, findings = [], []
    for p in vault.uc_paths():
        d = vault.load(p)
        if ids and d.id not in ids:
            continue
        n, f = mirror_uc(vault, d, brs)
        findings += f
        # a BR that says it governs this UC but has no § 4 row is a missing mirror (a judgement:
        # which step enforces it) — report, never guess the enforcement point
        mirrored = set(model.s4_brs(d))
        for bid, b in brs.items():
            if d.id in b.fm_list("uc") and bid not in mirrored and (b.fm_get("status") or "") != "removed":
                findings.append(f"{d.id} § 4: {bid} lists this UC in uc: but has no § 4 row (enforcement point needed)")
        if n:
            changed.append(d.id)
            if not dry:
                vault.write(d)
            else:
                d.verify()
                vault.forget(p)
    return changed, findings


def sync_links(vault, dry=False):
    ucs = {vault.load(p).id: vault.load(p) for p in vault.uc_paths()}
    brs = {vault.load(p).id: vault.load(p) for p in vault.br_paths()}
    mirrored_by = {}
    for uid, d in ucs.items():
        for b in model.s4_brs(d):
            mirrored_by.setdefault(b, set()).add(uid)
    report = {"br": [], "uc": [], "extras": []}
    for bid, d in sorted(brs.items(), key=lambda x: model_key(x[0])):
        cur = d.fm_list("uc")
        want = sort_ids(set(cur) | mirrored_by.get(bid, set()))
        extras = set(cur) - mirrored_by.get(bid, set())
        if extras:
            report["extras"].append(f"{bid} uc: lists {', '.join(sort_ids(extras))} but no § 4 there mirrors it")
        ch = False
        if "uc" in (d.fm or {}) and want != cur:
            ch |= d.fm_set("uc", want)
        src = d.fm_list("sources")
        wsrc = sort_ids(set(src) | _body_ints(d))
        if "sources" in (d.fm or {}) and wsrc != src:
            ch |= d.fm_set("sources", wsrc)
        if ch:
            report["br"].append(bid)
            _flush(vault, d, dry)
    for uid, d in sorted(ucs.items(), key=lambda x: model_key(x[0])):
        ch = False
        want_brs = model.s4_brs(d)
        if "brs" in (d.fm or {}) and d.fm_list("brs") != want_brs:
            ch |= d.fm_set("brs", want_brs)
        feats = d.fm_list("features")
        need = [brs[b].fm_get("feature") for b in want_brs if b in brs and brs[b].fm_get("feature")]
        merged = list(feats)
        pf = d.fm_get("primary_feature")
        if pf and pf not in merged:
            merged.insert(0, pf)
        for f in sorted(set(need)):
            if f not in merged:
                merged.append(f)
        if "features" in (d.fm or {}) and merged != feats:
            ch |= d.fm_set("features", merged)
        src = d.fm_list("sources")
        wsrc = sort_ids(set(src) | _body_ints(d))
        if "sources" in (d.fm or {}) and wsrc != src:
            ch |= d.fm_set("sources", wsrc)
        if ch:
            report["uc"].append(uid)
            _flush(vault, d, dry)
    report["features_md"] = sync_features_column(vault, dry)
    return report


def model_key(i):
    m = re.search(r"\d+", i)
    return int(m.group(0)) if m else 0


def _flush(vault, d, dry):
    if dry:
        d.verify()
        vault.forget(d.path)
    else:
        vault.write(d)


def sync_features_column(vault, dry=False):
    """FEATURES.md: the UC/FR column of each feature row lists its UC ids after any legacy text."""
    if not os.path.exists(vault.features_file):
        return False
    by = {}
    for p in vault.uc_paths():
        d = vault.load(p)
        for s in dict.fromkeys([d.fm_get("primary_feature")] + d.fm_list("features")):
            if s:
                by.setdefault(s, []).append(d.id)
    doc = vault.load(vault.features_file)
    changed = False
    from .vault import find_tables
    for t in find_tables(doc, doc.body_start, len(doc.lines)):
        slug_c = t.col("Slug")
        uc_c = next((k for k, h in enumerate(t.header) if h.strip().upper() in ("UC", "FR", "UC/FR", "UCS", "USE CASES")), None)
        if slug_c is None or uc_c is None:
            continue
        for i in t.row_idxs:
            raw = split_cells(doc.lines[i])
            cells = [cell_value(c) for c in raw]
            if len(cells) <= max(slug_c, uc_c):
                continue
            slug = cells[slug_c]
            if slug not in by:
                continue
            legacy = re.sub(r"\s*·?\s*\bUC-\d+\b", "", cells[uc_c]).strip(" ·")
            ids = " · ".join(sort_ids(by[slug]))
            want = " · ".join(x for x in (legacy, ids) if x)
            if cells[uc_c] != want:
                cells[uc_c] = want
                doc.set_row(i, cells)
                changed = True
    if changed:
        _flush(vault, doc, dry)
    return changed
