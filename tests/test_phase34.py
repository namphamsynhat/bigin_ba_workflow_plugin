"""Phases 3–4 — workflow scripts, cards, lean artifacts, split Signal Log, codebase intake, metrics."""
import glob
import json
import os
import re
import shutil
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
        with open(f, encoding="utf-8") as fh:
            src = fh.read()
        assert src.startswith("export const meta = {"), f
        meta = src.split("}\n", 1)[0]
        assert "name:" in meta and "description:" in meta, f
        assert "Date.now" not in src and "Math.random" not in src, f"{f}: breaks resume"
        code = src.replace("export const meta", "const meta", 1)
        js = ("const AF=Object.getPrototypeOf(async function(){}).constructor;"
              "new AF('args','agent','parallel','pipeline','phase','log','workflow','budget',require('fs').readFileSync(0,'utf8'));")
        try:
            r = subprocess.run(["node", "-e", js], input=code, capture_output=True, text=True,
                               encoding="utf-8", timeout=30)
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
    tiers = {"uc-router": {"sonnet"}, "code-adjudicator": {"sonnet"}, "uc-splitter": {"sonnet"},
             "signal-extractor": {"sonnet"}, "signal-filer": {"sonnet"}, "signal-auditor": {"sonnet"}}
    for name, allowed in tiers.items():
        p = os.path.join(ROOT, "agents", f"{name}.md")
        with open(p, encoding="utf-8") as fh:
            text = fh.read()
        m = re.search(r"^model:\s*(\S+)", text, re.M)
        assert m and m.group(1) in allowed, f"{name}: model {m and m.group(1)} not in {allowed}"
        assert len(text.encode()) <= 4096, f"{name}.md is {len(text.encode())} bytes (> 4 KB)"
    assert not os.path.exists(os.path.join(ROOT, "agents", "uc-applier.md")), "uc-applier must be deleted"


# ---------------------------------------------------------------------------- Phase 4

def test_cards_small_and_citations_resolve():
    cards = [p for p in glob.glob(os.path.join(ROOT, "cards", "*.md")) if not p.endswith("README.md")]
    assert len(cards) >= 8, cards
    for p in cards:
        with open(p, encoding="utf-8") as fh:
            text = fh.read()
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
    with open(p, encoding="utf-8") as fh:
        assert len(fh.read().encode()) <= 6144, "bigin-ba.md routing file must be ≤ 6 KB"


def test_lean_templates_and_new_uc():
    with open(os.path.join(WS, "templates", "use-case.md"), encoding="utf-8") as fh:
        assert len(fh.read()) < 3000
    assert os.path.exists(os.path.join(WS, "templates", "use-case.guide.md"))
    root, v = fresh("comm-vault")
    run(root, "mint", "uc", "--spec", write_json(root, "s.json", {"title": "Withdraw an application", "primary_feature": "grant-intake"}))
    t = read(root, find(root, "01-Requirements/_ucs", "UC-005"))
    assert t.count("<!--") == 1 and "guide: _bigin/templates/use-case.guide.md" in t


def test_strip_guidance_shrinks_and_keeps_content():
    root, v = fresh("comm-vault")
    before = {p: open(p, encoding="utf-8").read() for p in v.uc_paths() + v.br_paths() + v.hub_paths()}
    code, out = run(root, "migrate", "strip-guidance")
    res = json.loads(out)
    assert res["bytes_after"] < res["bytes_before"] * 0.7, res
    v2 = Vault(root)
    for p, old in before.items():
        new = open(p, encoding="utf-8").read()
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
    with open(os.path.join(root, "unmapped.json"), encoding="utf-8") as fh:
        task = json.load(fh)
    assert task["rows"][0]["id"] == "XR-MISC-900"
    lint_clean(root)


def test_metrics_and_budgets():
    root, v = fresh("comm-vault")
    pj = os.path.join(root, "_bigin/system/project.md")
    with open(pj, encoding="utf-8") as f:
        s = f.read().replace("workspace_version:", "budgets: {transform_per_feature_tokens: 1000}\nworkspace_version:")
    with open(pj, "w", encoding="utf-8", newline="\n") as f:
        f.write(s)
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


def test_ingest_records_an_estimate_without_any_agent_reporting_usage():
    """P1: a run always has a cost figure — `ingest` writes it from the task files themselves."""
    root, v = fresh("comm-vault")
    code, out = run(root, "--json", "run", "new", "--stage", "transform", "--scope", "payments")
    rid = json.loads(out)["id"]
    tasks = os.path.join(root, "_runs", rid, "tasks")
    run(root, "worklist", "route", "payments", "--out", os.path.join(tasks, "payments.route.in.json"))
    out_path = os.path.join(tasks, "payments.changesets.out.json")
    shutil.copy(os.path.join(ROOT, "tests", "golden", "transform-payments.changesets.json"), out_path)
    code, out = run(root, "ingest", out_path, "--kind", "changesets", "--run", rid)
    assert code == 0, out
    rows = [json.loads(l) for l in open(os.path.join(root, "_runs", rid, "metrics.jsonl"), encoding="utf-8")]
    assert len(rows) == 1 and rows[0]["est"] and rows[0]["agent"] == "uc-router" and rows[0]["feature"] == "payments"
    b = rows[0]["bytes"]
    assert b["card"] > 0 and b["in"] > 0 and b["out"] > 0 and rows[0]["tokens"] == sum(b.values()) // 4
    code, out = run(root, "metrics", "report", "--run", rid)
    assert "tokens 0 across 0" in out and "estimated ≥" in out, out      # never mixed into the measured total
    code, out = run(root, "run", "summary", rid)
    assert "estimated" in out, out


def test_route_worklist_is_split_by_phase():
    """P3: Phase A routes on index cards; Phase B gets full cards only for the UCs it routed to."""
    root, v = fresh("comm-vault")
    full = json.loads(run(root, "--json", "worklist", "route", "payments")[1])
    a = json.loads(run(root, "--json", "worklist", "route", "payments", "--phase", "a")[1])
    assert [c["id"] for c in a["candidates"]] == [c["id"] for c in full["candidates"]] and a["rows"] == full["rows"]
    for c in a["candidates"]:
        assert "open_questions" not in c and all("sha" not in s for s in c["steps"]), c
    target = full["candidates"][0]["id"]
    os.makedirs(os.path.join(root, "_runs"), exist_ok=True)
    spec = write_json(root, "_runs/route.out.json", {"kind": "route", "feature": "payments", "routes": [{"row": "4", "lane": "uc", "target": target}]})
    b = json.loads(run(root, "--json", "worklist", "route", "payments", "--phase", "b", "--spec", spec)[1])
    by_id = {c["id"]: c for c in b["candidates"]}
    assert by_id[target] == full["candidates"][0]                        # the routed UC: the full card, shas intact
    assert all("open_questions" not in c for i, c in by_id.items() if i != target)
    code, out = run(root, "worklist", "route", "payments", "--phase", "b")
    assert code != 0 and "--spec" in out, out


def test_filer_worklist_ranks_questions_elsewhere_and_reports_the_cut():
    from bigin import worklist
    qs = [{"int": f"INT-{i:03d}", "question": f"filler question number {i} about nothing"} for i in range(40)]
    qs[37] = {"int": "INT-900", "question": "Which bank details must the applicant confirm before payment?"}
    kept, omitted = worklist._relevant_questions(qs, [{"signal": "Applicant confirms bank details before payment"}])
    assert omitted == 10 and len(kept) == 30 and qs[37] in kept
    assert worklist._relevant_questions(qs[:30], [])[1] == 0


def _signals(root, nid, rows, self_audit=None, mode=None):
    d = {"kind": "signals", "int": nid, "rows": rows, "self_audit": self_audit or {}}
    if mode:
        d["mode"] = mode
    return write_json(root, f"{nid}.signals.out.json", d)


def test_engine_decides_audit_owed_not_the_extractor():
    """P4: the audit verdict comes from the note's structure and the self-audit's counts; the extractor's own
    `audit_owed` boolean is ignored either way."""
    root, v = fresh("comm-vault")
    ask = lambda t, why: {"type": "requirement", "signal": t, "why": why, "source": "Dana Client 2026-09-12",
                       "quote": "Appeals must be filed within 14 days of the rejection"}
    # a short single e-mail block, every reason stated → self-audit stands, even when the agent claims otherwise
    p = _signals(root, "INT-003", [ask("The report must list every grant", "auditors ask for it")],
                 {"audit_owed": True, "reason": "felt unsure"})
    res = json.loads(run(root, "--json", "note", "write-signals", p)[1])
    assert res["audit_owed"] is False and res["audit_reasons"] == [] and "why_repair" not in res, res
    # an inversion in the self-audit owes the audit even when the agent says it does not
    p = _signals(root, "INT-003", [ask("The report must be exportable", "finance re-keys it today")],
                 {"audit_owed": False, "inversions": 1}, mode="append")
    res = json.loads(run(root, "--json", "note", "write-signals", p)[1])
    assert res["audit_owed"] is True and "inversion" in res["audit_reasons"][0], res
    # `not stated` over 30% is a Why repair on those rows, not a second read of the whole source
    p = _signals(root, "INT-003", [ask("The export must include totals", "not stated"),
                                   ask("The export must include dates", "not stated")], mode="append")
    res = json.loads(run(root, "--json", "note", "write-signals", p)[1])
    assert res["audit_owed"] is False and res["not_stated_rate"] == 1.0 and len(res["why_repair"]) == 2, res


def test_write_signals_records_resume_state_in_the_run():
    root, v = fresh("comm-vault")
    rid = json.loads(run(root, "--json", "run", "new", "--stage", "extract", "--scope", "t")[1])["id"]
    doc = read(root, "00-Inbox/INT-003.md").replace("· email ·", "· transcript ·")
    with open(os.path.join(root, "00-Inbox/INT-003.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(doc)
    p = _signals(root, "INT-003", [{"type": "decision", "signal": "The legacy report is a spreadsheet", "source": "[00:01]",
                       "quote": "Appeals must be filed within 14 days of the rejection"}])
    res = json.loads(run(root, "--json", "note", "write-signals", p, "--run", rid)[1])
    assert res["audit_owed"] is True and res["audit_reasons"] == ["transcript block"], res
    done = run(root, "run", "done", rid)[1].split()
    assert "extracted:INT-003" in done and "audit-owed:INT-003" in done, done


def test_qualify_decides_lookup_gates_and_hands_back_only_what_needs_a_reader():
    """P5: Stage 2's lookups run in the engine; the orchestrator opens a note only for a `check` row."""
    from bigin.qualify import rows_named
    assert rows_named("Rationale is not stated for the following rows: 7, 10 and 14. Why?") == {7, 10, 14}
    assert rows_named("Rows 6, 25 (turn-time, scope) and 28-30 (NDA) fit several features") == {6, 25, 28, 29, 30}
    assert rows_named("target of 1 minute versus 15-20 minutes (row 34)") == {34}
    assert rows_named("Should partial payments be allowed within 10 days?") == set()

    root, v = fresh("comm-vault")
    res = json.loads(run(root, "--json", "qualify", "payments")[1])
    assert res["pass"] == ["4"] and res["held"] == [] and res["rows_arg"] == "4", res

    # an open question on the source note that names the cited row holds it (gate 1) …
    note = os.path.join(root, "00-Inbox/INT-002.md")
    s = read(root, "00-Inbox/INT-002.md")
    assert "## Open Questions" in s
    s = s.replace("## Open Questions\n", "## Open Questions\n\n- [ ] Q: For row 6, who confirms the bank details? (owner: client)\n  A:\n", 1)
    with open(note, "w", encoding="utf-8", newline="\n") as f:
        f.write(s)
    res = json.loads(run(root, "--json", "qualify", "payments", "--apply")[1])
    assert res["pass"] == [] and res["held"][0]["row"] == "4" and res["held"][0]["gate"] == 1, res
    assert res["flipped"] == ["4"]
    hub = read(root, "01-Requirements/_features/payments.md")
    assert "awaiting INT-002 — For row 6, who confirms" in hub and "| held |" in hub, hub
    # … a question naming a different row does not, and one naming no row goes to a reader
    s2 = read(root, "00-Inbox/INT-002.md").replace("For row 6, who", "Generally, who")
    with open(note, "w", encoding="utf-8", newline="\n") as f:
        f.write(s2)
    res = json.loads(run(root, "--json", "qualify", "payments")[1])
    assert res["held"] == [] and res["check"][0]["row"] == "4" and "names no row" in res["check"][0]["why"][0], res
    # a cite that does not resolve is held, never re-pointed (gate 3)
    hub_p = os.path.join(root, "01-Requirements/_features/payments.md")
    hub_text = read(root, "01-Requirements/_features/payments.md").replace("INT-002 #6", "INT-002 #99")
    with open(hub_p, "w", encoding="utf-8", newline="\n") as f:
        f.write(hub_text)
    res = json.loads(run(root, "--json", "qualify", "payments")[1])
    assert res["held"][0]["gate"] == 3 and "does not resolve" in res["held"][0]["note"], res


def test_readiness_names_a_drafted_uc_whose_goal_was_never_written():
    """A drafted UC with no open question reads as ready — unless § 1 never says why, and nobody is asking."""
    root, v = fresh("comm-vault")
    rel = find(root, "01-Requirements/_ucs", "UC-003")
    s = read(root, rel).replace("* **Business Need / Goal:** Pay approved grants on time",
                                "* **Business Need / Goal:** `<the value delivered or problem solved, in the client's own words>`")
    with open(os.path.join(root, rel), "w", encoding="utf-8", newline="\n") as f:
        f.write(s)
    run(root, "hub", "refresh", "payments")
    hub = read(root, "01-Requirements/_features/payments.md")
    row = next(l for l in hub.splitlines() if l.startswith("| UC-003 |") and ("| Yes |" in l or "| No |" in l))
    assert "| No |" in row and "Business Need / Goal not filled" in row, row


def test_coverage_worklist_is_the_whole_input_and_answers_the_lookup_lenses():
    """P5: Stage 4b reads one compact JSON; a BR no use case enforces is found by lookup, not by reading."""
    root, v = fresh("comm-vault")
    w = json.loads(run(root, "--json", "worklist", "coverage", "payments")[1])
    assert w["stage"] == "coverage" and {c["id"] for c in w["use_cases"]} >= {"UC-003"}
    assert all("sha" not in s for c in w["use_cases"] for s in c["steps"])
    assert [f["br"] for f in w["mechanical"]["rule"]] == ["BR-006"], w["mechanical"]
    assert w["has_gaps_section"] is True and w["existing_gaps"] == []
    code, out = run(root, "worklist", "coverage", "no-such-feature")
    assert code != 0


def test_mint_ux_reserves_numbers_and_never_hands_one_out_twice():
    """P8: the design stage's UX ids come from the engine, not from a grep that fails open."""
    root, v = fresh("comm-vault")
    os.makedirs(os.path.join(root, "04-UIUX"), exist_ok=True)
    with open(os.path.join(root, "04-UIUX", "UX-007 Payments.md"), "w", encoding="utf-8") as f:
        f.write("---\nid: UX-007\n---\n")
    first = json.loads(run(root, "--json", "mint", "ux", "--count", "2")[1])
    assert first == ["UX-008", "UX-009"], first
    # the files for 008/009 were never written — the numbers are still not reused
    assert json.loads(run(root, "--json", "mint", "ux")[1]) == ["UX-010"]
    code, out = run(root, "mint", "uc")
    assert code != 0 and "--spec" in out, out


def test_stories_worklist_hands_the_worker_only_approved_ucs_with_their_rules():
    root, v = fresh("comm-vault")
    p = os.path.join(root, "01-Requirements/_ucs", [f for f in os.listdir(os.path.join(root, "01-Requirements/_ucs")) if f.startswith("UC-002")][0])
    s = read(root, os.path.relpath(p, root)).replace("status: draft", "status: approved", 1)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(s)
    code, out = run(root, "worklist", "stories", "grant-intake")
    w = json.loads(out)
    assert code == 0 and [u["id"] for u in w["use_cases"]] == ["UC-002"], w
    assert all("sha" not in s_ for s_ in w["use_cases"][0]["steps"]) and w["use_cases"][0]["version"]
    assert {b["id"] for b in w["brs"]} == set(w["use_cases"][0]["brs"]) and all(b["statement"] for b in w["brs"]), w
    assert "do not open" in w["read"]
