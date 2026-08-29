#!/usr/bin/env python3
"""od_common.py — discovery helpers shared by sync_feature.py and check_setup.py.

Everything here reads the local filesystem and Open Design's sqlite catalog. Nothing in this module
calls an MCP tool, so a caller pays no model tokens to learn where the vault is, which projects
exist, or which design systems are installed.
"""
import glob
import os
import re
import sqlite3
import sys
from pathlib import Path

MCP_SERVER_SUBSTRING = "open-design"


def find_vault_root() -> Path:
    """Finds the vault root by searching upward for its own markers."""
    env_root = os.environ.get("VAULT_ROOT")
    if env_root and os.path.exists(env_root):
        return Path(env_root).resolve()

    current = Path.cwd().resolve()
    for parent in [current] + list(current.parents):
        if (parent / "01-Requirements").exists() or (parent / "_bigin").exists():
            return parent

    return current


def find_open_design_data_dir() -> Path:
    """Discovers Open Design's data directory cross-platform (Windows, macOS, Linux)."""
    env_od = os.environ.get("OPEN_DESIGN_DATA_DIR")
    if env_od and os.path.exists(env_od):
        return Path(env_od).resolve()

    candidate_bases = []
    if sys.platform == "win32":
        app_data = os.environ.get("APPDATA")
        if app_data:
            candidate_bases.append(Path(app_data) / "Open Design")
        candidate_bases.append(Path.home() / "AppData" / "Roaming" / "Open Design")
    elif sys.platform == "darwin":
        candidate_bases.append(Path.home() / "Library" / "Application Support" / "Open Design")
    else:
        xdg_config = os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))
        candidate_bases.append(Path(xdg_config) / "Open Design")

    for base in candidate_bases:
        if not base.exists():
            continue
        for pattern in [
            str(base / "namespaces" / "*" / "data"),
            str(base / "data"),
            str(base),
        ]:
            for match in sorted(glob.glob(pattern)):
                data_path = Path(match)
                if (data_path / "app.sqlite").exists():
                    return data_path

    raise FileNotFoundError(
        "Could not automatically locate Open Design's data directory. "
        "Confirm Open Design is installed, or set OPEN_DESIGN_DATA_DIR."
    )


def list_projects(od_data_dir: Path, limit: int = None) -> list:
    """Returns [(id, name, design_system_id, updated_at_ms)], most-recently-updated first."""
    conn = sqlite3.connect(f"file:{od_data_dir / 'app.sqlite'}?mode=ro", uri=True)
    try:
        sql = "SELECT id, name, design_system_id, updated_at FROM projects ORDER BY updated_at DESC"
        if limit:
            sql += f" LIMIT {int(limit)}"
        return conn.execute(sql).fetchall()
    finally:
        conn.close()


def resolve_project(od_data_dir: Path, project_name: str = None) -> tuple:
    """Resolves one project by name substring, else the most-recently-updated. Returns (id, name)."""
    conn = sqlite3.connect(f"file:{od_data_dir / 'app.sqlite'}?mode=ro", uri=True)
    try:
        if project_name:
            row = conn.execute(
                "SELECT id, name FROM projects WHERE name LIKE ? ORDER BY updated_at DESC LIMIT 1",
                (f"%{project_name}%",),
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT id, name FROM projects ORDER BY updated_at DESC LIMIT 1"
            ).fetchone()
    finally:
        conn.close()

    if not row:
        target = f"matching '{project_name}'" if project_name else "(any)"
        raise ValueError(f"No Open Design project found {target}.")
    return row[0], row[1]


def project_dir(od_data_dir: Path, project_id: str) -> Path:
    d = od_data_dir / "projects" / project_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def find_design_systems(od_data_dir: Path) -> list:
    """Lists installed design-system ids — bundled with the app plus any user-added ones.

    These are the same catalog the MCP `resources/list` surface exposes as
    od://design-systems/<id>/DESIGN.md, read straight off disk so picking one costs no tokens.
    """
    ids = set()

    user_dir = od_data_dir / "design-systems"
    if user_dir.exists():
        ids.update(p.name for p in user_dir.iterdir() if p.is_dir() and not p.name.startswith("_"))

    bundled_globs = []
    if sys.platform == "darwin":
        bundled_globs.append("/Applications/Open Design.app/Contents/Resources/open-design/design-systems")
    # the app bundle sits beside the data dir's installation on Linux/Windows installs
    bundled_globs.append(str(od_data_dir.parent.parent.parent / "open-design" / "design-systems"))

    for base in bundled_globs:
        p = Path(base)
        if p.exists():
            ids.update(x.name for x in p.iterdir() if x.is_dir() and not x.name.startswith("_"))

    return sorted(ids)


def read_app_config(od_data_dir: Path) -> dict:
    """Reads app-config.json — the offline source for installed agents and their chosen models."""
    import json
    cfg = od_data_dir / "app-config.json"
    if not cfg.exists():
        return {}
    try:
        return json.loads(cfg.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return {}


def read_project_settings(vault_root: Path) -> dict:
    """Reads the persisted od_* settings from _bigin/system/project.md's frontmatter."""
    pf = vault_root / "_bigin" / "system" / "project.md"
    if not pf.exists():
        return {}
    text = pf.read_text(encoding="utf-8", errors="replace")
    fm = re.search(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    scope = fm.group(1) if fm else text
    return {
        m.group(1): m.group(2).strip().strip("\"'")
        for m in re.finditer(r"^(od_[a-z_]+)\s*:\s*(.*)$", scope, re.MULTILINE)
        if m.group(2).strip()
    }
