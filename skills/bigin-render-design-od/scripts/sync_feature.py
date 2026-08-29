#!/usr/bin/env python3
"""sync_feature.py — copy vault markdown artifacts into an Open Design project's file tree.

Used by /bigin-render-design-od Step 1 (per-feature sync) and Step 4 (navigation-map sync). It
never calls Open Design's MCP tools: Open Design's daemon watches a project's directory on disk, so
writing the files there is what makes them show up in the app's Text tab. If a target file already
exists it is overwritten — the vault is always the source of truth, never the OD project.

Vault filenames carry spaces (`UC-012 Manage Wallet.md`) and an `@`-mention terminates at the first
space, so every file is copied under a space-free name and the printed prompt mentions that name.

usage:
    sync_feature.py <slug> [<slug2> ...] [--project NAME]   sync one or more features by slug
    sync_feature.py --all [--project NAME]                  sync every feature hub in the vault
    sync_feature.py --nav-map [--project NAME]              sync 04-UIUX/_ux/navigation-map.md only

    --project NAME   match an Open Design project by name substring (most-recently-updated wins a
                     tie). Omit to use the single most-recently-updated project on the daemon.

Prints one ready-to-use `@`-mention prompt per synced feature, and exits non-zero if a named
feature's hub is missing or if no Open Design project can be resolved.
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import od_common as od  # noqa: E402


def mention_name(filename: str) -> str:
    """Renders a vault filename as a name safe to `@`-mention — no spaces, no other separators."""
    stem, _, suffix = filename.rpartition(".")
    return re.sub(r"[^A-Za-z0-9._-]+", "-", stem).strip("-") + "." + suffix


def copy_file_by_prefix(search_dir: Path, prefix: str, target_dir: Path, copied: list) -> str:
    """Copies the first `<prefix>*.md` in search_dir under a mention-safe name. Returns that name."""
    if not search_dir.exists():
        return None
    for file_path in sorted(search_dir.iterdir()):
        if file_path.name.startswith(prefix) and file_path.suffix == ".md":
            safe = mention_name(file_path.name)
            shutil.copy2(file_path, target_dir / safe)
            copied.append(safe)
            return safe
    return None


def sync_feature(vault_root: Path, target_dir: Path, feature_slug: str) -> None:
    hub_file = vault_root / "01-Requirements" / "_features" / f"{feature_slug}.md"
    if not hub_file.exists():
        print(f"[!] Error: feature hub not found at: {hub_file}", file=sys.stderr)
        sys.exit(1)

    content = hub_file.read_text(encoding="utf-8")
    fm_match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not fm_match:
        print(f"[!] Error: no YAML frontmatter in {hub_file}", file=sys.stderr)
        sys.exit(1)
    frontmatter = fm_match.group(1)

    ucs = re.findall(r"UC-\d+", frontmatter)
    brs = re.findall(r"BR-\d+", frontmatter)
    entities = re.findall(r"EN-\d+", frontmatter)
    uiux_match = re.search(r"uiux:\s*(UX-\d+)", frontmatter)
    uiux = uiux_match.group(1) if uiux_match else None

    copied = []

    hub_name = mention_name(f"{feature_slug}.md")
    shutil.copy2(hub_file, target_dir / hub_name)
    copied.append(hub_name)

    ux_fname = copy_file_by_prefix(vault_root / "04-UIUX", uiux, target_dir, copied) if uiux else None

    uc_fnames = [
        fn for uc in ucs
        if (fn := copy_file_by_prefix(vault_root / "01-Requirements" / "_ucs", uc, target_dir, copied))
    ]
    br_fnames = [
        fn for br in brs
        if (fn := copy_file_by_prefix(vault_root / "01-Requirements" / "_brs", br, target_dir, copied))
    ]
    for en in entities:
        copy_file_by_prefix(vault_root / "01-Requirements" / "_entities", en, target_dir, copied)

    print(f"[✓] Synced {len(copied)} file(s) for '{feature_slug}' -> {target_dir}")

    print("\n" + "=" * 60)
    print(f"READY-TO-USE PROMPT — {feature_slug}")
    print("=" * 60)
    prompt = f"Generate the design of feature {feature_slug}\n"
    if ux_fname:
        prompt += f"the UX document: @{ux_fname}\n"
    if uc_fnames:
        prompt += f"The User Stories: {', '.join('@' + fn for fn in uc_fnames)}\n"
    if br_fnames:
        prompt += f"The Business Rules: {', '.join('@' + fn for fn in br_fnames)}\n"
    prompt += f"\nthe Feature that contains the unrefined material: @{hub_name}\n"
    print(prompt)


def sync_nav_map(vault_root: Path, target_dir: Path) -> None:
    nav_map = vault_root / "04-UIUX" / "_ux" / "navigation-map.md"
    if not nav_map.exists():
        print(f"[!] Error: navigation map not found at: {nav_map}", file=sys.stderr)
        sys.exit(1)
    shutil.copy2(nav_map, target_dir / "navigation-map.md")
    print(f"[✓] Synced navigation-map.md -> {target_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("slugs", nargs="*", help="feature slug(s) to sync")
    parser.add_argument("--all", action="store_true", help="sync every feature hub in the vault")
    parser.add_argument("--nav-map", action="store_true", help="sync 04-UIUX/_ux/navigation-map.md only")
    parser.add_argument("--project", default=None, help="Open Design project name substring")
    args = parser.parse_args()

    vault_root = od.find_vault_root()
    od_data_dir = od.find_open_design_data_dir()
    project_id, project_name = od.resolve_project(od_data_dir, args.project)
    target_dir = od.project_dir(od_data_dir, project_id)
    print(f"[*] Target Open Design project: '{project_name}' (od_project: {project_id})")

    if args.nav_map:
        sync_nav_map(vault_root, target_dir)
        return

    if args.all:
        hub_dir = vault_root / "01-Requirements" / "_features"
        slugs = sorted(p.stem for p in hub_dir.glob("*.md")) if hub_dir.exists() else []
        if not slugs:
            print(f"[!] No feature hubs found in {hub_dir}", file=sys.stderr)
            sys.exit(1)
    else:
        slugs = args.slugs
        if not slugs:
            parser.error("provide one or more slugs, or pass --all / --nav-map")

    for slug in slugs:
        sync_feature(vault_root, target_dir, slug)


if __name__ == "__main__":
    main()
