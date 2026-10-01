"""Survey of atmosphere emission ratios vs. same-fuel conversion rates.

READ-ONLY. Writes a report to logs/patch_survey.txt.

Usage:
    python tools/survey_co2_patch.py <model_db.sqlite>
"""
from __future__ import annotations

import collections
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "checkpoints" / "Final_SpineOpt_Model.tiny.1rep.repfix.sqlite"
OUT = ROOT / "logs" / "patch_survey.txt"

NON_PRODUCT = {"atmosphere"}


def is_co2_node(name):
    return name == "CO2" or name.startswith("CO2_") or name.startswith("CO2-")


def scalar(raw):
    """Return a float if the stored parameter value is a plain scalar, else None."""
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
    if isinstance(parsed, (int, float)):
        return float(parsed)
    return None


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


def load_rows(con):
    rows = con.execute(
        "SELECT e.id, pv.value FROM parameter_value pv "
        "JOIN parameter_definition pd ON pd.id = pv.parameter_definition_id "
        "JOIN entity e ON e.id = pv.entity_id "
        "WHERE pd.name = 'flow_ratio_equality_coefficient'"
    ).fetchall()
    for eid, raw in rows:
        flat = flat_byname(con, eid)
        if len(flat) == 4:
            yield eid, flat, raw


def main(db_path):
    con = sqlite3.connect(db_path)

    emissions = []
    non_scalar_emissions = []
    conv = collections.defaultdict(lambda: collections.defaultdict(dict))
    non_scalar_conv = 0

    total = 0
    for eid, flat, raw in load_rows(con):
        unit, out_node, in_node = flat[0], flat[1], flat[2]
        total += 1
        val = scalar(raw)
        if out_node == "atmosphere":
            if val is None:
                non_scalar_emissions.append((unit, in_node))
            else:
                emissions.append((eid, unit, in_node, val))
        elif out_node in NON_PRODUCT or is_co2_node(out_node):
            continue
        else:
            if val is None:
                non_scalar_conv += 1
            else:
                conv[unit][in_node][out_node] = val

    con.close()

    exact, multi, missing = [], [], []
    for _eid, unit, fuel, coeff in emissions:
        cands = conv.get(unit, {}).get(fuel, {})
        if not cands:
            missing.append((unit, fuel, coeff))
        elif len(cands) == 1:
            prod, rate = next(iter(cands.items()))
            exact.append((unit, fuel, coeff, prod, rate))
        else:
            multi.append((unit, fuel, coeff, dict(cands)))

    lines = [
        "db                         : %s" % db_path,
        "flow-ratio rows (4-dim)    : %d" % total,
        "emission rows (atmosphere) : %d" % len(emissions),
        "  non-scalar, skipped      : %d" % len(non_scalar_emissions),
        "conversion rows, non-scalar: %d" % non_scalar_conv,
        "",
        "emission rows with EXACTLY ONE same-fuel conversion : %d" % len(exact),
        "emission rows with MULTIPLE same-fuel conversions   : %d" % len(multi),
        "emission rows with NO same-fuel conversion          : %d" % len(missing),
        "",
        "--- examples: exactly one (unit, fuel, emission_coeff, product, rate) ---",
    ]
    lines += ["  %r" % (r,) for r in exact[:15]]
    lines += ["", "--- multiple candidates (needs a rule) ---"]
    lines += ["  %r" % (r,) for r in multi[:25]]
    lines += ["", "--- no same-fuel conversion (cannot patch) ---"]
    lines += ["  %r" % (r,) for r in missing[:25]]
    if non_scalar_emissions:
        lines += ["", "--- non-scalar emission values ---"]
        lines += ["  %r" % (r,) for r in non_scalar_emissions[:25]]

    routes = sorted(set(u.rsplit("_", 1)[0] for _e, u, _f, _c in emissions))
    lines += ["", "--- distinct routes (%d) ---" % len(routes), "  " + ", ".join(routes)]

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines[:20]))
    print("\nfull report -> %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else str(DEFAULT_DB)))
