# Conventions — the workspace version check

The two `Grep`s every **skill** runs at its precondition, before it does anything else.

**Read by a skill, never by a worker.** A dispatched subagent does not run this check — the skill
that dispatched it already did, and a version mismatch is a stop for the whole run, not something a
worker can act on. It lives in its own file so it is not carried into every subagent that reads
`core.md`.

## Workspace version check (every skill, at its precondition)

`_bigin/conventions/`, `_bigin/stages/`, and `_bigin/templates/` are **copies**. The originals live in the
installed plugin, and `_bigin/system/project.md`'s `workspace_version` records which plugin version last
copied them. Those two can disagree in **both** directions, and only one of them is a warning.

```text
at every skill's existing "missing _bigin/ → stop" precondition, add one Grep each:
    workspace = Grep '^workspace_version:' _bigin/system/project.md
    plugin    = Grep '"version"' ${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json

COMPARE AS SEMVER — component by component, numerically. Never as strings: "1.10.0" sorts BEFORE
"1.6.5" lexically, so a string compare reports an upgrade as a downgrade at exactly the version
where it starts to matter.

workspace == plugin   → proceed silently. The ordinary case.
workspace <  plugin    → WARN and proceed: "workspace is on <a>, plugin is <b> — run
                         /bigin-upgrade-project". The rulebook this run follows is the older one,
                         which is usually harmless for one run and always worth saying.
workspace >  plugin    → STOP. Do not run.
                         Say: the vault's content was built against a NEWER rulebook than the one
                         installed here, so this run would follow superseded rules and, worse, an
                         upgrade run would copy the older rulebook over the newer one and stamp the
                         version backwards. Usual cause: a stale plugin cache being resolved as
                         ${CLAUDE_PLUGIN_ROOT} while the workspace was materialized from a newer
                         install. Name both versions and the cache path, and stop.
workspace_version absent / unparseable → warn, name it, proceed. An old project predates the field.
```

**Why "ahead" is a stop rather than a warning.** Every other version mismatch costs one run following
slightly stale rules. This one is the only case where continuing can *destroy* correct state: the
materialized rulebook gets overwritten with an older one, `workspace_version` is stamped down, and the
next run has no way left to tell that a downgrade happened. There is nothing to reconcile from
afterwards, because the record of what the content was built against is exactly what got overwritten.

`${CLAUDE_PLUGIN_ROOT}` is otherwise not a path any stage reads — see § Reconciliation notes.
