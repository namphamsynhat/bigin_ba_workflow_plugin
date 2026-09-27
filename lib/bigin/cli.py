#!/usr/bin/env python3
"""bigin — the Bigin BA engine's front door. One sub-command per module.

    bigin [--vault ROOT] [--json] <command> …

Run ``bigin <command> -h`` for each command's options. Every write command accepts ``--dry``.
Exit codes: 0 ok · 1 findings/missing (lint, coverage) · 2 refused (bad input, drift) · 64 usage.
"""
import argparse
import json
import os
import sys

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    __package__ = "bigin"

from bigin import __version__  # noqa: E402
from bigin.util import EngineError, dump_json  # noqa: E402
from bigin.vault import Vault  # noqa: E402

COMMANDS = {}


def command(name, help_):
    def deco(fn):
        COMMANDS[name] = (fn, help_)
        return fn
    return deco


def vault_of(args):
    v = Vault(args.vault) if args.vault else Vault.discover()
    v.dry = bool(getattr(args, "dry", False))
    return v


def out(args, obj, text=None):
    if args.json:
        print(json.dumps(obj, indent=2, ensure_ascii=False, default=list))
    elif text is not None:
        if text:
            print(text)
    else:
        print(obj)


# ---------------------------------------------------------------------------- Phase 1

def cmd_lint(args, rest):
    from bigin import lint
    argv = ["bigin-lint"]
    if args.mode == "hook":
        argv += ["--hook"] + (["--quiet"] if args.quiet else [])
    elif args.mode == "full":
        argv += ["--full"] + ([args.vault] if args.vault else [])
    elif args.mode == "self-test":
        argv += ["--self-test"]
    elif args.mode == "fix-citations":
        argv += ["--fix-citations"] + ([args.vault] if args.vault else []) + (["--apply"] if args.apply else [])
    return lint.main(argv)


def cmd_audit(args, rest):
    from bigin import audit
    v = vault_of(args)
    results, passed = audit.audit_vault(v, baseline=args.baseline, strict=args.strict, id_pattern=args.id_pattern)
    rep = audit.report(results, strict=args.strict)
    out(args, results, rep)
    return 0 if passed else 1


def cmd_hub(args, rest):
    from bigin import hub
    v = vault_of(args)
    if args.action == "refresh":
        slugs = None if (args.all or not args.targets) else args.targets
        res = hub.refresh_many(v, slugs, dry=args.dry)
        changed = {k: c for k, c in res.items() if c}
        out(args, res, "\n".join(f"{k}: {', '.join(c)}" for k, c in changed.items())
            + f"\nhub refresh: {len(changed)} of {len(res)} hub(s) changed{' (dry)' if args.dry else ''}")
    elif args.action == "flip":
        if len(args.targets) < 2:
            raise EngineError("usage: bigin hub flip <slug> <row>=<status>[:<dest>][@<note>] …")
        lines = hub.flip(v, args.targets[0], args.targets[1:], dry=args.dry)
        out(args, lines, "\n".join(lines))
    elif args.action == "sweep":
        res = hub.sweep(v, args.targets or None, dry=args.dry)
        out(args, res, "\n".join(f"{k}: {len(r)} -> applied ({' '.join('#' + x for x in r)})" for k, r in res.items())
            + f"\ntotal {sum(len(r) for r in res.values())}{' (dry)' if args.dry else ''}")
    elif args.action == "citers":
        res = hub.citers(v, args.targets[0], args.targets[1:])
        out(args, res, "\n".join(f"#{k}: {' '.join(x) or '-'}" for k, x in res.items()))
    elif args.action == "fix-tables":
        res = hub.fix_split_tables(v, args.targets or None, dry=args.dry)
        out(args, res, "\n".join(f"{k}: {n} split(s) removed" for k, n in res.items()) or "no split tables")
    return 0


def cmd_mirror(args, rest):
    from bigin import mirror
    v = vault_of(args)
    ids = None if (args.all or not args.ids) else set(args.ids)
    changed, findings = mirror.mirror_brs(v, ids, dry=args.dry)
    out(args, {"changed": changed, "findings": findings},
        "\n".join(findings[:40] + ([f"… +{len(findings) - 40} more"] if len(findings) > 40 else []))
        + f"\nmirror br: {len(changed)} UC(s) refreshed, {len(findings)} finding(s){' (dry)' if args.dry else ''}")
    return 0


def cmd_links(args, rest):
    from bigin import mirror
    v = vault_of(args)
    res = mirror.sync_links(v, dry=args.dry)
    out(args, res, f"links sync: {len(res['br'])} BR(s), {len(res['uc'])} UC(s) updated; "
                   f"FEATURES.md {'updated' if res['features_md'] else 'unchanged'}; "
                   f"{len(res['extras'])} BR uc: extra(s) reported{' (dry)' if args.dry else ''}"
        + ("\n" + "\n".join(res["extras"][:20]) if res["extras"] and args.verbose else ""))
    return 0


def cmd_status(args, rest):
    from bigin import status
    v = vault_of(args)
    ch = status.recount(v, set(args.ids) if args.ids else None, dry=args.dry)
    out(args, ch, "\n".join(f"{a}: {b} -> {c}" for a, b, c in ch) + f"\n{len(ch)} status change(s){' (dry)' if args.dry else ''}")
    return 0


def cmd_coverage(args, rest):
    from bigin import coverage
    v = vault_of(args)
    pattern = args.id_pattern or v.config("coverage_id_pattern")
    res = coverage.run(v, args.stage, pattern, args.universe, set(args.notes.split(",")) if args.notes else None)
    out(args, res, coverage.report(res, args.list))
    return 1 if res["missing"] else 0


def cmd_mint(args, rest):
    from bigin import ids
    v = vault_of(args)
    res = ids.mint_from_spec(v, args.kind, args.spec)
    if args.kind == "route":
        out(args, dict(res), "\n".join(f"{k} = {i}" for k, i in res) or "nothing to mint")
    else:
        out(args, [{"id": i, "path": v.rel(p)} for i, p in res], "\n".join(f"{i} {v.rel(p)}" for i, p in res))
    return 0


# ---------------------------------------------------------------------------- Phase 2+

def cmd_context(args, rest):
    from bigin import worklist
    v = vault_of(args)
    res = worklist.context(v, args.id, args.sections.split(",") if args.sections else None)
    out(args, res, worklist.render_context(res))
    return 0


def cmd_worklist(args, rest):
    from bigin import worklist
    v = vault_of(args)
    res = worklist.build(v, args.stage, args.scope, args)
    if args.out:
        dump_json(res, args.out)
        print(f"worklist {args.stage} {args.scope}: {worklist.summary(res)} → {args.out}")
    else:
        print(dump_json(res), end="")
    return 0


def legacy_guard(v, what):
    """project.md `engine: legacy` keeps a half-migrated vault on v1.8 behaviour (## Discussion staging)
    for one minor version: change-set writers refuse; read-only and derived-table commands still run."""
    if (v.config("engine") or "").strip() == "legacy":
        raise EngineError(f"{what} refused: project.md says `engine: legacy` (v1.8 Discussion staging). "
                          "Finish the run the v1.8 way, then `bigin migrate all` and set `engine: engine`.")


def cmd_apply(args, rest):
    from bigin import changeset
    v = vault_of(args)
    legacy_guard(v, "bigin apply")
    res = changeset.apply_paths(v, args.paths, run=args.run, dry=args.dry)
    out(args, res, changeset.render_result(res))
    return 2 if res.get("rejected") else 0


def cmd_ingest(args, rest):
    from bigin import runs
    v = vault_of(args)
    res = runs.ingest(v, args.path, kind=args.kind, run=args.run)
    out(args, res, runs.render_ingest(res))
    return 0 if res["ok"] else 2


def cmd_ledger(args, rest):
    from bigin import ledger
    v = vault_of(args)
    if args.action == "list":
        res = ledger.entries(v, state=None if args.all else "open")
        out(args, res, ledger.render_list(res))
    elif args.action == "render":
        res = ledger.render_blocks(v, dry=args.dry)
        out(args, res, f"ledger render: {len(res)} artifact(s) updated")
    elif args.action == "release":
        legacy_guard(v, "bigin ledger release")
        res = ledger.release(v, verdicts=args.verdicts, dry=args.dry, run=args.run)
        out(args, res, ledger.render_release(res))
    elif args.action == "supersede":
        res = ledger.supersede(v, args.ids, args.reason or "superseded by the answer", dry=args.dry)
        out(args, res, f"superseded {len(res)} change set(s)")
    return 0


def cmd_note(args, rest):
    from bigin import notes
    v = vault_of(args)
    if args.action == "write-signals":
        res = notes.write_signals(v, args.path, dry=args.dry)
    elif args.action == "audit-apply":
        res = notes.apply_audit(v, args.path, dry=args.dry)
    else:
        raise EngineError(f"unknown note action {args.action}")
    out(args, res, notes.render(res))
    return 0


def cmd_file(args, rest):
    from bigin import notes
    v = vault_of(args)
    res = notes.file_apply(v, args.path, dry=args.dry)
    out(args, res, notes.render(res))
    return 0


def cmd_intake(args, rest):
    v = vault_of(args)
    if args.mode == "codebase":
        from bigin.intake import codebase
        res = codebase.intake(v, args.cards, assignment=args.assignment, group_by=args.group_by,
                              title=args.title, dry=args.dry, unmapped_out=args.unmapped_out)
        out(args, res, codebase.render(res))
    else:
        from bigin.intake import communication
        res = communication.scaffold(v, args.spec, dry=args.dry)
        out(args, res, f"{res['id']} {res['path']}")
    return 0


def cmd_migrate(args, rest):
    from bigin import migrate
    v = vault_of(args)
    res = migrate.run(v, args.step, args, dry=args.dry)
    out(args, res, migrate.render(res))
    return 0


def cmd_run(args, rest):
    from bigin import runs
    v = vault_of(args)
    if args.action == "new":
        res = runs.new_run(v, args.stage, args.scope)
        out(args, res, res["id"])
    elif args.action == "summary":
        out(args, runs.summary(v, args.id), runs.render_summary(runs.summary(v, args.id)))
    elif args.action == "done":
        out(args, runs.done_tasks(v, args.id), "\n".join(sorted(runs.done_tasks(v, args.id))))
    elif args.action == "record":
        res = runs.record(v, args.id, args.task, args.status, args.note)
        out(args, res, f"{args.id} {args.task}: {args.status}")
    return 0


def cmd_metrics(args, rest):
    from bigin import metrics
    v = vault_of(args)
    if args.action == "add":
        res = metrics.add(v, args.run, args.stage, args.task, args.agent, args.tokens, args.feature, args.tool_uses,
                          args.duration_ms, args.usage)
        out(args, res, f"metrics: +{res['tokens']} tokens ({args.stage}/{args.task})")
    else:
        res = metrics.report(v, args.run)
        out(args, res, metrics.render(res))
    return 0


def cmd_launcher(args, rest):
    """Write _bigin/bin/bigin (+ copy cards to _bigin/cards) so agents that cannot resolve
    ${CLAUDE_PLUGIN_ROOT} still reach the engine and their cards. Re-run on every upgrade."""
    import shutil
    from bigin.vault import PLUGIN_ROOT
    v = vault_of(args)
    d = os.path.join(v.root, "_bigin", "bin")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "bigin")
    with open(p, "w") as f:
        f.write("#!/bin/sh\n# generated by `bigin launcher` — points at the installed plugin; regenerated on upgrade\n"
                f'exec python3 "{os.path.join(PLUGIN_ROOT, "lib", "bigin", "cli.py")}" "$@"\n')
    os.chmod(p, 0o755)
    cards = os.path.join(v.root, "_bigin", "cards")
    if os.path.isdir(cards):
        shutil.rmtree(cards)
    shutil.copytree(os.path.join(PLUGIN_ROOT, "cards"), cards)
    out(args, {"launcher": v.rel(p), "cards": v.rel(cards)}, f"{v.rel(p)} → {PLUGIN_ROOT}\n{v.rel(cards)} refreshed")
    return 0


# ---------------------------------------------------------------------------- parser

def build_parser():
    p = argparse.ArgumentParser(prog="bigin", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--vault", help="vault root (default: discovered upward from cwd, or $BIGIN_VAULT)")
    p.add_argument("--json", action="store_true", help="machine-readable output")
    p.add_argument("--version", action="version", version=f"bigin {__version__}")
    sub = p.add_subparsers(dest="cmd")

    s = sub.add_parser("lint", help="vault invariant checks (was hooks/bigin-lint.py)")
    g = s.add_mutually_exclusive_group()
    g.add_argument("--hook", dest="mode", action="store_const", const="hook")
    g.add_argument("--full", dest="mode", action="store_const", const="full")
    g.add_argument("--self-test", dest="mode", action="store_const", const="self-test")
    g.add_argument("--fix-citations", dest="mode", action="store_const", const="fix-citations")
    s.add_argument("--quiet", action="store_true")
    s.add_argument("--apply", action="store_true")
    s.set_defaults(fn=cmd_lint, mode="full")

    s = sub.add_parser("audit", help="mechanical audit comparing vault to baseline")
    s.add_argument("--baseline", help="baseline snapshot (.tgz or directory)")
    s.add_argument("--strict", action="store_true", help="fail on WARN")
    s.add_argument("--id-pattern", help="pattern for ID-based coverage (e.g. XR-[A-Z]+-\\d+)")
    s.set_defaults(fn=cmd_audit)

    s = sub.add_parser("hub", help="refresh derived hub tables; flip/sweep Signal Log rows")
    s.add_argument("action", choices=["refresh", "flip", "sweep", "citers", "fix-tables"])
    s.add_argument("targets", nargs="*")
    s.add_argument("--all", action="store_true")
    s.add_argument("--dry", action="store_true")
    s.set_defaults(fn=cmd_hub)

    s = sub.add_parser("mirror", help="refresh UC § 4 rule mirrors from BR statements")
    s.add_argument("what", choices=["br"])
    s.add_argument("ids", nargs="*")
    s.add_argument("--all", action="store_true")
    s.add_argument("--dry", action="store_true")
    s.set_defaults(fn=cmd_mirror)

    s = sub.add_parser("links", help="sync brs:/uc:/features:/sources: and FEATURES.md UC column")
    s.add_argument("what", choices=["sync"])
    s.add_argument("--dry", action="store_true")
    s.add_argument("--verbose", "-v", action="store_true")
    s.set_defaults(fn=cmd_links)

    s = sub.add_parser("status", help="re-derive UC/BR status from the live open-question count")
    s.add_argument("ids", nargs="*")
    s.add_argument("--dry", action="store_true")
    s.set_defaults(fn=cmd_status)

    s = sub.add_parser("coverage", help="traceability coverage across extract/file/transform")
    s.add_argument("--stage", choices=["extract", "file", "transform"])
    s.add_argument("--id-pattern", help=r"trace ids instead of note rows, e.g. 'XR-[A-Z]+-\d+'")
    s.add_argument("--universe", help="JSON/text file listing every id that must survive")
    s.add_argument("--notes", help="comma-separated INT ids to restrict to")
    s.add_argument("--list", action="store_true")
    s.set_defaults(fn=cmd_coverage)

    s = sub.add_parser("mint", help="mint UC/BR/INT ids from a JSON spec (file-locked)")
    s.add_argument("kind", choices=["uc", "br", "int", "route"])
    s.add_argument("--spec", required=True)
    s.add_argument("--dry", action="store_true")
    s.set_defaults(fn=cmd_mint)

    s = sub.add_parser("context", help="compact slice of one artifact for an agent")
    s.add_argument("id")
    s.add_argument("--sections")
    s.set_defaults(fn=cmd_context)

    s = sub.add_parser("worklist", help="build a compact JSON task input for an agent")
    s.add_argument("stage", choices=["route", "adjudicate", "extract", "audit", "file", "release", "split"])
    s.add_argument("scope", help="feature slug, INT id, or UC id")
    s.add_argument("--out")
    s.add_argument("--rows", help="restrict to these Signal Log rows (comma-separated)")
    s.add_argument("--uc", help="UC ids to include as candidates (comma-separated)")
    s.set_defaults(fn=cmd_worklist)

    s = sub.add_parser("apply", help="validate and apply change sets (the only writer of UC/BR/hub content)")
    s.add_argument("paths", nargs="+")
    s.add_argument("--run")
    s.add_argument("--dry", action="store_true")
    s.set_defaults(fn=cmd_apply)

    s = sub.add_parser("ingest", help="schema-validate an agent's .out.json and store it under _runs/")
    s.add_argument("path")
    s.add_argument("--kind", help="schema name (default: from the file's $schema_kind or its name)")
    s.add_argument("--run")
    s.set_defaults(fn=cmd_ingest)

    s = sub.add_parser("ledger", help="change sets gated on a question")
    s.add_argument("action", choices=["list", "render", "release", "supersede"])
    s.add_argument("ids", nargs="*")
    s.add_argument("--all", action="store_true")
    s.add_argument("--verdicts", help="JSON file of {cs id: apply|supersede|revise} from a judging agent")
    s.add_argument("--reason")
    s.add_argument("--run")
    s.add_argument("--dry", action="store_true")
    s.set_defaults(fn=cmd_ledger)

    s = sub.add_parser("note", help="write an intake note's ## Extracted signals from agent JSON")
    s.add_argument("action", choices=["write-signals", "audit-apply"])
    s.add_argument("path")
    s.add_argument("--dry", action="store_true")
    s.set_defaults(fn=cmd_note)

    s = sub.add_parser("file", help="apply a signal-filer's filing.json (hub rows, registers, note columns)")
    s.add_argument("what", choices=["apply"])
    s.add_argument("path")
    s.add_argument("--dry", action="store_true")
    s.set_defaults(fn=cmd_file)

    s = sub.add_parser("intake", help="scaffold an intake note (communication) or import rule cards (codebase)")
    s.add_argument("mode", choices=["codebase", "communication"])
    s.add_argument("--cards", help="rule cards: _rules-store.json shape, a JSON list, or CSV")
    s.add_argument("--assignment", help="JSON map card id → {slug, …}")
    s.add_argument("--group-by", default="capability", choices=["capability", "feature", "group", "none"])
    s.add_argument("--title")
    s.add_argument("--spec", help="communication: JSON spec for the note")
    s.add_argument("--unmapped-out", help="write the unmapped remainder as a filer task input")
    s.add_argument("--dry", action="store_true")
    s.set_defaults(fn=cmd_intake)

    s = sub.add_parser("migrate", help="vault migrations between plugin versions")
    s.add_argument("step", choices=["discussion-to-ledger", "strip-guidance", "split-signal-log", "all", "snapshot", "plan"])
    s.add_argument("--from", dest="from_v")
    s.add_argument("--to", dest="to_v")
    s.add_argument("--dry", action="store_true")
    s.set_defaults(fn=cmd_migrate)

    s = sub.add_parser("run", help="run ledger: new, summary, done, record")
    s.add_argument("action", choices=["new", "summary", "done", "record"])
    s.add_argument("id", nargs="?")
    s.add_argument("--stage")
    s.add_argument("--scope")
    s.add_argument("--task")
    s.add_argument("--status")
    s.add_argument("--note")
    s.set_defaults(fn=cmd_run)

    s = sub.add_parser("launcher", help="write _bigin/bin/bigin and copy cards to _bigin/cards (for subagents)")
    s.set_defaults(fn=cmd_launcher)

    s = sub.add_parser("metrics", help="token/agent accounting per stage")
    s.add_argument("action", choices=["add", "report"])
    s.add_argument("--run")
    s.add_argument("--stage")
    s.add_argument("--task")
    s.add_argument("--agent")
    s.add_argument("--feature")
    s.add_argument("--tokens", type=int, default=0)
    s.add_argument("--tool-uses", type=int, default=0)
    s.add_argument("--duration-ms", type=int, default=0)
    s.add_argument("--usage", help="raw <usage> block text from a task notification")
    s.set_defaults(fn=cmd_metrics)
    return p


def main(argv=None):
    parser = build_parser()
    args, rest = parser.parse_known_args(argv)
    if not getattr(args, "fn", None):
        parser.print_help()
        return 64
    try:
        return args.fn(args, rest) or 0
    except EngineError as e:
        print(f"bigin: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
