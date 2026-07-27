"""Report obsolete name occurrences in a file, using _v1_rename_map.

Usage: python _report_obsolete_names.py <file>
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
)


def count_string_lit(text: str, name: str) -> int:
    """Count occurrences of a name as a Python string literal (double or single quoted)."""
    pat = rf'["\']{re.escape(name)}["\']'
    return len(re.findall(pat, text))


def report(path: pathlib.Path) -> None:
    src = path.read_text(encoding="utf-8")
    print(f"File: {path}")
    print(f"  {len(src)} chars, {src.count(chr(10)) + 1} lines")
    print()

    print("OBSOLETE PARAMETER NAMES (as string literals):")
    param_counts: dict[str, int] = {}
    for (_cls, old_p) in PARAM_RENAMES.keys():
        param_counts[old_p] = param_counts.get(old_p, 0) + 0
    for name in list(param_counts.keys()):
        c = count_string_lit(src, name)
        if c > 0:
            param_counts[name] = c
    for name, c in sorted(param_counts.items(), key=lambda x: -x[1]):
        if c > 0:
            print(f"  {c:4d}  {name}")
    if not any(c > 0 for c in param_counts.values()):
        print("  (none)")

    print()
    print("REMOVED PARAMETERS (should NOT appear):")
    for (_cls, p) in REMOVED_PARAMS.keys():
        c = count_string_lit(src, p)
        if c > 0:
            print(f"  {c:4d}  {p}  <- WILL BE UNSUPPORTED; needs manual handling")

    print()
    print("OBSOLETE CLASS NAMES (as string literals):")
    class_counts: dict[str, int] = {}
    all_old_classes = list(CLASS_UPDATES.keys()) + list(CLASS_RENAMES.keys()) + list(REMOVED_CLASSES.keys())
    for name in set(all_old_classes):
        c = count_string_lit(src, name)
        if c > 0:
            class_counts[name] = c
    for name, c in sorted(class_counts.items(), key=lambda x: -x[1]):
        print(f"  {c:4d}  {name}")
    if not class_counts:
        print("  (none)")

    print()
    print("OBSOLETE VALUES (as string literals):")
    value_counts: dict[str, int] = {}
    for v in VALUE_RENAMES.keys():
        c = count_string_lit(src, v)
        if c > 0:
            value_counts[v] = c
    for v, c in sorted(value_counts.items(), key=lambda x: -x[1]):
        print(f"  {c:4d}  {v}")
    if not value_counts:
        print("  (none)")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: _report_obsolete_names.py <file>")
    report(pathlib.Path(sys.argv[1]))
