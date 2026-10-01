"""Patch industrial CO2 emission coefficients directly in a built SpineOpt model DB.

The pipeline derives each unit's emission-to-atmosphere coefficient from the
INPUT FUEL's co2_content (coal 0.35, waste 0.30, crude 0.26, fossil CH4 0.20).
That is technology-blind: every refinery route gets 0.26 regardless of whether it
captures its CO2. The authoritative per-route values live in the source Excel
sheet ``ind_process_routes_co2_emission`` and are already net of capture.

Each unit carries flow_ratio_equality_coefficient rows on the 4-element byname
``(unit, out_node, in_node, unit)``:

    emission row   : out_node == 'atmosphere', in_node == <fuel>
    conversion row : out_node == <product>,     in_node == <fuel>

The source emission factor is per unit of OUTPUT product, while the coefficient
is applied per unit of INPUT fuel, so we rescale:

    new_coeff = route_emission * conversion_rate(same fuel -> product)

Usage:
    python tools/patch_co2_in_model_db.py <model_db.sqlite>            # dry run
    python tools/patch_co2_in_model_db.py <model_db.sqlite> --apply    # write
"""
from __future__ import annotations

import argparse
import collections
import json
import shutil
import sqlite3
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
XLSX = ROOT / "data" / "Industry" / "technology_catalogue_ind_nuts0_nuts3.xlsx"
SHEET = "ind_process_routes_co2_emission"
YEAR = "2030"  # values are identical across 2030/2040/2050 (verified)
TOL = 1e-12


def is_co2_node(name):
    return name == "CO2" or name.startswith("CO2_") or name.startswith("CO2-")


def scalar(raw):
    if raw is None:
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    if isinstance(raw, (bytes, bytearray)):
        try:
            raw = raw.decode("utf-8")
        except UnicodeDecodeError:
            return None
    try:
        return float(raw)
    except (TypeError, ValueError):
        pass
    try:
        parsed = json.loads(raw)
    except (TypeError, ValueError):
        return None
    return float(parsed) if isinstance(parsed, (int, float)) else None


def flat_byname(con, eid):
    out = []
    for (el_name,) in con.execute(
        "SELECT el.name FROM entity_element ee JOIN entity el ON el.id = ee.element_id "
        "WHERE ee.entity_id = ? ORDER BY ee.position",
        (eid,),
    ):
        leaves = [
            r[0]
            for r in con.execute(
                "SELECT el.name FROM entity_element ee JOIN entity el ON el.id = ee.element_id "
                "WHERE ee.entity_id = (SELECT id FROM entity WHERE name = ?) ORDER BY ee.position",
                (el_name,),
            )
        ]
        out.extend(leaves or [el_name])
    return out


def load_source():
    """route name -> emission factor (per unit of output product)."""
    df = pd.ExcelFile(XLSX).parse(SHEET)
    col = next((c for c in df.columns if str(c).strip() == YEAR), None)
    if col is None:
        raise SystemExit("no %s column in %s" % (YEAR, SHEET))
    out = {}
    for ind, val in zip(df["Industry"], df[col]):
        out[str(ind)] = float(val)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("db")
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry run)")
    ap.add_argument("--backup", action="store_true", help="save a .prepatch copy before writing")
    args = ap.parse_args()

    source = load_source()
    print("source routes read : %d" % len(source))

    if args.apply and args.backup:
        bak = Path(args.db).with_suffix(".prepatch.sqlite")
        shutil.copy2(args.db, bak)
        print("backup written     : %s" % bak)

    con = sqlite3.connect(args.db)

    rows = con.execute(
        "SELECT pv.id, e.id, pv.value FROM parameter_value pv "
        "JOIN parameter_definition pd ON pd.id = pv.parameter_definition_id "
        "JOIN entity e ON e.id = pv.entity_id "
        "WHERE pd.name = 'flow_ratio_equality_coefficient'"
    ).fetchall()

    emissions = []  # (pv_id, unit, fuel, old_coeff)
    conv = collections.defaultdict(lambda: collections.defaultdict(dict))
    skipped_nonscalar = 0

    for pv_id, eid, raw in rows:
        flat = flat_byname(con, eid)
        if len(flat) != 4:
            continue
        unit, out_node, in_node = flat[0], flat[1], flat[2]
        val = scalar(raw)
        if out_node == "atmosphere":
            if val is None:
                skipped_nonscalar += 1
            else:
                emissions.append((pv_id, unit, in_node, val))
        elif not is_co2_node(out_node):
            if val is not None:
                conv[unit][in_node][out_node] = val

    print("emission rows      : %d (non-scalar skipped: %d)" % (len(emissions), skipped_nonscalar))

    planned, unmatched_route, ambiguous, no_conv = [], [], [], []
    for pv_id, unit, fuel, old in emissions:
        route = unit.rsplit("_", 1)[0]
        if route not in source:
            unmatched_route.append((unit, route))
            continue
        cands = conv.get(unit, {}).get(fuel, {})
        if not cands:
            no_conv.append((unit, fuel))
            continue
        if len(cands) > 1:
            ambiguous.append((unit, fuel, dict(cands)))
            continue
        product, rate = next(iter(cands.items()))
        new = source[route] * rate
        planned.append((pv_id, unit, fuel, product, old, new, source[route], rate))

    print("planned updates    : %d" % len(planned))
    print("  route not in xlsx: %d  (left untouched - energy-sector units)" % len(unmatched_route))
    print("  no conversion    : %d" % len(no_conv))
    print("  ambiguous        : %d" % len(ambiguous))

    if unmatched_route:
        left = sorted(set(r for _u, r in unmatched_route))
        print("  untouched routes : %s" % ", ".join(left))
    for label, items in (("no conversion", no_conv), ("ambiguous", ambiguous)):
        for it in items[:10]:
            print("    [%s] %r" % (label, it))

    print()
    print("--- sample of planned changes ---")
    print("%-26s %-10s %-10s %10s -> %-10s  (emis x rate)" % ("unit", "fuel", "product", "old", "new"))
    for _pv, unit, fuel, product, old, new, emis, rate in planned[:20]:
        print("%-26s %-10s %-10s %10.5f -> %-10.5f  (%.4f x %.4f)"
              % (unit, fuel, product, old, new, emis, rate))

    changed = [p for p in planned if abs(p[4] - p[5]) > TOL]
    print()
    print("rows whose value actually changes: %d of %d" % (len(changed), len(planned)))
    negatives = [p for p in planned if p[5] < 0]
    print("rows with NEGATIVE new value (BECCS): %d" % len(negatives))
    for p in negatives[:10]:
        print("    %s  %.6f" % (p[1], p[5]))
    zeros = [p for p in planned if abs(p[5]) < TOL]
    print("rows with ZERO new value: %d" % len(zeros))

    if not args.apply:
        print()
        print("DRY RUN - nothing written. Re-run with --apply to commit.")
        con.close()
        return 0

    cur = con.cursor()
    for pv_id, _u, _f, _p, _old, new, _e, _r in planned:
        cur.execute(
            "UPDATE parameter_value SET value = ?, type = 'float' WHERE id = ?",
            (repr(float(new)).encode("utf-8"), pv_id),
        )
    con.commit()
    print()
    print("APPLIED: %d rows updated in %s" % (len(planned), args.db))
    con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
