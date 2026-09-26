"""A small JSON Schema (draft 2020-12 subset) validator — stdlib only.

Supports: type (incl. lists), enum, const, required, properties, additionalProperties (bool or
schema), items, minItems, maxItems, minLength, maxLength, pattern, minimum, oneOf, anyOf, allOf,
$ref to "#/$defs/…", if/then (property-const conditions). Enough for the engine's own schemas;
not a general-purpose implementation.
"""
import json
import os
import re

SCHEMA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema")
_TYPES = {
    "object": dict, "array": list, "string": str, "boolean": bool, "null": type(None),
}


def load(name):
    with open(os.path.join(SCHEMA_DIR, f"{name}.json"), encoding="utf-8") as f:
        return json.load(f)


def _is_type(v, t):
    if t == "integer":
        return isinstance(v, int) and not isinstance(v, bool)
    if t == "number":
        return isinstance(v, (int, float)) and not isinstance(v, bool)
    return isinstance(v, _TYPES[t])


def validate(inst, schema, root=None, path="$"):
    """Return a list of error strings (empty = valid)."""
    root = root or schema
    errs = []
    if "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/"):
            return [f"{path}: unsupported $ref {ref}"]
        node = root
        for part in ref[2:].split("/"):
            node = node[part]
        errs += validate(inst, node, root, path)
    t = schema.get("type")
    if t is not None:
        ts = t if isinstance(t, list) else [t]
        if not any(_is_type(inst, x) for x in ts):
            return errs + [f"{path}: expected {'/'.join(ts)}, got {type(inst).__name__}"]
    if "const" in schema and inst != schema["const"]:
        errs.append(f"{path}: must be {schema['const']!r}")
    if "enum" in schema and inst not in schema["enum"]:
        errs.append(f"{path}: {inst!r} not one of {schema['enum']}")
    if isinstance(inst, str):
        if "minLength" in schema and len(inst) < schema["minLength"]:
            errs.append(f"{path}: shorter than {schema['minLength']}")
        if "maxLength" in schema and len(inst) > schema["maxLength"]:
            errs.append(f"{path}: longer than {schema['maxLength']}")
        if "pattern" in schema and not re.search(schema["pattern"], inst):
            errs.append(f"{path}: {inst!r} does not match /{schema['pattern']}/")
    if isinstance(inst, (int, float)) and not isinstance(inst, bool):
        if "minimum" in schema and inst < schema["minimum"]:
            errs.append(f"{path}: below {schema['minimum']}")
    if isinstance(inst, list):
        if "minItems" in schema and len(inst) < schema["minItems"]:
            errs.append(f"{path}: fewer than {schema['minItems']} item(s)")
        if "maxItems" in schema and len(inst) > schema["maxItems"]:
            errs.append(f"{path}: more than {schema['maxItems']} item(s)")
        if "items" in schema:
            for i, x in enumerate(inst):
                errs += validate(x, schema["items"], root, f"{path}[{i}]")
    if isinstance(inst, dict):
        for k in schema.get("required", []):
            if k not in inst:
                errs.append(f"{path}: missing required '{k}'")
        props = schema.get("properties", {})
        for k, v in inst.items():
            if k in props:
                errs += validate(v, props[k], root, f"{path}.{k}")
            else:
                ap = schema.get("additionalProperties", True)
                if ap is False:
                    errs.append(f"{path}: unexpected property '{k}'")
                elif isinstance(ap, dict):
                    errs += validate(v, ap, root, f"{path}.{k}")
    if "allOf" in schema:
        for sub in schema["allOf"]:
            errs += validate(inst, sub, root, path)
    if "anyOf" in schema:
        if not any(not validate(inst, sub, root, path) for sub in schema["anyOf"]):
            errs.append(f"{path}: matches none of anyOf")
    if "oneOf" in schema:
        n = sum(1 for sub in schema["oneOf"] if not validate(inst, sub, root, path))
        if n != 1:
            errs.append(f"{path}: matches {n} of oneOf (need exactly 1)")
    if "if" in schema:
        if not validate(inst, schema["if"], root, path):
            if "then" in schema:
                errs += validate(inst, schema["then"], root, path)
        elif "else" in schema:
            errs += validate(inst, schema["else"], root, path)
    return errs


def check(inst, name):
    return validate(inst, load(name))
