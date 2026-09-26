"""Shared test helpers: fresh fixture copies, CLI runner, file digests."""
import contextlib
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "lib"))
os.environ.setdefault("BIGIN_TODAY", "2026-09-27")

from bigin import cli  # noqa: E402
from bigin.vault import Vault  # noqa: E402

FIX = os.path.join(HERE, "fixtures")


def fresh(name):
    """A throwaway copy of tests/fixtures/<name>; returns (root, Vault)."""
    d = tempfile.mkdtemp(prefix=f"bigin-{name}-")
    root = os.path.join(d, name)
    shutil.copytree(os.path.join(FIX, name), root)
    return root, Vault(root)


def run(root, *args):
    """Run the CLI in-process; returns (exit code, stdout)."""
    buf = io.StringIO()
    err = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
        code = cli.main(["--vault", root] + list(args))
    return code, buf.getvalue() + err.getvalue()


def digest(root, sub=("01-Requirements", "00-Inbox")):
    """{relpath: sha1} over the vault's content dirs."""
    out = {}
    for s in sub:
        base = os.path.join(root, s)
        for dp, _dn, fns in os.walk(base):
            for fn in fns:
                p = os.path.join(dp, fn)
                with open(p, "rb") as f:
                    out[os.path.relpath(p, root)] = hashlib.sha1(f.read()).hexdigest()
    return out


def read(root, rel):
    with open(os.path.join(root, rel), encoding="utf-8") as f:
        return f.read()


def find(root, sub, prefix):
    for fn in os.listdir(os.path.join(root, sub)):
        if fn.startswith(prefix):
            return os.path.join(sub, fn)
    raise AssertionError(f"{prefix} not in {sub}")


def write_json(root, name, obj):
    p = os.path.join(root, name)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
    return p


def lint_clean(root):
    code, out = run(root, "lint", "--full")
    assert code == 0, out
    return out
