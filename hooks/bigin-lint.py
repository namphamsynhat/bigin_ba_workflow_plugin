#!/usr/bin/env python3
"""Back-compat shim (v1.9.0): bigin-lint now lives in lib/bigin/lint.py — run `bin/bigin lint …`."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from bigin.lint import main  # noqa: E402
sys.exit(main(sys.argv))
