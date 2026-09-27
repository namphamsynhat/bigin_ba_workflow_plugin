"""End-to-end fixture tests for workflow scripts (workflows/*.js)."""
import json
import os
import shutil
import subprocess

from helpers import ROOT, find, fresh, read


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
    const lines = prompt.split("\\n").filter(l => /^\\d+\\.\\s+/.test(l));
    let lastStdout = "";
    for (const line of lines) {{
      const cmd = line.replace(/^\\d+\\.\\s*/, "").trim();
      if (!cmd) continue;
      try {{
        const out = execSync(cmd, {{ cwd: VAULT, stdio: ["pipe", "pipe", "pipe"], encoding: "utf8" }});
        lastStdout = out;
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
    console.log("WORKFLOW_RESULT:" + JSON.stringify({{ result, logMessages }}));
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
