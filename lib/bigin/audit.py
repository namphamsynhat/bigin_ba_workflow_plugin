"""Mechanical audit of a Bigin BA vault.

    bigin audit --baseline <snapshot.tgz | extracted-dir> [--strict]

Read-only. Compares the live vault with a baseline snapshot and verifies vault invariants:
  C1 lint        — linter reports 0 findings
  C2 staged      — every staged entry in Discussion is gated by an open question
  C3 coverage    — traceability coverage has 0 unexplained gaps
  C4 questions   — ADD-ONLY: no question present in baseline vanished
  C5 steps       — no S#/A#/E# step/flow id present in baseline is missing
  C6 structure   — every UC and BR has standard sections and frontmatter
  C7 signal-log  — every baseline Signal Log row exists; text edits flagged as WARN
  C8 status      — status matches open-question count (draft ⇔ 0, needs-clarification ⇔ >0)
  C9 approvals   — no UC/BR is approved by automated passes
  C10 repos      — repos/* have no working-tree changes
  C11 secrets    — no unmasked emails or secret keys in UC, BR, or hub text
  C12 partials   — unticked questions with filled A: are folded or marked not settleable
"""
import collections
import glob
import io
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile

from . import coverage, lint, model
from .vault import Vault, mask_lines


def uncomment(s):
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    return re.sub(r"```.*?```", "", s, flags=re.S)


def section(s, head):
    m = re.search(rf"^{re.escape(head)}[^\n]*\n(.*?)(?=^## |\Z)", uncomment(s), re.M | re.S)
    return m.group(1) if m else ""


def qtexts(s):
    return re.findall(r"^\s*- \[[ xX]\] Q:\s*(.+)", uncomment(s), re.M)


norm = lambda t: re.sub(r"[^a-z0-9]", "", t.lower())


def audit_vault(vault, baseline=None, strict=False, id_pattern=None):
    """Run all audit checks over a Vault; returns (results, passed)."""
    results = []  # (check, level, summary, details)

    def add(check, ok, summary, details=(), warn=False):
        results.append((check, "PASS" if ok else ("WARN" if warn else "FAIL"), summary, list(details)))

    # Files
    ucs = {os.path.basename(p): p for p in vault.uc_paths()}
    brs = {os.path.basename(p): p for p in vault.br_paths()}
    hubs = {os.path.basename(p): p for p in vault.hub_paths() if not p.endswith(".signals.md")}

    # Baseline setup
    bdir = None
    temp_dir = None
    if baseline:
        if os.path.isdir(baseline):
            bdir = baseline
        elif os.path.exists(baseline):
            temp_dir = tempfile.mkdtemp(prefix="audit-baseline-")
            with tarfile.open(baseline) as t:
                members = [m for m in t.getmembers() if m.name.startswith("01-Requirements") and "/._" not in m.name]
                t.extractall(temp_dir, members=members)
            bdir = os.path.join(temp_dir, "01-Requirements") if os.path.isdir(os.path.join(temp_dir, "01-Requirements")) else temp_dir

    try:
        # C1 lint
        old_stdout = sys.stdout
        buf = io.StringIO()
        try:
            sys.stdout = buf
            code = lint.run_full(vault.root)
        finally:
            sys.stdout = old_stdout
        out = buf.getvalue()
        m = re.search(r"(\d+) finding", out)
        n = int(m.group(1)) if m else (0 if "clean" in out else 1)
        add("C1 lint", code == 0 and n == 0, f"real plugin linter: {n} finding(s)",
            [l for l in out.splitlines() if l.strip().startswith("-")][:20])

        # C2 staged
        ungated = []
        open_q_text = "\n".join(q for p in list(ucs.values()) + list(hubs.values())
                                for q in re.findall(r"^\s*- \[ \] Q:\s*(.+)", uncomment(open(p, encoding="utf-8", errors="ignore").read()), re.M))
        for name, p in {**ucs, **brs}.items():
            s = open(p, encoding="utf-8", errors="ignore").read()
            d = section(s, "## Discussion")
            if re.search(r"\(staged 20", d):
                zone = section(s, "## 5") if name.startswith("UC") else section(s, "## Open Questions")
                if re.search(r"^\s*- \[ \] Q:", zone, re.M):
                    continue
                aid = name.split(" ")[0]
                if aid.startswith("BR") and re.search(rf"\b{re.escape(aid)}\b", open_q_text):
                    continue
                ungated.append(aid)
        add("C2 staged", not ungated, f"{len(ungated)} file(s) with staged entries but no open question", ungated)

        # C3 coverage
        pat = id_pattern
        if not pat:
            p_doc = vault.project()
            if p_doc:
                pat = p_doc.fm_get("coverage_id_pattern") or p_doc.fm_get("id_pattern")
        if not pat:
            for np in vault.note_paths():
                try:
                    txt = open(np, encoding="utf-8", errors="ignore").read()
                    if "XR-" in txt:
                        pat = r"XR-[A-Z]+-\d+"
                        break
                except OSError:
                    pass

        c_res = coverage.run(vault, stage="transform", id_pattern=pat)
        if c_res.get("mode") == "id":
            universe = c_res.get("universe", 0)
            filed = c_res.get("filed", 0)
            tr = c_res.get("transformed", 0)
            parked = c_res.get("parked", 0)
            miss = c_res.get("missing", [])
            gap = sorted(x for x in miss if x in c_res.get("missing_filed", miss[:filed]))
            # If missing includes unfiled items:
            unfiled_count = universe - filed
            unexplained = len(miss) - unfiled_count if len(miss) >= unfiled_count else len(gap)
            if unexplained < 0:
                unexplained = 0
            add("C3 coverage", unexplained == 0,
                f"{tr}/{universe} transformed · {parked} parked · {unfiled_count} unfiled (human feature mapping) · {unexplained} UNEXPLAINED gaps",
                miss if unexplained > 0 else [])
        else:
            units = c_res.get("units", 0)
            tr = c_res.get("transformed", 0)
            parked = c_res.get("parked", 0)
            gap = c_res.get("missing", [])
            add("C3 coverage", not gap, f"{tr}/{units} transformed · {parked} parked · {len(gap)} UNEXPLAINED gaps", gap)

        # Baseline checks: C4, C5, C7
        if bdir and os.path.exists(bdir):
            def b_files(sub):
                return {os.path.basename(p): p for p in glob.glob(os.path.join(bdir, sub, "*.md"))}

            b_ucs = b_files("_ucs")
            b_brs = b_files("_brs")
            b_hubs = {k: v for k, v in b_files("_features").items() if not k.endswith(".signals.md")}

            # C4 questions add-only
            lost_hub, lost_art = [], []
            for kind, bset, nset in (("hub", b_hubs, hubs), ("uc", b_ucs, ucs), ("br", b_brs, brs)):
                for name, bp in bset.items():
                    if name not in nset:
                        continue
                    now = norm(open(nset[name], encoding="utf-8", errors="ignore").read())
                    for q in qtexts(open(bp, encoding="utf-8", errors="ignore").read()):
                        if norm(q)[:50] and norm(q)[:50] not in now:
                            (lost_hub if kind == "hub" else lost_art).append(f"{name[:40]}: {q[:90]}")
            add("C4 questions (hubs)", not lost_hub, f"{len(lost_hub)} hub question(s) vanished", lost_hub)
            add("C4 questions (UC/BR)", not lost_art, f"{len(lost_art)} UC/BR question text(s) no longer verbatim (OK only if moved to a Decision log / Changelog)",
                lost_art, warn=True)

            # C5 steps
            def ids(s):
                t = section(s, "## 2") + section(s, "## 3")
                return set(re.findall(r"\*\*(S\d+)\*\*", t)) | set(re.findall(r"^### ([AE]\d+)", t, re.M))

            lost_steps = []
            for n, bp in b_ucs.items():
                if n in ucs:
                    b_ids = ids(open(bp, encoding="utf-8", errors="ignore").read())
                    n_ids = ids(open(ucs[n], encoding="utf-8", errors="ignore").read())
                    diff = b_ids - n_ids
                    if diff:
                        lost_steps.append(f"{n[:7]} {sorted(diff)}")
            add("C5 steps", not lost_steps, f"{len(lost_steps)} UC(s) lost a step/flow id", lost_steps)

            # C7 signal log
            def rows(p):
                out_r = {}
                sig = p[:-3] + ".signals.md"
                txt = open(sig, encoding="utf-8", errors="ignore").read() if os.path.exists(sig) else section(open(p, encoding="utf-8", errors="ignore").read(), "## Signal Log")
                for l in txt.split("\n"):
                    if re.match(r"^\| \d+[a-z]? \|", l):
                        c = [x.strip() for x in l.split("|")[1:-1]]
                        if len(c) >= 4:
                            out_r[c[0]] = (c[1], c[3])
                return out_r

            lost_rows, changed = [], []
            for n, bp in b_hubs.items():
                if n not in hubs:
                    continue
                a, b = rows(bp), rows(hubs[n])
                lost_rows += [f"{n}#{k}" for k in a if k not in b]
                changed += [f"{n}#{k}" for k in a if k in b and a[k] != b[k]]
            add("C7 signal-log rows", not lost_rows, f"{len(lost_rows)} Signal Log row(s) lost", lost_rows)
            add("C7 signal-log text", not changed, f"{len(changed)} row(s) with Signal/Source text rewritten (must carry a Notes line explaining it)",
                changed, warn=True)
        else:
            add("C4 questions (hubs)", True, "no --baseline given: check skipped", warn=True)
            add("C4 questions (UC/BR)", True, "no --baseline given: check skipped", warn=True)
            add("C5 steps", True, "no --baseline given: check skipped", warn=True)
            add("C7 signal-log rows", True, "no --baseline given: check skipped", warn=True)
            add("C7 signal-log text", True, "no --baseline given: check skipped", warn=True)

        # C6 structure
        broken = []
        for n, p in ucs.items():
            s = open(p, encoding="utf-8", errors="ignore").read()
            h = re.findall(r"^(## [^\n]+)$", uncomment(s), re.M)
            c = collections.Counter(x.split(".")[0] if x[3:4].isdigit() else x for x in h)
            need = ["## 1", "## 2", "## 3", "## 4", "## 5", "## 6", "## Discussion", "## Changelog"]
            if not s.startswith("---\n") or any(c[k] != 1 for k in need):
                broken.append(f"{n[:7]} missing/dup: {[k for k in need if c[k] != 1]}")
        for n, p in brs.items():
            s = open(p, encoding="utf-8", errors="ignore").read()
            c = collections.Counter(re.findall(r"^(## [^\n]+)$", uncomment(s), re.M))
            need = ["## Discussion", "## Open Questions", "## Changelog"]
            if not s.startswith("---\n") or any(c[k] != 1 for k in need):
                broken.append(f"{n[:8]} missing/dup: {[k for k in need if c[k] != 1]}")
        add("C6 structure", not broken, f"{len(broken)} structurally broken file(s)", broken)

        # C8 status, C9 approvals
        mism, appr = [], []
        for n, p in {**ucs, **brs}.items():
            s = open(p, encoding="utf-8", errors="ignore").read()
            st = (re.search(r"^status:\s*(\S+)", s, re.M) or [None, "?"])[1]
            if st in ("approved", "enriched", "consolidated"):
                appr.append(n.split(" ")[0])
            zone = (re.search(r"Still open(.*?)(?:Decision log|\Z)", section(s, "## 5"), re.S) or [None, ""])[1] \
                if n.startswith("UC") else section(s, "## Open Questions")
            k = len(re.findall(r"^\s*- \[ \] Q:", zone, re.M))
            if st in ("draft", "needs-clarification") and st != ("needs-clarification" if k else "draft"):
                mism.append(f"{n.split(' ')[0]} {st} open={k}")
        add("C8 status", not mism, f"{len(mism)} status/open-question mismatch(es)", mism)
        add("C9 approvals", not appr, f"{len(appr)} artifact(s) approved by a non-human pass", appr)

        # C10 repos
        repos_dir = os.path.join(vault.root, "repos")
        dirty = []
        if os.path.isdir(repos_dir):
            for r in glob.glob(os.path.join(repos_dir, "*")):
                if os.path.isdir(r) and os.path.exists(os.path.join(r, ".git")):
                    o = subprocess.run(["git", "-C", r, "status", "--porcelain"], capture_output=True, text=True).stdout.strip()
                    if o:
                        dirty.append(f"{os.path.basename(r)}: {len(o.splitlines())} change(s)")
            add("C10 repos", not dirty, "repos/ untouched" if not dirty else "repos/ modified", dirty)
        else:
            add("C10 repos", True, "repos/ not present (skipped)", [])

        # C11 secrets
        EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
        KEY = re.compile(r"AKIA[0-9A-Z]{16}|sk_(?:live|test)_[0-9a-zA-Z]{10,}|-----BEGIN [A-Z ]+KEY")
        hits = []
        for p in list(ucs.values()) + list(brs.values()) + list(hubs.values()):
            s = open(p, encoding="utf-8", errors="ignore").read()
            for mm in EMAIL.finditer(s):
                if not re.search(r"(Controller|Request|Service)@|noreply@", s[max(0, mm.start() - 20):mm.end()]):
                    hits.append(f"{os.path.basename(p)[:40]}: e-mail")
            if KEY.search(s):
                hits.append(f"{os.path.basename(p)[:40]}: key-like string")
        add("C11 secrets", not hits, f"{len(hits)} sensitive value(s) in UC/BR/hub text", sorted(set(hits)))
        # C12 partials
        partials_records = set()
        for pfile in glob.glob(os.path.join(vault.root, "**", "*PARTIALS*.md"), recursive=True):
            try:
                ptext = open(pfile, encoding="utf-8", errors="ignore").read()
                for m in re.finditer(r"`([^`]+:\d+)`.*?\|\s*(folded-before|folded-now|no target)", ptext):
                    partials_records.add(m.group(1))
                    parts = m.group(1).split(":")
                    partials_records.add(f"{os.path.basename(parts[0])}:{parts[1]}")
            except Exception:
                pass

        all_target_paths = sorted(set(list(ucs.values()) + list(brs.values()) + list(hubs.values()) + vault.note_paths()))
        partials = []
        unaddressed = []
        for p in all_target_paths:
            if not os.path.exists(p) or p.endswith(".signals.md"):
                continue
            rel = os.path.relpath(p, vault.root)
            base = os.path.basename(p)
            try:
                with open(p, encoding="utf-8", errors="ignore") as f:
                    raw_lines = f.readlines()
            except Exception:
                continue
            lines = mask_lines(raw_lines)
            for i, line in enumerate(lines):
                if re.match(r"^\s*- \[ \] Q:\s*", line):
                    j = i + 1
                    block = [line]
                    a_val = None
                    checked_first = False
                    while j < len(lines):
                        l = lines[j]
                        if re.match(r"^\s*- \[[ xX]\]", l) or re.match(r"^#{1,6}\s+", l):
                            break
                        block.append(l)
                        if l.strip() and not checked_first:
                            checked_first = True
                            m = re.match(r"^\s*(?:\*\*)?A:(?:\*\*)?\s*(.*)", l)
                            if m and m.group(1).strip():
                                a_val = m.group(1).strip()
                        j += 1
                    if a_val:
                        line_no = i + 1
                        btext = "".join(block)
                        partials.append((rel, line_no, line.strip(), a_val))
                        has_folded = bool(re.search(r"^\s*Folded(?:\s*\(as-built half\))?:\s*\S+", btext, re.M | re.I))
                        has_not_settleable = "not settleable" in btext.lower()
                        in_records = (f"{rel}:{line_no}" in partials_records or
                                      f"{base}:{line_no}" in partials_records)
                        if not (has_folded or has_not_settleable or in_records):
                            unaddressed.append(f"{base}:{line_no} {line.strip()[:40]}")

        add("C12 partials", not unaddressed,
            f"{len(unaddressed)} unticked question(s) with an unfolded partial answer" if unaddressed
            else f"{len(partials)} partial answer(s) verified (folded or not settleable)",
            unaddressed, warn=True)

    finally:
        if temp_dir and os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

    fail = False
    for c, lvl, summ, det in results:
        fail |= lvl == "FAIL" or (strict and lvl == "WARN")
    return results, not fail


def report(results, strict=False):
    lines = []
    for c, lvl, summ, det in results:
        lines.append(f"{lvl:4}  {c:22} {summ}")
    lines.append("")
    for c, lvl, summ, det in results:
        if det and lvl != "PASS":
            lines.append(f"--- {c} ({lvl})")
            for d in det[:40]:
                lines.append(f"    {d}")
            if len(det) > 40:
                lines.append(f"    … {len(det) - 40} more")
    return "\n".join(lines)
