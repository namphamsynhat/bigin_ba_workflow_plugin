"""End-to-end fixture tests for workflow scripts (workflows/*.js)."""
import json
import os
import shutil
import subprocess

from helpers import ROOT, find, fresh, read, run


def _has_node():
    try:
        r = subprocess.run(["node", "-v"], capture_output=True, text=True)
        return r.returncode == 0
    except FileNotFoundError:
        return False


def _run_transform_workflow(vault_root, run_id, features, golden_changesets_name="transform-payments.changesets.json"):
    """Run workflows/transform.js via Node with a mock engine runner and mock judge."""
    golden_path = os.path.join(ROOT, "tests", "golden", golden_changesets_name)
    golden_text = json.dumps(open(golden_path, encoding="utf-8").read())

    driver_js = f"""
const fs = require("fs");
const path = require("path");
const {{ execSync }} = require("child_process");

const VAULT = {json.dumps(vault_root)};
const PLUGIN_ROOT = {json.dumps(ROOT)};
const RUN = {json.dumps(run_id)};
const GOLDEN_CHANGESETS = {golden_text};

const args = {{
  run: RUN,
  vault: VAULT,
  plugin_root: PLUGIN_ROOT,
  features: {json.dumps(features)},
  grounding: "communication",
  max_agents: 2,
}};

let logMessages = [];
let engineCalls = 0, judgeCalls = 0;
function log(msg) {{
  logMessages.push(msg);
}}

function phase(title) {{}}

async function pipeline(items, ...steps) {{
  let current = items;
  for (const step of steps) {{
    current = await Promise.all(current.map(async x => step(x)));
  }}
  return current;
}}

async function workflow(descriptor, wfArgs) {{
  return {{ status: "OK", skipped: true }};
}}

async function agent(prompt, options) {{
  // Engine runner: executes commands sequentially
  if (options.schema && options.schema.properties && options.schema.properties.ok) {{
    engineCalls += 1;
    const lines = prompt.split("\\n").filter(l => /^\\d+\\.\\s+/.test(l));
    const pickM = prompt.match(/the stdout of command (\\d+)/);
    const pick = pickM ? Number(pickM[1]) : lines.length;
    let lastStdout = "", n = 0;
    for (const line of lines) {{
      n += 1;
      const cmd = line.replace(/^\\d+\\.\\s*/, "").trim();
      if (!cmd) continue;
      try {{
        const out = execSync(cmd, {{ cwd: VAULT, stdio: ["pipe", "pipe", "pipe"], encoding: "utf8" }});
        if (n === pick) lastStdout = out;
      }} catch (err) {{
        return {{ ok: false, error: ((err.stderr || "") + (err.stdout || "") + err.message).slice(-1500) }};
      }}
    }}
    let data;
    try {{
      data = JSON.parse(lastStdout);
    }} catch (_) {{
      data = {{ text: lastStdout }};
    }}
    return {{ ok: true, data }};
  }}

  // Judge agent: returns canned route or changesets
  if (options.schema && options.schema.properties && options.schema.properties.status) {{
    judgeCalls += 1;
    const outMatch = prompt.match(/Write your result as JSON to `([^`]+)`/);
    const outFile = outMatch ? outMatch[1] : null;
    if (outFile) {{
      const fullOut = path.resolve(VAULT, outFile);
      fs.mkdirSync(path.dirname(fullOut), {{ recursive: true }});
      if (outFile.includes("route.out.json")) {{
        const routeData = {{
          "$schema_version": 1,
          "kind": "route",
          "feature": "payments",
          "routes": [
            {{ "row": "3", "lane": "br", "target": "BR-005" }},
            {{ "row": "4", "lane": "uc", "target": "UC-003" }}
          ]
        }};
        fs.writeFileSync(fullOut, JSON.stringify(routeData, null, 2));
      }} else if (outFile.includes("changesets.out.json")) {{
        fs.writeFileSync(fullOut, GOLDEN_CHANGESETS);
      }}
      return {{ status: "OK", out: outFile, counts: {{}} }};
    }}
  }}

  return {{ ok: false, error: "Unknown agent call: " + prompt.slice(0, 100) }};
}}

(async () => {{
  try {{
    const src = fs.readFileSync(path.resolve(PLUGIN_ROOT, "workflows/transform.js"), "utf8");
    const code = src.replace("export const meta", "const meta", 1);
    const AF = Object.getPrototypeOf(async function(){{}}).constructor;
    const fn = new AF("args", "agent", "parallel", "pipeline", "phase", "log", "workflow", "budget", code);
    const result = await fn(args, agent, null, pipeline, phase, log, workflow, null);
    console.log("WORKFLOW_RESULT:" + JSON.stringify({{ result, logMessages, engineCalls, judgeCalls }}));
  }} catch (err) {{
    console.error("WORKFLOW_ERROR:", err);
    process.exit(1);
  }}
}})();
"""
    res = subprocess.run(["node", "-e", driver_js], capture_output=True, text=True)
    assert res.returncode == 0, f"node failed ({res.returncode}): {res.stderr}\n{res.stdout}"
    assert "WORKFLOW_RESULT:" in res.stdout, f"missing WORKFLOW_RESULT in output: {res.stdout}"
    return json.loads(res.stdout.split("WORKFLOW_RESULT:")[1])


def test_transform_workflow_e2e():
    """End-to-end fixture test for workflows/transform.js with mock runner and judge."""
    if not _has_node():
        return
    vault_root, _ = fresh("comm-vault")
    run_id = "test-e2e-transform"

    payload = _run_transform_workflow(vault_root, run_id, ["payments"])
    res = payload["result"]
    assert res["run"] == run_id
    assert len(res["features"]) == 1
    f0 = res["features"][0]
    assert f0["feature"] == "payments"
    assert f0["stage"] == "done"
    assert f0["error"] is None
    assert f0["applied"] == 4
    assert f0["review"] == ["UC-003"]
    assert "clean" in res["lint"]
    # P2: two judgement calls per feature, and at most two engine runners per feature on top of the
    # per-run ones (done-check, Phase A worklists, impact, coverage, lint) — never one runner per command
    assert payload["judgeCalls"] == 2, payload["judgeCalls"]
    assert payload["engineCalls"] <= 2 * 1 + 5, payload["engineCalls"]
    assert res["coverage"] is not None
    # P3: Phase A routed on index cards; Phase B read full cards only for the UC it routed to
    tasks = os.path.join(vault_root, "_runs", run_id, "tasks")
    a = json.load(open(os.path.join(tasks, "payments.route.in.json"), encoding="utf-8"))
    b = json.load(open(os.path.join(tasks, "payments.draft.in.json"), encoding="utf-8"))
    assert a["phase"] == "a" and all("open_questions" not in c for c in a["candidates"])
    assert b["phase"] == "b" and [c["id"] for c in b["candidates"] if "open_questions" in c] == ["UC-003"]
    # P1: the run has a cost figure although no agent reported usage
    code, out = run(vault_root, "metrics", "report", "--run", run_id)
    assert "estimated ≥" in out and "uc-router" in out, out

    # Verify vault side effects
    uc_path = find(vault_root, "01-Requirements/_ucs", "UC-003")
    uc_content = read(vault_root, uc_path)
    assert "Finance officer checks the applicant confirmed their bank details." in uc_content
    assert "BR-006" in uc_content

    br_path = find(vault_root, "01-Requirements/_brs", "BR-005")
    br_content = read(vault_root, br_path)
    assert "approver's name" in br_content


def test_transform_workflow_resume():
    """Verify that rerunning the workflow on the same run_id skips finished features."""
    if not _has_node():
        return
    vault_root, _ = fresh("comm-vault")
    run_id = "test-resume-transform"

    # Run 1: processes payments
    p1 = _run_transform_workflow(vault_root, run_id, ["payments"])
    assert len(p1["result"]["features"]) == 1
    assert p1["result"]["features"][0]["stage"] == "done"

    # Run 2: skips payments because close:payments is recorded ok
    p2 = _run_transform_workflow(vault_root, run_id, ["payments"])
    assert len(p2["result"]["features"]) == 0
    assert any("skipping 1 finished feature" in m for m in p2["logMessages"])


def _run_workflow(script, vault_root, args, canned):
    """Run workflows/<script> under Node with a real engine (execSync) and canned judge outputs.
    `canned` maps a substring of the judge's output path → the JSON it writes."""
    driver_js = f"""
const fs = require("fs"), path = require("path");
const {{ execSync }} = require("child_process");
const VAULT = {json.dumps(vault_root)}, PLUGIN_ROOT = {json.dumps(ROOT)};
const CANNED = {json.dumps(canned)};
const args = Object.assign({{ vault: VAULT, plugin_root: PLUGIN_ROOT }}, {json.dumps(args)});
let engineCalls = 0, judgeCalls = 0, labels = [];
const log = () => {{}}, phase = () => {{}};
const parallel = thunks => Promise.all(thunks.map(t => t()));
async function pipeline(items, ...steps) {{
  let cur = items;
  for (const step of steps) cur = await Promise.all(cur.map(x => step(x)));
  return cur;
}}
async function agent(prompt, options) {{
  labels.push(options.label);
  if (options.schema.properties.ok) {{
    engineCalls += 1;
    const lines = prompt.split("\\n").filter(l => /^\\d+\\.\\s+/.test(l));
    const pick = Number((prompt.match(/the stdout of command (\\d+)/) || [0, lines.length])[1]);
    let picked = "", n = 0;
    for (const line of lines) {{
      n += 1;
      try {{
        const out = execSync(line.replace(/^\\d+\\.\\s*/, "").trim(), {{ cwd: VAULT, stdio: ["pipe", "pipe", "pipe"], encoding: "utf8" }});
        if (n === pick) picked = out;
      }} catch (err) {{
        return {{ ok: false, error: ((err.stderr || "") + (err.stdout || "") + err.message).slice(-1500) }};
      }}
    }}
    try {{ return {{ ok: true, data: JSON.parse(picked) }}; }} catch (_) {{ return {{ ok: true, data: {{ text: picked }} }}; }}
  }}
  judgeCalls += 1;
  const out = (prompt.match(/Write your (?:JSON result|result as JSON) to `([^`]+)`/) || [])[1];
  const key = Object.keys(CANNED).find(k => out && out.includes(k));
  if (!key) return {{ status: "BLOCKED", reason: "no canned output for " + out }};
  fs.mkdirSync(path.dirname(path.resolve(VAULT, out)), {{ recursive: true }});
  fs.writeFileSync(path.resolve(VAULT, out), JSON.stringify(CANNED[key]));
  return {{ status: "OK", out, counts: {{}} }};
}}
(async () => {{
  const src = fs.readFileSync(path.resolve(PLUGIN_ROOT, "workflows/{script}"), "utf8").replace("export const meta", "const meta");
  const AF = Object.getPrototypeOf(async function(){{}}).constructor;
  const fn = new AF("args", "agent", "parallel", "pipeline", "phase", "log", "workflow", "budget", src);
  const result = await fn(args, agent, parallel, pipeline, phase, log, null, null);
  console.log("WORKFLOW_RESULT:" + JSON.stringify({{ result, engineCalls, judgeCalls, labels }}));
}})().catch(err => {{ console.error("WORKFLOW_ERROR:", err); process.exit(1); }});
"""
    res = subprocess.run(["node", "-e", driver_js], capture_output=True, text=True)
    assert res.returncode == 0 and "WORKFLOW_RESULT:" in res.stdout, f"node failed: {res.stderr}\n{res.stdout}"
    return json.loads(res.stdout.split("WORKFLOW_RESULT:")[1])


def test_extract_workflow_e2e_batches_engine_steps():
    """workflows/extract.js on one e-mail note: three judgement calls, the engine decides the audit depth, and
    the engine runs in a handful of runners — not one per command (P2, P4)."""
    if not _has_node():
        return
    root, _ = fresh("comm-vault")
    p = os.path.join(root, "00-Inbox/INT-003.md")
    s = read(root, "00-Inbox/INT-003.md").replace("declared_features: []", "declared_features: [grant-intake]")
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(s)
    code, out = run(root, "--json", "run", "new", "--stage", "extract", "--scope", "t")
    rid = json.loads(out)["id"]
    src = "Dana Client 2026-09-12"
    canned = {
        "signals.out.json": {"kind": "signals", "int": "INT-003", "rows": [
            {"type": "constraint", "signal": "Appeals must be filed within 14 days of the rejection", "source": src, "quote": "Appeals must be filed within 14 days of the rejection"},
            {"type": "requirement", "signal": "Reviewers see why an appeal was rejected", "why": "applicants phone to ask", "source": src, "quote": "Appeals must be filed within 14 days of the rejection"}],
            "self_audit": {"audit_owed": True, "reason": "the agent's opinion no longer decides"}},
        "filing.out.json": {"kind": "filing", "int": "INT-003",
            "rows": [{"n": 1, "feature": "grant-intake", "status": "new"}, {"n": 2, "feature": "grant-intake", "status": "new"}],
            "hub_rows": [{"hub": "grant-intake", "signal": "**Appeals** — filed within 14 days; reviewers see the rejection reason",
                          "type": "constraint + requirement", "note_rows": [1, 2], "status": "new"}],
            "questions": [], "note_status": "in-review"},
        "analysis.out.json": {"kind": "analysis", "int": "INT-003", "summary": "Appeals get a deadline and a visible reason.",
                              "flow": [], "affected": [], "conflicts": [], "questions": []},
    }
    payload = _run_workflow("extract.js", root, {"run": rid, "notes": ["INT-003"]}, canned)
    res = payload["result"]
    assert res["extracted"] == [{"note": "INT-003", "error": None, "audit": "self", "audited": False, "why_repair": None, "quote_repair": None}], res
    assert res["filed"] == [{"nid": "INT-003", "ok": True, "error": None}], res
    assert res["analysed"][0]["ok"] is True, res
    assert payload["judgeCalls"] == 3, payload["labels"]                 # extractor, filer, analyst — no auditor
    # per run: done-check, extract worklists, first file worklist, analyze worklists, close; per note: 3
    assert payload["engineCalls"] <= 5 + 3, payload["labels"]
    done = run(root, "run", "done", rid)[1].split()
    assert {"extracted:INT-003", "filed:INT-003", "analysed:INT-003"} <= set(done), done
    assert "| grant-intake | new |" in read(root, "00-Inbox/INT-003.md")
    # resume: nothing left to do, and no judge is called again
    again = _run_workflow("extract.js", root, {"run": rid, "notes": ["INT-003"]}, canned)
    assert again["judgeCalls"] == 0, again["labels"]


def test_schema_repair_helper_is_identical_in_extract_and_transform():
    """W7: one repair round on a schema failure, the same code in both workflows (scripts cannot import)."""
    def helper(name):
        with open(os.path.join(ROOT, "workflows", name), encoding="utf-8") as f:
            s = f.read()
        a = s.index("const schemaError =")
        return s[a:s.index("\n}\n", s.index("async function ingestThen")) + 3]
    assert helper("extract.js") == helper("transform.js")
    with open(os.path.join(ROOT, "workflows", "extract.js"), encoding="utf-8") as f:
        src = f.read()
    for who in ("XTR", "AUDITOR", "FILER", "ANALYST"):
        assert f"{who})" in src, who
