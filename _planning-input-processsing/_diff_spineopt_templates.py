"""Normalized diff between SpineOpt v0.11.1 (legacy schema) and v1.0.0 (unified schema).

The two template formats:
  - Legacy:  object_classes + object_parameters + relationship_classes + relationship_parameters
  - Unified: entity_classes (dimensions) + parameter_definitions (per entity_class)

We normalize both to two dicts:
  - classes[name]              -> {"dimensions": (...), "description": str, "type": "object"|"relationship"}
  - params[class::name]        -> {"class": str, "name": str, "default": ..., "value_list": str, "description": str}

Then produce ADDED / REMOVED / CHANGED lists.
"""
from __future__ import annotations

import json
import pathlib
import sys
from typing import Any

OLD = pathlib.Path(
    r"C:\Users\maganih\.julia\packages\SpineOpt\4Vpxd\templates\spineopt_template.json"
)
NEW = pathlib.Path(
    r"C:\Users\maganih\.julia\packages\SpineOpt\1NRBB\templates\spineopt_template.json"
)


def load(p: pathlib.Path) -> dict[str, Any]:
    return json.loads(p.read_text(encoding="utf-8"))


def norm_row(row: list[Any], expected_len: int) -> list[Any]:
    row = list(row)
    while len(row) < expected_len:
        row.append(None)
    return row


def normalize_legacy(t: dict[str, Any]) -> tuple[dict, dict]:
    classes: dict[str, dict] = {}
    for row in t.get("object_classes") or []:
        name, desc, *_ = norm_row(row, 3)
        classes[name] = {"dimensions": (), "description": desc, "type": "object"}
    for row in t.get("relationship_classes") or []:
        name, obj_class_list, desc, *_ = norm_row(row, 3)
        classes[name] = {
            "dimensions": tuple(obj_class_list or ()),
            "description": desc,
            "type": "relationship",
        }

    params: dict[str, dict] = {}
    for row in t.get("object_parameters") or []:
        cls, name, default, value_list, desc, *_ = norm_row(row, 5)
        params[f"{cls}::{name}"] = {
            "class": cls, "name": name, "default": default,
            "value_list": value_list, "description": desc,
        }
    for row in t.get("relationship_parameters") or []:
        cls, name, default, value_list, desc, *_ = norm_row(row, 5)
        params[f"{cls}::{name}"] = {
            "class": cls, "name": name, "default": default,
            "value_list": value_list, "description": desc,
        }
    return classes, params


def normalize_unified(t: dict[str, Any]) -> tuple[dict, dict]:
    classes: dict[str, dict] = {}
    for row in t.get("entity_classes") or []:
        name, dim_list, desc, *_ = norm_row(row, 3)
        dim_tuple = tuple(dim_list or ())
        classes[name] = {
            "dimensions": dim_tuple, "description": desc,
            "type": "object" if not dim_tuple else "relationship",
        }
    params: dict[str, dict] = {}
    for row in t.get("parameter_definitions") or []:
        cls, name, default, value_list, desc, *_ = norm_row(row, 5)
        params[f"{cls}::{name}"] = {
            "class": cls, "name": name, "default": default,
            "value_list": value_list, "description": desc,
        }
    return classes, params


def normalize(t: dict[str, Any]) -> tuple[dict, dict]:
    if "entity_classes" in t:
        return normalize_unified(t)
    return normalize_legacy(t)


def value_lists(t: dict[str, Any]) -> dict[str, list]:
    out: dict[str, list] = {}
    for row in t.get("parameter_value_lists") or []:
        if not row:
            continue
        name = row[0]
        val = row[1] if len(row) > 1 else None
        out.setdefault(name, []).append(val)
    for k in out:
        out[k] = sorted(out[k], key=lambda v: json.dumps(v, sort_keys=True) if v is not None else "")
    return out


def print_class_diff(old_classes: dict, new_classes: dict) -> None:
    added = sorted(set(new_classes) - set(old_classes))
    removed = sorted(set(old_classes) - set(new_classes))
    common = sorted(set(old_classes) & set(new_classes))
    changed = [(c, old_classes[c], new_classes[c]) for c in common if old_classes[c] != new_classes[c]]

    print(f"\n=== entity classes  (+{len(added)}  -{len(removed)}  ~{len(changed)}) ===")
    if added:
        print("  ADDED:")
        for c in added:
            info = new_classes[c]
            dim = f"({','.join(info['dimensions'])})" if info["dimensions"] else ""
            print(f"    + {c}{dim}   [{info['type']}]")
    if removed:
        print("  REMOVED:")
        for c in removed:
            info = old_classes[c]
            dim = f"({','.join(info['dimensions'])})" if info["dimensions"] else ""
            print(f"    - {c}{dim}   [{info['type']}]")
    if changed:
        print("  CHANGED (dimension list or type flipped):")
        for c, o, n in changed:
            print(f"    ~ {c}")
            print(f"        was:  {o}")
            print(f"        now:  {n}")


def print_param_diff(old_params: dict, new_params: dict,
                     added_classes: set, removed_classes: set) -> None:
    added = sorted(set(new_params) - set(old_params))
    removed = sorted(set(old_params) - set(new_params))
    common = sorted(set(old_params) & set(new_params))
    changed_semantic = []
    changed_desc_only = []
    for k in common:
        o, n = old_params[k], new_params[k]
        if o == n:
            continue
        if o["default"] != n["default"] or o["value_list"] != n["value_list"]:
            changed_semantic.append((k, o, n))
        else:
            changed_desc_only.append((k, o, n))

    added_meaningful = [k for k in added if k.split("::")[0] not in added_classes]
    removed_meaningful = [k for k in removed if k.split("::")[0] not in removed_classes]

    print(f"\n=== parameter definitions  (+{len(added)}  -{len(removed)}  ~sem {len(changed_semantic)}  ~desc {len(changed_desc_only)}) ===")

    if added_meaningful:
        print(f"  ADDED (on classes that already existed) [{len(added_meaningful)}]:")
        for k in added_meaningful:
            info = new_params[k]
            print(f"    + {k}   default={info['default']!r}  value_list={info['value_list']!r}")

    if removed_meaningful:
        print(f"  REMOVED (from classes that still exist) [{len(removed_meaningful)}]:")
        for k in removed_meaningful:
            info = old_params[k]
            print(f"    - {k}   was default={info['default']!r}  value_list={info['value_list']!r}")

    added_class_owned = [k for k in added if k.split("::")[0] in added_classes]
    removed_class_owned = [k for k in removed if k.split("::")[0] in removed_classes]
    if added_class_owned:
        print(f"  (also {len(added_class_owned)} parameters attached to newly-added classes; see class diff)")
    if removed_class_owned:
        print(f"  (also {len(removed_class_owned)} parameters attached to removed classes; see class diff)")

    if changed_semantic:
        print(f"  CHANGED default or value_list  [{len(changed_semantic)}]:")
        for k, o, n in changed_semantic:
            if o["default"] != n["default"]:
                print(f"    ~ {k}   default: {o['default']!r}  ->  {n['default']!r}")
            if o["value_list"] != n["value_list"]:
                print(f"    ~ {k}   value_list: {o['value_list']!r}  ->  {n['value_list']!r}")


def print_value_list_diff(old_lists: dict, new_lists: dict) -> None:
    added = sorted(set(new_lists) - set(old_lists))
    removed = sorted(set(old_lists) - set(new_lists))
    common = sorted(set(old_lists) & set(new_lists))
    changed = [(k, old_lists[k], new_lists[k]) for k in common if old_lists[k] != new_lists[k]]

    print(f"\n=== parameter_value_lists  (+{len(added)}  -{len(removed)}  ~{len(changed)}) ===")
    if added:
        print("  ADDED:")
        for k in added:
            print(f"    + {k}   values={new_lists[k]}")
    if removed:
        print("  REMOVED:")
        for k in removed:
            print(f"    - {k}   was values={old_lists[k]}")
    if changed:
        print("  CHANGED (values added/removed within the list):")
        for k, o, n in changed:
            added_vals = sorted(set(map(str, n)) - set(map(str, o)))
            removed_vals = sorted(set(map(str, o)) - set(map(str, n)))
            print(f"    ~ {k}")
            if added_vals:
                print(f"        + values: {added_vals}")
            if removed_vals:
                print(f"        - values: {removed_vals}")


def main() -> int:
    if not OLD.exists() or not NEW.exists():
        print(f"Missing template: OLD={OLD.exists()}  NEW={NEW.exists()}")
        return 1
    old = load(OLD)
    new = load(NEW)

    old_classes, old_params = normalize(old)
    new_classes, new_params = normalize(new)
    old_lists = value_lists(old)
    new_lists = value_lists(new)

    print("=" * 78)
    print(f"OLD: {OLD}")
    print(f"     top-level keys: {sorted(old.keys())}")
    print(f"     {len(old_classes)} entity classes, {len(old_params)} parameter defs, {len(old_lists)} value lists")
    print(f"NEW: {NEW}")
    print(f"     top-level keys: {sorted(new.keys())}")
    print(f"     {len(new_classes)} entity classes, {len(new_params)} parameter defs, {len(new_lists)} value lists")
    print("=" * 78)

    added_classes = set(new_classes) - set(old_classes)
    removed_classes = set(old_classes) - set(new_classes)

    print_class_diff(old_classes, new_classes)
    print_param_diff(old_params, new_params, added_classes, removed_classes)
    print_value_list_diff(old_lists, new_lists)

    return 0


if __name__ == "__main__":
    sys.exit(main())
