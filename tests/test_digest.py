"""W4 — one digest, three audiences: sections from engine data, no ids in the client body, empty sections omitted."""
import json
import os
import re

from helpers import fresh, read, run, write_json

IDS = re.compile(r"\b(?:UC|BR|INT|EN|PP|US|EP|UX)-\d+\b")
SINCE = ("--since", "2026-09-01")


def _digest(root, aud, *extra):
    code, out = run(root, "digest", "--for", aud, *SINCE, *extra)
    assert code == 0, out
    return out


def test_ba_digest_has_the_sections_the_vault_supports():
    root, _ = fresh("comm-vault")
    out = _digest(root, "ba")
    for sec in ("## Came in", "## Changed", "## Waiting", "## Ready to approve"):
        assert sec in out, (sec, out)
    assert "INT-003" in out and "UC-001" in out and "[client] Is there a maximum amount" in out
    assert "UC-001 Submit a grant application" not in out.split("## Ready to approve")[1]      # UC-001 still has an open question
    assert "## Stale downstream" not in out and "## Spend" not in out and "## Dev feedback" not in out   # empty → omitted


def test_since_filters_by_date_and_a_future_date_is_empty():
    root, _ = fresh("comm-vault")
    code, out = run(root, "digest", "--for", "ba", "--since", "2030-01-01")
    assert code == 0
    assert "## Came in" not in out and "## Changed" not in out and "## Waiting" in out         # open questions are timeless
    code, out = run(root, "digest", "--since", "last-tuesday")
    assert code == 2 and "neither a date" in out


def test_client_digest_has_no_vault_ids_outside_the_trailing_ref():
    root, _ = fresh("comm-vault")
    out = _digest(root, "client")
    assert "## Came in" not in out and "## Ready to approve" not in out and "## Stale downstream" not in out
    assert "## Changed" in out and "## Waiting" in out
    for ln in out.splitlines():
        body = re.sub(r"\(ref:[^)]*\)", "", ln)
        assert not IDS.search(body), ln
    assert "(ref: UC-001)" in out                                    # the id survives, in the ref
    assert "[client]" not in out and "[dev]" not in out


def test_dev_digest_keeps_only_approved_scope_and_dev_questions():
    root, _ = fresh("comm-vault")
    assert "Nothing new" in _digest(root, "dev")                    # nothing approved, nothing waiting on dev
    p = os.path.join(root, "01-Requirements/_ucs", [f for f in os.listdir(os.path.join(root, "01-Requirements/_ucs")) if f.startswith("UC-002")][0])
    s = read(root, os.path.relpath(p, root)).replace("status: draft", "status: approved", 1)
    open(p, "w", encoding="utf-8", newline="\n").write(s)
    out = _digest(root, "dev")
    assert "## Changed" in out and "Review an application" in out and "Pay an approved grant" not in out, out
    assert "## Waiting" not in out and "## Came in" not in out


def test_write_saves_to_the_outbox_and_dry_does_not():
    root, _ = fresh("comm-vault")
    code, out = run(root, "--json", "digest", "--for", "client", *SINCE, "--write")
    assert code == 0 and json.loads(out)["written"] == "06-Outbox/digest-2026-09-27-client.md", out
    assert "# Digest — client" in read(root, "06-Outbox/digest-2026-09-27-client.md")
    root2, _ = fresh("comm-vault")
    run(root2, "digest", *SINCE, "--write", "--dry")
    assert not os.path.exists(os.path.join(root2, "06-Outbox"))


def test_default_since_is_the_previous_run_not_the_current_one():
    root, _ = fresh("comm-vault")
    for rid, created in (("20260910-extract", "2026-09-10"), ("20260927-extract", "2026-09-27")):
        os.makedirs(os.path.join(root, "_runs", rid), exist_ok=True)
        write_json(root, f"_runs/{rid}/plan.json", {"id": rid, "created": created})
    code, out = run(root, "digest")
    assert code == 0 and "since 2026-09-10" in out, out
