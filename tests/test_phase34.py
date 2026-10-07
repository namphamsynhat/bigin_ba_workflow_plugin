"""Phases 3–4 — workflow scripts, cards, lean artifacts, split Signal Log, codebase intake, metrics."""
import glob
import json
import os
import re
import subprocess

from helpers import FIX, ROOT, digest, find, fresh, lint_clean, read, run, write_json

from bigin import model
from bigin.vault import Vault

CONV = os.path.join(ROOT, "workspace", "conventions")
WS = os.path.join(ROOT, "workspace")
CITE = re.compile(r"‹([\w./-]+\.md) § ([^›]+)›")


def _headings(path):
    with open(path, encoding="utf-8") as f:
        text = re.sub(r"```.*?```", "", f.read(), flags=re.S)
    return [re.sub(r"[`*]", "", m.group(1)).strip() for m in re.finditer(r"^#{1,4}\s+(.*)$", text, re.M)]


# ---------------------------------------------------------------------------- Phase 3

def test_workflow_scripts_parse_and_declare_meta():
    for f in glob.glob(os.path.join(ROOT, "workflows", "*.js")):
        src = open(f).read()
        assert src.startswith("export const meta = {"), f
        meta = src.split("}\n", 1)[0]
        assert "name:" in meta and "description:" in meta, f
        assert "Date.now" not in src and "Math.random" not in src, f"{f}: breaks resume"
        code = src.replace("export const meta", "const meta", 1)
        js = ("const AF=Object.getPrototypeOf(async function(){}).constructor;"
              "new AF('args','agent','parallel','pipeline','phase','log','workflow','budget',require('fs').readFileSync(0,'utf8'));")
        try:
            r = subprocess.run(["node", "-e", js], input=code, capture_output=True, text=True, timeout=30)
        except FileNotFoundError:
            return  # no node on this machine: syntax check skipped
        assert r.returncode == 0, f"{f}: {r.stderr[:400]}"
        for phase_title in re.findall(r"phase\('([^']+)'\)|phase: '([^']+)'", src):
            t = phase_title[0] or phase_title[1]
            assert f"title: '{t}'" in meta, f"{f}: phase '{t}' missing from meta.phases"


def test_run_ledger_resume():
    root, v = fresh("comm-vault")
    code, out = run(root, "run", "new", "--stage", "transform", "--scope", "payments")
    rid = out.strip()
    # the Workflow tool only takes a scriptPath inside the working dir — run new stages the scripts there
    for wf in ("transform.js", "extract.js", "adjudicate.js"):
        assert os.path.isfile(os.path.join(root, "_runs", rid, "workflows", wf))
    run(root, "run", "record", rid, "--task", "close:payments", "--status", "ok")
    code, out = run(root, "run", "done", rid)
    assert "close:payments" in out
    code, out = run(root, "run", "summary", rid)
    assert "results: ok 1" in out and len(out.splitlines()) <= 20


def test_agents_tiered_and_small():
    tiers = {"uc-router": {"inherit", "opus"}, "code-adjudicator": {"inherit", "opus"}, "uc-splitter": {"inherit", "opus"},
             "signal-extractor": {"sonnet"}, "signal-filer": {"sonnet"}, "signal-auditor": {"sonnet"}}
    for name, allowed in tiers.items():
        p = os.path.join(ROOT, "agents", f"{name}.md")
        text = open(p).read()
        m = re.search(r"^model:\s*(\S+)", text, re.M)
        assert m and m.group(1) in allowed, f"{name}: model {m and m.group(1)} not in {allowed}"
        assert len(text.encode()) <= 4096, f"{name}.md is {len(text.encode())} bytes (> 4 KB)"
    assert not os.path.exists(os.path.join(ROOT, "agents", "uc-applier.md")), "uc-applier must be deleted"


# ---------------------------------------------------------------------------- Phase 4

def test_cards_small_and_citations_resolve():
    cards = [p for p in glob.glob(os.path.join(ROOT, "cards", "*.md")) if not p.endswith("README.md")]
    assert len(cards) >= 8, cards
    for p in cards:
        text = open(p).read()
        assert len(text.encode()) <= 3072, f"{os.path.basename(p)} is {len(text.encode())} bytes (> 3 KB)"
        for f, head in CITE.findall(text):
            path = os.path.join(CONV, f) if os.path.exists(os.path.join(CONV, f)) else os.path.join(WS, f)
            assert os.path.exists(path), f"{os.path.basename(p)} cites missing file {f}"
            hs = _headings(path)
            want = head.strip().replace("`", "")
            assert any(h == want or h.startswith(want) for h in hs), f"{os.path.basename(p)}: ‹{f} § {head}› no such heading"


def test_card_citations_resolve():
    test_cards_small_and_citations_resolve()


def test_bigin_ba_routing_is_small():
    p = os.path.join(ROOT, "agents", "bigin-ba.md")
    assert len(open(p).read().encode()) <= 6144, "bigin-ba.md routing file must be ≤ 6 KB"


def test_lean_templates_and_new_uc():
    assert len(open(os.path.join(WS, "templates", "use-case.md")).read()) < 3000
    assert os.path.exists(os.path.join(WS, "templates", "use-case.guide.md"))
    root, v = fresh("comm-vault")
    run(root, "mint", "uc", "--spec", write_json(root, "s.json", {"title": "Withdraw an application", "primary_feature": "grant-intake"}))
    t = read(root, find(root, "01-Requirements/_ucs", "UC-005"))
    assert t.count("<!--") == 1 and "guide: _bigin/templates/use-case.guide.md" in t


def test_strip_guidance_shrinks_and_keeps_content():
    root, v = fresh("comm-vault")
    before = {p: open(p).read() for p in v.uc_paths() + v.br_paths() + v.hub_paths()}
    code, out = run(root, "migrate", "strip-guidance")
    res = json.loads(out)
    assert res["bytes_after"] < res["bytes_before"] * 0.7, res
    v2 = Vault(root)
    for p, old in before.items():
        new = open(p).read()
        assert [s.title for s in v2.load(p).sections] == [s.title for s in Vault(root).load(p).sections]
        strip = lambda t: re.sub(r"\s+", " ", re.sub(r"<!--.*?-->", "", t, flags=re.S)).strip()
        assert strip(new) == strip(old), f"{os.path.basename(p)}: visible content changed"
    lint_clean(root)
    code, out = run(root, "migrate", "strip-guidance")
    assert json.loads(out)["files"] == 0


def test_split_signal_log_keeps_every_tool_working():
    root, v = fresh("comm-vault")
    cov_before = run(root, "coverage", "--stage", "file")[1]
    code, out = run(root, "migrate", "split-signal-log")
    assert json.loads(out)["hubs"] == 2
    assert os.path.exists(os.path.join(root, "01-Requirements/_features/payments.signals.md"))
    hub = read(root, "01-Requirements/_features/payments.md")
    assert "| 4 |" not in hub and "payments.signals.md" in hub
    assert run(root, "coverage", "--stage", "file")[1] == cov_before
    code, out = run(root, "--json", "worklist", "route", "payments")
    assert [r["row"] for r in json.loads(out)["rows"]] == ["4"]
    run(root, "hub", "flip", "payments", "4=applied:UC-003 S2")
    assert "| applied | UC-003 S2 |" in read(root, "01-Requirements/_features/payments.signals.md")
    run(root, "hub", "refresh", "--all")
    lint_clean(root)


def test_codebase_intake_zero_llm():
    root, v = fresh("code-vault")
    code, out = run(root, "intake", "codebase", "--cards", os.path.join(root, "cards.json"),
                    "--assignment", os.path.join(root, "assignment.json"), "--unmapped-out", os.path.join(root, "unmapped.json"))
    assert code == 0, out
    assert "12 already imported" in out and "unmapped rows left for the filer: 0" in out, out
    assert not os.path.exists(os.path.join(root, "unmapped.json"))
    code, out = run(root, "coverage", "--stage", "file", "--id-pattern", r"XR-[A-Z]+-\d{3}",
                    "--universe", os.path.join(root, "cards.json"))
    assert code == 0 and "ids: 20" in out, out
    notes = sorted(glob.glob(os.path.join(root, "00-Inbox", "INT-*.md")))
    assert len(notes) >= 2
    new = read(root, os.path.relpath(notes[-1], root))
    assert "source: codebase" in new and "grounding: codebase" in new and "Asymmetry warning" in new
    assert "| problem |" in new or "| question |" in new
    lint_clean(root)
    code, out = run(root, "intake", "codebase", "--cards", os.path.join(root, "cards.json"),
                    "--assignment", os.path.join(root, "assignment.json"))
    assert "20 already imported" in out, out


def test_codebase_intake_unmapped_goes_to_filer():
    root, v = fresh("code-vault")
    cards = [{"id": "XR-MISC-900", "plainEnglish": "Something no feature owns.", "source": "repos/other/Thing.php:1-5"}]
    p = write_json(root, "misc.json", cards)
    code, out = run(root, "intake", "codebase", "--cards", p, "--unmapped-out", os.path.join(root, "unmapped.json"))
    assert "unmapped rows left for the filer: 1" in out, out
    task = json.load(open(os.path.join(root, "unmapped.json")))
    assert task["rows"][0]["id"] == "XR-MISC-900"
    lint_clean(root)


def test_metrics_and_budgets():
    root, v = fresh("comm-vault")
    pj = os.path.join(root, "_bigin/system/project.md")
    s = open(pj).read().replace("workspace_version:", "budgets: {transform_per_feature_tokens: 1000}\nworkspace_version:")
    open(pj, "w").write(s)
    run(root, "metrics", "add", "--run", "r1", "--stage", "transform", "--task", "route payments", "--agent", "uc-router",
        "--feature", "payments", "--usage", "<usage>total_tokens: 1500\ntool_uses: 4\nduration_ms: 900</usage>")
    code, out = run(root, "metrics", "report", "--run", "r1")
    assert "tokens 1,500" in out and "OVER BUDGET: transform feature payments" in out, out


def test_migrate_all_from_1_8_12():
    root, v = fresh("comm-vault")
    code, out = run(root, "migrate", "all", "--from", "1.8.12", "--to", "1.12.0")
    res = json.loads(out)
    assert [s["step"] for s in res["steps"]] == ["discussion-to-ledger", "strip-guidance", "split-signal-log"], res
    assert "workspace_version: 1.12.0" in read(root, "_bigin/system/project.md")
    assert glob.glob(os.path.join(root, "_runs", "migrate-1.12.0-*.tgz"))
    lint_clean(root)
