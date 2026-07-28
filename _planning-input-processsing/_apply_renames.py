"""Apply v0.11.1 -> v1.0.0 parameter/class/value renames to a source file.

Handles Python (.py), YAML (.yaml/.yml), and JSON (.json) by treating them
uniformly: any occurrence of the OLD name as a quoted string literal (double,
single, or YAML unquoted plain scalar) is replaced with the NEW name.

Class renames and class-structural updates (unit__from_node -> node__to_unit
with byname swap) are handled for the class NAME string only — the byname
argument-order swap must be done by hand where relevant. This script prints a
warning for any hit on such a class so you can review.

Usage:
    python _apply_renames.py <path> [--dry-run]

--dry-run: report intended edits but don't modify the file.
"""

from __future__ import annotations

import re
import sys
import pathlib

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


def _quoted_variants(name: str) -> list[str]:
    """String literal variants to match: "name", 'name'."""
    return [f'"{name}"', f"'{name}'"]


def apply_to_source(src: str, log: list[str]) -> str:
    # 1) Parameter renames (many): safe because they're on unique names.
    for (_cls, old_p), new_p in PARAM_RENAMES.items():
        for variant in _quoted_variants(old_p):
            new_variant = variant.replace(old_p, new_p)
            n = src.count(variant)
            if n:
                src = src.replace(variant, new_variant)
                log.append(f"  param  {old_p:<50s} -> {new_p:<50s}  ({n}x, {variant[0]})")

    # 2) Value renames.
    for old_v, new_v in VALUE_RENAMES.items():
        for variant in _quoted_variants(old_v):
            new_variant = variant.replace(old_v, new_v)
            n = src.count(variant)
            if n:
                src = src.replace(variant, new_variant)
                log.append(f"  value  {old_v:<50s} -> {new_v:<50s}  ({n}x)")

    # 3) Parameter-value-list renames.
    for old_l, new_l in LIST_RENAMES.items():
        for variant in _quoted_variants(old_l):
            new_variant = variant.replace(old_l, new_l)
            n = src.count(variant)
            if n:
                src = src.replace(variant, new_variant)
                log.append(f"  list   {old_l:<50s} -> {new_l:<50s}  ({n}x)")

    # 4) Class name renames (simple: no dim change).
    for old_c, new_c in CLASS_RENAMES.items():
        for variant in _quoted_variants(old_c):
            new_variant = variant.replace(old_c, new_c)
            n = src.count(variant)
            if n:
                src = src.replace(variant, new_variant)
                log.append(f"  class  {old_c:<50s} -> {new_c:<50s}  ({n}x)")

    # 5) Class-structural updates: mechanical string swap for class NAME only.
    #    WARN loudly — the caller almost always also needs to swap arg order or
    #    change dimensionality by hand.
    for old_c, (new_c, mapping) in CLASS_UPDATES.items():
        for variant in _quoted_variants(old_c):
            new_variant = variant.replace(old_c, new_c)
            n = src.count(variant)
            if n:
                src = src.replace(variant, new_variant)
                log.append(f"  CLASS-UPD (review byname!)  {old_c} -> {new_c} mapping={mapping} ({n}x)")

    # 6) Removed classes and params: flag but do not touch (needs manual attention).
    for old_c, why in REMOVED_CLASSES.items():
        for variant in _quoted_variants(old_c):
            n = src.count(variant)
            if n:
                log.append(f"  REMOVED-CLASS (manual!)     {old_c} ({n}x) — {why}")
    for (_cls, p), why in REMOVED_PARAMS.items():
        for variant in _quoted_variants(p):
            n = src.count(variant)
            if n:
                log.append(f"  REMOVED-PARAM (manual!)     {p} ({n}x) — {why}")

    return src


def main() -> int:
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    args = [a for a in args if a != "--dry-run"]
    if len(args) != 1:
        sys.exit("Usage: _apply_renames.py <file> [--dry-run]")
    path = pathlib.Path(args[0])
    if not path.is_file():
        sys.exit(f"Not a file: {path}")

    src = path.read_text(encoding="utf-8")
    log: list[str] = []
    new_src = apply_to_source(src, log)

    if not log:
        print(f"No changes needed in {path}")
        return 0

    header = "DRY RUN — would apply these changes" if dry_run else f"Applying changes to {path}"
    print(header)
    for line in log:
        print(line)
    print(f"Total distinct rules that fired: {len(log)}")

    if not dry_run:
        path.write_text(new_src, encoding="utf-8")
        print(f"Wrote {path} ({len(new_src)} chars)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
