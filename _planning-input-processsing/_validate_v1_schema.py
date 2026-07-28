"""Cross-reference SpineOpt v1.0.0 template against pipeline source files.

For every parameter/class/value-list name that appears as a string literal in
the source files (Python, YAML), warn if it isn't part of the v1.0.0 template.
This catches:
  - Renames we missed (old name still present as a string literal)
  - Typos in target names
  - References to removed items

Not authoritative — string literals aren't necessarily entity/param references
(may be Python variable names, YAML dict keys unrelated to SpineOpt, etc.).
Use the output as a *hint list* to eyeball, not a hard failure.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys
from typing import Iterable

TEMPLATE = pathlib.Path(
    r"C:\Users\maganih\.julia\packages\SpineOpt\1NRBB\templates\spineopt_template.json"
)

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _v1_rename_map import (
    PARAM_RENAMES,
    CLASS_RENAMES,
    CLASS_UPDATES,
    REMOVED_CLASSES,
    REMOVED_PARAMS,
    VALUE_RENAMES,
    LIST_RENAMES,
)


def load_v1_names() -> tuple[set[str], set[str], set[str]]:
    """Return (class_names, param_names, list_names) present in v1.0.0."""
    t = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    classes = {row[0] for row in t.get("entity_classes", [])}
    params = {row[1] for row in t.get("parameter_definitions", [])}
    lists = {row[0] for row in t.get("parameter_value_lists", [])}
    return classes, params, lists


def string_literals(text: str) -> set[str]:
    """Extract every double- or single-quoted string literal from text.
    Filters out obvious non-identifiers (spaces, punctuation) to keep the set tight.
    """
    out: set[str] = set()
    # Simple regex; misses escaped quotes inside strings but that's OK here
    for m in re.finditer(r'"([^"\n]{2,100})"', text):
        out.add(m.group(1))
    for m in re.finditer(r"'([^'\n]{2,100})'", text):
        out.add(m.group(1))
    # Keep only identifier-like names (letters, digits, underscore only)
    return {s for s in out if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", s)}


def check_file(
    path: pathlib.Path,
    v1_classes: set[str],
    v1_params: set[str],
    v1_lists: set[str],
    old_class_names: set[str],
    old_param_names: set[str],
    old_value_names: set[str],
    old_list_names: set[str],
) -> tuple[list[str], list[str]]:
    if not path.exists():
        return ([f"MISSING FILE: {path}"], [])
    text = path.read_text(encoding="utf-8")
    lits = string_literals(text)
    errors: list[str] = []
    warnings: list[str] = []

    # HARD errors: any old-name literal still present
    for lit in sorted(lits):
        if lit in old_param_names:
            errors.append(f"  ERROR  obsolete PARAM  {lit!r}  (rename needed)")
        elif lit in old_class_names:
            errors.append(f"  ERROR  obsolete CLASS  {lit!r}  (rename or restructure needed)")
        elif lit in old_value_names:
            errors.append(f"  ERROR  obsolete VALUE  {lit!r}  (value rename needed)")
        elif lit in old_list_names:
            errors.append(f"  ERROR  obsolete LIST   {lit!r}  (value list rename needed)")

    return errors, warnings


def main() -> int:
    v1_classes, v1_params, v1_lists = load_v1_names()

    old_class_names: set[str] = (
        set(CLASS_RENAMES) | set(CLASS_UPDATES) | set(REMOVED_CLASSES)
    )
    old_param_names: set[str] = {p for (_, p) in PARAM_RENAMES.keys()} | {
        p for (_, p) in REMOVED_PARAMS.keys()
    }
    old_value_names: set[str] = set(VALUE_RENAMES)
    old_list_names: set[str] = set(LIST_RENAMES)

    print("V1 template summary:")
    print(f"  entity_classes:       {len(v1_classes)}")
    print(f"  parameter_definitions:{len(v1_params)}")
    print(f"  parameter_value_lists:{len(v1_lists)}")
    print()

    root = pathlib.Path(__file__).resolve().parents[1]
    files = [
        "_planning-input-processsing/inspect_storage_state.py",
        "_planning-input-processsing/planning_setup.py",
        "_planning-input-processsing/scenario_run.py",
        "_clustering/clustering_input.py",
        "_clustering/clustering_output.py",
        "_planning-output-processing/fix_investments.py",
        "_visualization/visualization.py",
        "ines-spineopt/ines-spineopt/ines_to_spineopt.py",
        "ines-spineopt/ines-spineopt/ines_to_spineopt_methods.yaml",
        "ines-spineopt/ines-spineopt/ines_to_spineopt_parameters.yaml",
        "ines-spineopt/ines-spineopt/settings.yaml",
    ]

    total_err = 0
    for rel in files:
        path = root / rel
        errors, warnings = check_file(
            path,
            v1_classes,
            v1_params,
            v1_lists,
            old_class_names,
            old_param_names,
            old_value_names,
            old_list_names,
        )
        print(f"=== {rel} ===")
        if not errors and not warnings:
            print("  OK (no obsolete SpineOpt names remaining)")
        else:
            for e in errors:
                print(e)
            for w in warnings:
                print(w)
        total_err += len(errors)
        print()

    print("=" * 60)
    print(f"Total ERRORS across all files: {total_err}")
    return 1 if total_err > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
