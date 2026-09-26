"""Feature-hub bookkeeping — replaces the hub-bookkeeper agent and its script backstops.

Ported from Agoyu ``hub_refresh.py``, ``sync_uc_pointers.py``, ``mirror_br_questions.py``,
``fix_readiness.py``, ``dedupe_hub_questions.py`` (exact duplicates only), ``flip_rows.py``,
``sweep_applied.py``, ``row_citers.py``, ``fix_split_tables.py``.

``refresh`` regenerates only derived content: ``uc:`` pointers, ## Use Cases, ## Requirement
Readiness, the ADD-ONLY ## Open Questions / Gates mirror, one Changelog line and ``updated:``.
## Signal Log and ## Coverage Gaps are never edited by refresh — Doc.verify() refuses the write
if either changed.
"""
import os
import re

from . import model
from .edit import append_changelog, q_core, question_block, same_question, touch_updated
from .util import EngineError, num_key, sort_ids, today
from .vault import cell_value, find_tables, questions_in, render_row, split_cells

UC_HEADER = ["UC", "Goal", "Role", "Status"]
READY_HEADER = ["Artifact", "Status", "Ready for next step?", "Blocking"]
EMPTY_READY = "| — no UC/BR yet — | — | No | Human decision: brainstorm now / draft the use case directly / hold |"


class Index:
    """One pass over every UC and BR, shared by every hub a command touches."""

    def __init__(self, vault):
        self.vault = vault
        self.ucs = {}
        self.brs = {}
        for p in vault.uc_paths():
            d = vault.load(p)
            if d.id:
                self.ucs[d.id] = d
        for p in vault.br_paths():
            d = vault.load(p)
            if d.id:
                self.brs[d.id] = d
        try:
            from . import ledger
            self.pending = ledger.open_counts(vault)
        except Exception:  # ledger absent in a v1.9 vault
            self.pending = {}

    def participating(self, slug):
        out = []
        for uid in sorted(self.ucs, key=num_key):
            d = self.ucs[uid]
            if d.fm_get("primary_feature") == slug:
                out.append((uid, "owns"))
            elif slug in d.fm_list("features"):
                out.append((uid, "participates"))
        return out

    def blocking(self, aid):
        """Reasons an artifact is not ready. Ready ⟺ no reasons (status ≠ needs-clarification,
        0 open questions, nothing pending in the ledger or ## Discussion, § 2 drafted)."""
        d = self.ucs.get(aid) or self.brs.get(aid)
        if d is None:
            return None, ["file missing"]
        status = d.fm_get("status") or "draft"
        reasons = []
        nq = len(model.open_questions(d))
        if nq:
            reasons.append(f"{nq} open question{'s' if nq > 1 else ''}")
        elif status == "needs-clarification":
            reasons.append("status is needs-clarification with no open question (run `bigin status`)")
        if status == "removed":
            reasons.append("removed")
        if aid.startswith("UC") and model.is_placeholder(d):
            reasons.append("not yet drafted (§ 2 is still the template placeholder)")
        if model.has_staged(d):
            reasons.append("staged content awaiting fold-in")
        if self.pending.get(aid):
            n = self.pending[aid]
            reasons.append(f"{n} pending change set{'s' if n > 1 else ''} gated on a question")
        return status, reasons


def _table_or_none(doc, key):
    s = doc.section(key)
    if not s:
        return None
    ts = find_tables(doc, s.start, s.end)
    return ts[0] if ts else None


def _set_table(doc, key, header, rows, empty_row=None):
    """Replace the data rows of the first table in ``key`` (creating the table if absent)."""
    lines = [render_row(r) for r in rows] or ([empty_row] if empty_row else [])
    t = _table_or_none(doc, key)
    if t is None:
        s = doc.section(key)
        if s is None:
            doc.insert_section(key, [""] + [render_row(header), "|" + "|".join(["---"] * len(header)) + "|"] + lines + [""],
                               before="Changelog")
            return True
        pos = s.end
        while pos > s.start and not doc.lines[pos - 1].strip():
            pos -= 1
        return doc.splice(pos, pos, ["", render_row(header), "|" + "|".join(["---"] * len(header)) + "|"] + lines)
    cur = [doc.lines[i] for i in t.row_idxs]
    if [cell_value(c) for x in cur for c in split_cells(x)] == [cell_value(c) for x in lines for c in split_cells(x)]:
        return False
    return doc.replace_table_rows(t, lines)


def _mirror_sources(ix, slug, part):
    """(artifact id, question) pairs whose open/ticked questions belong on this hub."""
    hub_brs = [b for b in ix.vault.load(ix.vault.hub_path(slug)).fm_list("br") if b in ix.brs]
    for uid, _role in part:
        for q in model.uc_questions(ix.ucs[uid]):
            yield uid, q
    for bid in sort_ids(hub_brs):
        for q in model.br_questions(ix.brs[bid]):
            yield bid, q


def _gates(doc, ix, slug, part):
    """ADD-ONLY mirror into ## Open Questions / Gates. Returns list of change descriptions."""
    s = doc.section("Open Questions / Gates")
    if s is None:
        doc.insert_section("Open Questions / Gates", [""], before="Changelog")
        s = doc.section("Open Questions / Gates")
    changes = []
    existing = questions_in(doc, s.start, s.end)
    to_add = []
    for aid, q in _mirror_sources(ix, slug, part):
        match = next((e for e in existing if same_question(e.text, q.text)), None)
        if match is None:
            if q.checked:
                continue
            if any(same_question(t, q.text) for t, _ in to_add):
                continue
            ref = None if "(ref:" in q.text else aid
            to_add.append((q.text, ref))
        elif q.checked and q.answered and not match.checked:
            # tick the hub copy only when its source copy is ticked with an A:
            block = question_block(match.text, answer=q.answer, indent=" " * match.indent, checked=True)
            doc.splice(match.start, match.end, block)
            changes.append(f"ticked mirror of {aid}")
            s = doc.section("Open Questions / Gates")
            existing = questions_in(doc, s.start, s.end)
    # coverage gaps: open/answered rows mirror in the same sentence
    gap_t = _table_or_none(doc, "Coverage Gaps")
    if gap_t is not None:
        gi, si = gap_t.col("Gap"), gap_t.col("Status")
        body = "\n".join(doc.lines[s.start:s.end])
        flat = q_core(body)
        for row in gap_t.rows():
            if gi is None or si is None or len(row) <= max(gi, si):
                continue
            if row[si].strip().lower() not in ("open", "answered"):
                continue
            if re.search(rf"\b(Coverage )?[Gg]ap #{re.escape(row[0])}\b", body) or q_core(row[gi])[:60] in flat:
                continue  # already mirrored, in whatever shape an earlier run used
            to_add.append((f"Coverage gap #{row[0]}: {row[gi]}", None))
    if to_add:
        s = doc.section("Open Questions / Gates")
        pos = s.end
        while pos > s.start and not doc.masked[pos - 1].strip():
            pos -= 1
        block = []
        for text, ref in to_add:
            if text.startswith("Coverage gap #"):
                block += [f"- [ ] {text}"]
            else:
                block += question_block(text, ref=ref)
        doc.splice(pos, pos, block)
        changes.append(f"mirrored {len(to_add)} open question(s)")
    return changes


def dedupe_exact(doc):
    """Remove later EXACT duplicate unchecked, unanswered questions from ## Open Questions / Gates."""
    s = doc.section("Open Questions / Gates")
    if not s:
        return 0
    seen = set()
    drop = []
    for q in questions_in(doc, s.start, s.end):
        key = q_core(q.text)
        if not q.checked and not q.answered and key in seen:
            drop.append(q)
        seen.add(key)
    for q in reversed(drop):
        doc.splice(q.start, q.end, [])
    return len(drop)


def refresh(vault, slug, ix=None, dry=False):
    """Regenerate one hub's derived tables. Returns a list of what changed (empty = no-op)."""
    hp = vault.hub_path(slug)
    if not os.path.exists(hp):
        raise EngineError(f"no hub for '{slug}'")
    ix = ix or Index(vault)
    doc = vault.load(hp)
    part = ix.participating(slug)
    changes = []

    # uc: pointers (sync_uc_pointers) — every UC that owns or participates, numeric order
    want_uc = [u for u, _ in part]
    if doc.fm and doc.fm_list("uc") != want_uc and ("uc" in doc.fm):
        doc.fm_set("uc", want_uc)
        changes.append("uc: pointers")

    # ## Use Cases
    rows = [[u, model.title_of(ix.ucs[u]), role, ix.ucs[u].fm_get("status") or "draft"] for u, role in part]
    if doc.has("Use Cases") and _set_table(doc, "Use Cases", UC_HEADER, rows):
        changes.append("Use Cases table")

    # ## Requirement Readiness — one row per artifact, never ranges
    arts = [u for u, _ in part] + sort_ids(b for b in doc.fm_list("br") if b in ix.brs)
    rrows = []
    for aid in arts:
        status, reasons = ix.blocking(aid)
        rrows.append([aid, status or "—", "No" if reasons else "Yes", "; ".join(reasons)])
    if doc.has("Requirement Readiness") and _set_table(doc, "Requirement Readiness", READY_HEADER, rrows, EMPTY_READY):
        changes.append("Requirement Readiness")

    # ## Open Questions / Gates — add-only
    changes += _gates(doc, ix, slug, part)
    n = dedupe_exact(doc)
    if n:
        changes.append(f"removed {n} exact duplicate question line(s)")

    if changes:
        touch_updated(doc)
        append_changelog(doc, f"- {today()} — bigin hub refresh: {', '.join(changes)} "
                              f"({len(part)} UC(s), {len([a for a in arts if a.startswith('BR')])} BR(s))")
        if not dry:
            vault.write(doc)
        else:
            doc.verify()
            vault.forget(hp)
    return changes


def refresh_many(vault, slugs=None, dry=False):
    ix = Index(vault)
    out = {}
    for slug in (slugs or vault.slugs()):
        out[slug] = refresh(vault, slug, ix, dry=dry)
    return out


# ---------------------------------------------------------------------------- Signal Log edits

def _parse_flip(spec):
    """'<row>=<status>[:<destination>][@<note>]'"""
    if "=" not in spec:
        raise EngineError(f"bad flip spec '{spec}' — want <row>=<status>[:<dest>][@<note>]")
    n, rest = spec.split("=", 1)
    note = None
    if "@" in rest:
        rest, note = rest.split("@", 1)
    st, _, dest = rest.partition(":")
    st = st.strip()
    if st not in model.SIGNAL_STATUSES:
        raise EngineError(f"'{st}' is not a Signal Log status ({', '.join(sorted(model.SIGNAL_STATUSES))})")
    return n.strip(), st, dest.strip() or None, note


def set_row(doc, row, status=None, dest=None, note=None, add_dest=False):
    """Edit one Signal Log row's Status / Destination / Notes in place. Returns (before, after) status."""
    cells = list(row.cells)
    hdr = row.header

    def col(name):
        for k, h in enumerate(hdr):
            if h.lower() == name.lower():
                while len(cells) <= k:
                    cells.append("")
                return k
        raise EngineError(f"Signal Log has no '{name}' column")

    before = row.status
    if status:
        cells[col("Status")] = status
    if dest:
        k = col("Destination")
        if add_dest and cells[k].strip() and cells[k].strip() not in ("—", "-"):
            have = [x.strip() for x in cells[k].split("·")]
            for d in [x.strip() for x in dest.split("·")]:
                if d and d not in have:
                    have.append(d)
            cells[k] = " · ".join(have)
        else:
            cells[k] = dest
    if note:
        k = col("Notes")
        if note not in cells[k]:
            cells[k] = "; ".join(x for x in (cells[k].strip(), note) if x)
    doc.set_row(row.idx, cells)
    return before, status or before


def flip(vault, slug, specs, dry=False):
    doc = model.signal_doc(vault, slug)
    if doc is None:
        raise EngineError(f"no hub for '{slug}'")
    rows = {r.num: r for r in model.signal_rows(doc)}
    out = []
    parsed = [_parse_flip(s) for s in specs]
    missing = [n for n, *_ in parsed if n not in rows]
    if missing:
        raise EngineError(f"{slug}: Signal Log row(s) not found: {', '.join(missing)}")
    for n, st, dest, note in parsed:
        row = {r.num: r for r in model.signal_rows(doc)}[n]
        b, a = set_row(doc, row, st, dest, note)
        out.append(f"{slug} #{n}: {b} -> {a}")
    if not dry:
        vault.write(doc)
    return out


def discussion_citers(vault):
    """{(slug, row): {artifact ids}} for every hub row a UC/BR ## Discussion still cites."""
    out = {}
    for p in vault.uc_paths() + vault.br_paths():
        d = vault.load(p)
        txt = model.discussion_text(d)
        if not txt.strip():
            continue
        for key in model.hub_row_cites(txt):
            out.setdefault(key, set()).add(d.id)
    return out


def ledger_citers(vault):
    out = {}
    try:
        from . import ledger
    except ImportError:
        return out
    for e in ledger.entries(vault, state="open"):
        cs = e["changeset"]
        tr = cs.get("trace") or {}
        for r in tr.get("hub_rows") or []:
            out.setdefault((tr.get("hub"), str(r)), set()).add(cs["target"]["id"])
    return out


def citers(vault, slug, rows):
    d = discussion_citers(vault)
    lg = ledger_citers(vault)
    return {str(n): sorted(d.get((slug, str(n)), set()) | lg.get((slug, str(n)), set())) for n in rows}


def sweep(vault, slugs=None, dry=False):
    """staged → applied when nothing still pending cites the row (no ## Discussion entry, no open
    ledger change set) and its Destination names at least one existing UC/BR. Nothing else flips."""
    ids = vault.ids("UC") | vault.ids("BR")
    cited = discussion_citers(vault)
    for k, v in ledger_citers(vault).items():
        cited.setdefault(k, set()).update(v)
    report = {}
    for slug in (slugs or vault.slugs()):
        doc = model.signal_doc(vault, slug)
        if doc is None:
            continue
        flips = []
        for row in model.signal_rows(doc):
            if row.status != "staged":
                continue
            if cited.get((slug, row.num)):
                continue
            if not (set(re.findall(r"\b(?:UC|BR)-\d+\b", row.destination)) & ids):
                continue
            set_row(doc, row, "applied")
            flips.append(row.num)
        if flips:
            report[slug] = flips
            if not dry:
                vault.write(doc)
            else:
                vault.forget(doc.path)
    return report


def fix_split_tables(vault, slugs=None, dry=False):
    """Remove blank lines that split a Signal Log table in two (fix_split_tables.py)."""
    out = {}
    for slug in (slugs or vault.slugs()):
        doc = model.signal_doc(vault, slug)
        t = model.signal_table(doc)
        if not t:
            continue
        idxs = t.row_idxs
        blanks = [i for a, b in zip(idxs, idxs[1:]) for i in range(a + 1, b)]
        if not blanks:
            continue
        for i in reversed(blanks):
            doc.splice(i, i + 1, [])
        out[slug] = len(blanks)
        if not dry:
            vault.write(doc)
        else:
            vault.forget(doc.path)
    return out
