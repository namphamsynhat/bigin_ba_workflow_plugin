"""Communication-mode note scaffolding for /bigin-intake.

The capture itself (fetching mail / transcripts, verbatim ``## Raw``) stays with the skill; this only
mints the id under the lock and writes the note skeleton from ``_bigin/templates/intake.md`` so two
parallel captures can never collide on an INT number.

spec.json: {"title", "kind", "source": email|meeting|direct, "source_ref", "source_ids": [],
            "blocks": [{"kind": "email|transcript|attachment|note|webpage|summary", "ref", "text"}],
            "attachments": [], "declared_features": []}
"""
from ..ids import mint_int
from ..util import load_json


def scaffold(vault, spec_path, dry=False):
    spec = load_json(spec_path)
    if dry:
        return {"id": "INT-(next)", "path": "(dry)"}
    nid, path = mint_int(vault, spec)
    return {"id": nid, "path": vault.rel(path)}
