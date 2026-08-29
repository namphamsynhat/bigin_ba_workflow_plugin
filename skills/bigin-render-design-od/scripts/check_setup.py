#!/usr/bin/env python3
"""check_setup.py — /bigin-render-design-od's preflight. Answers Preconditions 1-5 in one shot.

Everything it reports is read from disk: Open Design's sqlite catalog, its app-config.json, its
bundled design-system directory, and the vault's own _bigin/system/project.md. The only subprocess
is `claude mcp list`, needed because "is the daemon actually up" is not a question disk can answer.
Running this instead of calling list_projects / list_agents / resources/list keeps the whole
precondition phase out of the model's context.

usage:
    check_setup.py                       full report
    check_setup.py --json                same, machine-readable
    check_setup.py --design-systems      print every design-system id and nothing else
    check_setup.py --no-mcp              skip the `claude mcp list` probe (slow on many servers)

exit 0  ready to render
exit 1  a halt condition — the reason is on stderr, and § Precondition says what to do about it
"""
import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import od_common as od  # noqa: E402


def probe_mcp(timeout: int = 60) -> dict:
    """Finds the open-design row in `claude mcp list` and derives its tool prefix.

    The server name is whatever `od mcp install claude` registered on this machine, so the row is
    matched on a case-insensitive SUBSTRING and never on a fixed name. `command -v od` is NOT a
    valid probe: /usr/bin/od is the BSD octal-dump utility and wins on PATH on a stock macOS.
    """
    if not shutil.which("claude"):
        return {"ok": False, "reason": "the `claude` CLI is not on PATH, so the MCP row cannot be read"}
    try:
        proc = subprocess.run(
            ["claude", "mcp", "list"], capture_output=True, text=True, timeout=timeout
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "reason": f"`claude mcp list` did not answer within {timeout}s"}

    for line in proc.stdout.splitlines():
        if od.MCP_SERVER_SUBSTRING not in line.lower() or ":" not in line:
            continue
        name = line.split(":", 1)[0].strip()
        connected = "✔" in line or "Connected" in line
        return {
            "ok": connected,
            "server": name,
            "tool_prefix": f"mcp__{name}__",
            "reason": None if connected else f"the '{name}' row is not Connected — the daemon is down",
        }

    return {"ok": False, "reason": "no MCP server whose name contains 'open-design' is registered"}


def build_report(args) -> dict:
    report = {"ready": True, "halts": []}

    if args.no_mcp:
        report["mcp"] = {"ok": None, "reason": "skipped (--no-mcp)"}
    else:
        report["mcp"] = probe_mcp()
        if report["mcp"]["ok"] is False:
            report["ready"] = False
            report["halts"].append(report["mcp"]["reason"])

    try:
        data_dir = od.find_open_design_data_dir()
    except FileNotFoundError as exc:
        report["ready"] = False
        report["halts"].append(str(exc))
        return report

    report["data_dir"] = str(data_dir)
    vault = od.find_vault_root()
    report["vault_root"] = str(vault)

    report["projects"] = [
        {
            "id": pid,
            "name": name,
            "design_system": ds,
            "updated": datetime.fromtimestamp(updated / 1000, timezone.utc).strftime("%Y-%m-%d %H:%M"),
        }
        for pid, name, ds, updated in od.list_projects(data_dir, limit=args.project_limit)
    ]
    if not report["projects"]:
        report["ready"] = False
        report["halts"].append("no Open Design project exists yet — create one in the app first")

    report["design_systems"] = od.find_design_systems(data_dir)

    cfg = od.read_app_config(data_dir)
    report["agents"] = [
        {"id": aid, "model": (spec or {}).get("model"), "default": aid == cfg.get("agentId")}
        for aid, spec in sorted((cfg.get("agentModels") or {}).items())
    ]
    report["default_design_system"] = cfg.get("designSystemId")

    persisted = od.read_project_settings(vault)
    known_projects = {p["id"] for p in report["projects"]}
    report["persisted"] = {
        k: {
            "value": v,
            "still_valid": (
                v in known_projects if k == "od_project"
                else v in report["design_systems"] if k == "od_design_system"
                else v in {a["id"] for a in report["agents"]} if k == "od_agent"
                else None
            ),
        }
        for k, v in persisted.items()
    }
    return report


def print_human(r: dict) -> None:
    mcp = r.get("mcp", {})
    if mcp.get("ok"):
        print(f"[✓] MCP              {mcp['server']} — connected. Tool prefix: {mcp['tool_prefix']}")
    elif mcp.get("ok") is None:
        print(f"[-] MCP              {mcp.get('reason')}")
    else:
        print(f"[!] MCP              {mcp.get('reason')}")

    if "data_dir" not in r:
        return
    print(f"[✓] Open Design data {r['data_dir']}")
    print(f"[✓] Vault root       {r['vault_root']}")

    print(f"\nPROJECTS ({len(r['projects'])} most recent) — pick one, its id is `od_project`")
    for p in r["projects"]:
        print(f"  {p['updated']}  {p['id']:<38} {p['name']:<24} design system: {p['design_system'] or '—'}")

    ds = r["design_systems"]
    print(f"\nDESIGN SYSTEMS ({len(ds)} installed, app default: {r.get('default_design_system') or '—'})")
    line = "  "
    for name in ds:
        if len(line) + len(name) > 96:
            print(line.rstrip())
            line = "  "
        line += name + "  "
    if line.strip():
        print(line.rstrip())

    print("\nAGENTS — `agent` / `model` for start_run (omit both to use Open Design's own runtime)")
    for a in r["agents"]:
        print(f"  {'*' if a['default'] else ' '} {a['id']:<20} {a['model'] or '—'}")

    if r["persisted"]:
        print("\nPERSISTED in _bigin/system/project.md")
        for k, v in r["persisted"].items():
            mark = {True: "✓ still valid", False: "✗ STALE — re-ask", None: ""}[v["still_valid"]]
            print(f"  {k:<20} {v['value']:<40} {mark}")
    else:
        print("\nPERSISTED in _bigin/system/project.md\n  (nothing yet — ask, then write od_* back)")

    if r["halts"]:
        print("\nHALT:")
        for h in r["halts"]:
            print(f"  - {h}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--design-systems", action="store_true", help="print design-system ids only")
    parser.add_argument("--no-mcp", action="store_true", help="skip the `claude mcp list` probe")
    parser.add_argument("--project-limit", type=int, default=10, help="how many projects to list")
    args = parser.parse_args()

    if args.design_systems:
        print("\n".join(od.find_design_systems(od.find_open_design_data_dir())))
        return

    report = build_report(args)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_human(report)

    if not report["ready"]:
        for h in report["halts"]:
            print(f"[!] {h}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
