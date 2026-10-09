"""Suspect-link flags: which UX specs, epics and stories were built on a use case that has since changed.

Every UX / EP / US records what it was built from in ``absorbed: [UC-###@<version>]`` (runtime.md §
Absorbed). When the UC moves on — a Jira ticket's change applied, an answer folded in — that record
no longer matches, and the artifact is *suspect* until design or stories re-processes it. This module
derives that, mechanically, into a ``stale:`` frontmatter list:

    stale: [UC-003@1.4]      # UC-003 is at 1.4; this artifact absorbed an older version

* a UC counts only when the artifact absorbed it before (a UC it never absorbed is NEW work for its
  stage, not a stale link);
* for an epic or story, a UC that is no longer ``approved`` is stale too (a story is only ever built
  from approved content, so its source being re-opened is exactly what the dev team needs to see);
* the artifact's own ``status`` is never changed — an approved story stays approved and flagged
  (runtime.md: "reported, never rewritten"); the flag clears itself when the stage re-stamps
  ``absorbed``.

Idempotent: a second run with nothing changed writes nothing. Run at the end of ``bigin apply`` /
``bigin ledger release``, and alone as ``bigin cascade``.
"""
import os
import re

from .edit import append_changelog
from .stories import parse_slices
from .util import today

ABS = re.compile(r"^(UC-\d+)@(.+)$")


def _uc_state(vault):
    out = {}
    for p in vault.uc_paths():
        d = vault.load(p)
        if d.id:
            out[d.id] = {"version": str(d.fm_get("version") or "").strip(), "status": (d.fm_get("status") or "").strip(),
                         "trigger": _trigger(d)}
    return out


def _trigger(doc):
    """The INT the UC's newest Changelog line cites — what made it move."""
    s = doc.section("Changelog")
    if not s:
        return None
    for line in reversed(doc.lines[s.start:s.end]):
        m = re.findall(r"\bINT-\d+", line)
        if m:
            return m[-1]
        if line.strip().startswith("- "):
            return None
    return None


def _cited(doc, kind):
    if kind == "UX":
        return set(doc.fm_list("uc"))
    if kind == "EP":
        return set(doc.fm_list("source_ucs"))
    ucs = set()
    for item in parse_slices(doc.fm_list("slice_of") or doc.fm_get("slice_of") or ""):
        m = re.match(r"^(UC-\d+)", item.strip())
        if m:
            ucs.add(m.group(1))
    return ucs


def trace_of(vault, slice_of):
    """A story's handoff trace from what it slices: (sources: the INT-### its UCs cite, jira: their ticket
    keys). Mechanical — the dev team links branches / commits / PRs to the Jira key."""
    ucs = set()
    for item in parse_slices(slice_of or ""):
        m = re.match(r"^(UC-\d+)", item.strip())
        if m:
            ucs.add(m.group(1))
    ints, keys = set(), set()
    for uc in ucs:
        p = vault.find(uc)
        if not p:
            continue
        for s in vault.load(p).fm_list("sources"):
            if re.match(r"^INT-\d+$", str(s).strip()):
                ints.add(str(s).strip())
    for nid in ints:
        p = vault.find(nid)
        if p:
            k = (vault.load(p).fm_get("jira_key") or "").strip()
            if k:
                keys.add(k)
    from .util import sort_ids
    return sort_ids(ints), sorted(keys)


def derive(doc, kind, ucs):
    """The stale list this artifact SHOULD carry, sorted."""
    absorbed = {}
    for a in doc.fm_list("absorbed"):
        m = ABS.match(str(a).strip())
        if m:
            absorbed[m.group(1)] = m.group(2).strip()
    out = []
    for uc in sorted(_cited(doc, kind) | set(absorbed)):
        st = ucs.get(uc)
        if not st:
            continue
        drifted = uc in absorbed and absorbed[uc] != st["version"]
        reopened = kind in ("EP", "US") and uc in absorbed and st["status"] != "approved"
        if drifted or reopened:
            out.append(f"{uc}@{st['version']}")
    return out


def artifacts(vault):
    return [("UX", p) for p in vault.ux_paths()] + [("EP", p) for p in vault.epic_paths()] + \
        [("US", p) for p in vault.story_paths()]


def run(vault, dry=False):
    """Refresh every UX / EP / US ``stale:``. Returns [{id, path, stale, was}] for each that changed."""
    ucs = _uc_state(vault)
    changed = []
    for kind, p in artifacts(vault):
        d = vault.load(p)
        if not d.fm:
            continue
        trace_changed = kind == "US" and _refresh_trace(vault, d)
        want = derive(d, kind, ucs)
        have = [str(x).strip() for x in d.fm_list("stale")]
        if want == have or (not want and "stale" not in d.fm):
            if trace_changed:
                changed.append({"id": d.id, "path": vault.rel(p), "stale": want, "was": have, "trace": True})
                if dry:
                    d.verify()
                    vault.forget(p)
                else:
                    vault.write(d)
            continue
        d.fm_set("stale", want, after="absorbed")
        new = [x for x in want if x not in have]
        if new and d.section("Changelog"):
            why = []
            for x in new:
                uc = x.split("@")[0]
                trig = ucs[uc]["trigger"]
                why.append(f"{x}" + (f" (from {trig})" if trig else "") +
                           ("" if ucs[uc]["status"] == "approved" else f", now {ucs[uc]['status']}"))
            append_changelog(d, f"- {today()} — stale: built on an older {', '.join(why)} — re-run "
                                f"{'/bigin-generate-design' if kind == 'UX' else '/bigin-generate-stories'}")
        elif not want and d.section("Changelog"):
            append_changelog(d, f"- {today()} — stale cleared: absorbed is current")
        changed.append({"id": d.id, "path": vault.rel(p), "stale": want, "was": have})
        if dry:
            d.verify()
            vault.forget(p)
        else:
            vault.write(d)
    return changed


def _refresh_trace(vault, d):
    """Keep a story's ``sources`` / ``jira`` equal to what its slices trace to. True when it changed."""
    ints, keys = trace_of(vault, d.fm_list("slice_of") or d.fm_get("slice_of"))
    did = False
    for key, want in (("sources", ints), ("jira", keys)):
        have = [str(x).strip() for x in d.fm_list(key)]
        if want != have and (want or key in d.fm):
            d.fm_set(key, want, after="absorbed")
            did = True
    return did


def render(res):
    if not res:
        return "cascade: nothing stale changed"
    return "\n".join(f"{r['id']}: " + ("trace (sources / jira) refreshed" if r.get("trace") and r["stale"] == r["was"]
                                         else f"stale {', '.join(r['stale']) or '— cleared'}") for r in res)
