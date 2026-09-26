#!/usr/bin/env python3
"""Stdlib test runner — no pytest needed (the tests are pytest-compatible too).

    python3 tests/run.py [-k substring] [-v]
"""
import importlib.util
import glob
import os
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))


def main(argv):
    pattern = argv[argv.index("-k") + 1] if "-k" in argv else ""
    verbose = "-v" in argv
    os.environ.setdefault("BIGIN_TODAY", "2026-09-27")
    passed, failed = 0, []
    t0 = time.time()
    for path in sorted(glob.glob(os.path.join(HERE, "test_*.py"))):
        spec = importlib.util.spec_from_file_location(os.path.basename(path)[:-3], path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for name in sorted(n for n in dir(mod) if n.startswith("test_")):
            full = f"{os.path.basename(path)}::{name}"
            if pattern and pattern not in full:
                continue
            try:
                getattr(mod, name)()
                passed += 1
                if verbose:
                    print(f"PASS {full}")
            except Exception:
                failed.append((full, traceback.format_exc()))
                print(f"FAIL {full}")
    for full, tb in failed:
        print(f"\n=== {full}\n{tb}")
    print(f"\n{passed} passed, {len(failed)} failed in {time.time() - t0:.1f}s")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
