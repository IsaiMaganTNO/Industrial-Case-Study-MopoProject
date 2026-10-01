"""Static validation of the CO2 route-emission fix.

Read-only. Run this against a freshly built model DB BEFORE committing to a
multi-hour solve.

Usage:
    python tools/validate_co2_fix.py <model_db.sqlite>

Exits non-zero if any check fails.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
XLSX = ROOT / "data" / "Industry" / "technology_catalogue_ind_nuts0_nuts3.xlsx"
TOL = 1e-6

failures: list[str] = []
notes: list[str] = []


def check(ok: bool, label: str, detail: str = "") -> None:
    mark = "PASS" if ok else "FAIL"
    line = f"  [{mark}] {label}"
    if detail:
        line += f"  ({detail})"
    print(line)
    if not ok:
        failures.append(label)


def atmosphere_ratios(con: sqlite3.Connection) -> dict[str, float]:
    """unit name -> emission ratio to atmosphere (output side only)."""
    rows = con.execute(
        """
        SELECT e.id, pv.value
        FROM parameter_value pv
        JOIN parameter_definition pd ON pd.id = pv.parameter_definition_id
        JOIN entity e ON e.id = pv.entity_id
        WHERE pd.name = 'flow_ratio_equality_coefficient'
          AND e.name LIKE '%atmosphere%'
        """
    ).fetchall()

    out: dict[str, float] = {}
    for eid, raw in rows:
        flat: list[str] = []
        for (el_name,) in con.execute(
            """
            SELECT el.name FROM entity_element ee
            JOIN entity el ON el.id = ee.element_id
            WHERE ee.entity_id = ? ORDER BY ee.position
            """,
            (eid,),
        ):
            flat.extend(
                r[0]
                for r in con.execute(
                    """
                    SELECT el.name FROM entity_element ee
                    JOIN entity el ON el.id = ee.element_id
                    WHERE ee.entity_id = (SELECT id FROM entity WHERE name = ?)
                    ORDER BY ee.position
                    """,
                    (el_name,),
                )
            )        # emission rows are those whose OUTPUT node is atmosphere
        if len(flat) == 4 and flat[1] == "atmosphere":
            try:
                out[flat[0]] = float(raw)
            except (TypeError, ValueError):
                notes.append(f"non-scalar atmosphere ratio on {flat[0]}: {raw!r}")
    return out


def _flat(con: sqlite3.Connection, eid: int) -> list[str]:
    out: list[str] = []
    for (el_name,) in con.execute(
        "SELECT el.name FROM entity_element ee JOIN entity el ON el.id = ee.element_id "
        "WHERE ee.entity_id = ? ORDER BY ee.position",
        (eid,),
    ):
        out.extend(
            r[0]
            for r in con.execute(
                "SELECT el.name FROM entity_element ee JOIN entity el ON el.id = ee.element_id "
                "WHERE ee.entity_id = (SELECT id FROM entity WHERE name = ?) ORDER BY ee.position",
                (el_name,),
            )
        )
    return out


def scale_factors(con: sqlite3.Connection) -> dict[str, float]:
    """unit -> conversion rate from the SAME fuel that feeds its atmosphere row.

    The emission coefficient can be stored in either of two conventions:

      * output-keyed  -> coefficient equals the raw source emission factor
      * input-keyed   -> coefficient equals source factor * conversion rate

    This returns the conversion rate so both conventions can be accepted.
    """
    rows = con.execute(
        """
        SELECT e.id, pv.value
        FROM parameter_value pv
        JOIN parameter_definition pd ON pd.id = pv.parameter_definition_id
        JOIN entity e ON e.id = pv.entity_id
        WHERE pd.name = 'flow_ratio_equality_coefficient'
        """
    ).fetchall()

    emission_fuel: dict[str, str] = {}
    conv: dict[tuple[str, str], list[float]] = {}
    for eid, raw in rows:
        flat = _flat(con, eid)
        if len(flat) != 4:
            continue
        unit, out_node, in_node = flat[0], flat[1], flat[2]
        try:
            val = float(raw)
        except (TypeError, ValueError):
            continue
        if out_node == "atmosphere":
            emission_fuel[unit] = in_node
        elif not (out_node == "CO2" or out_node.startswith(("CO2_", "CO2-"))):
            conv.setdefault((unit, in_node), []).append(val)

    out: dict[str, float] = {}
    for unit, fuel in emission_fuel.items():
        cands = conv.get((unit, fuel), [])
        if len(cands) == 1:
            out[unit] = cands[0]
    return out


def main(db_path: str) -> int:
    print(f"model db : {db_path}")
    print(f"source   : {XLSX.name}")
    print()

    con = sqlite3.connect(db_path)
    ratios = atmosphere_ratios(con)

    xl = pd.ExcelFile(XLSX)
    emi = xl.parse("ind_process_routes_co2_emission")

    # Year headers may be read as int or str depending on the engine/version.
    year_col = next(
        (c for c in emi.columns if str(c).strip() == "2030"), None
    )
    if year_col is None:
        print(f"  !! no 2030 column in emission sheet; columns = {list(emi.columns)}")
        return 2

    expected = {
        str(ind): float(val)
        for ind, val in zip(emi["Industry"], emi[year_col])
    }

    FUEL_VALUES = {0.35, 0.30, 0.26, 0.20}
    scales = scale_factors(con)

    def matches(unit: str, val: float, want: float) -> tuple[bool, str]:
        """Accept the raw source factor (output-keyed) or factor*rate (input-keyed)."""
        if abs(val - want) < TOL:
            return True, "output-keyed"
        rate = scales.get(unit)
        if rate is not None and abs(val - want * rate) < max(TOL, abs(want * rate) * 1e-6):
            return True, f"input-keyed (x{rate:g})"
        return False, "no convention matches"

    print("=== 1. refinery routes carry route-specific values ===")
    for route, want in (("REF-SMR", 0.019), ("REF-SMR-MEA", 0.002), ("REF(H2)", 0.016)):
        got = {u: v for u, v in ratios.items() if u.rsplit("_", 1)[0] == route}
        if not got:
            check(False, f"{route} has an atmosphere ratio", "no units found")
            continue
        results = [matches(u, v, want) for u, v in got.items()]
        ok = all(r[0] for r in results)
        how = results[0][1]
        check(
            ok,
            f"{route} == {want}",
            f"found {sorted(set(got.values()))} [{how}]",
        )

    print()
    print("=== 2. BECCS routes survive with NEGATIVE values ===")
    for route in ("CEM2-(BMW)MEA", "CEM2-(BMW)CaL"):
        want = expected.get(route)
        got = {u: v for u, v in ratios.items() if u.rsplit("_", 1)[0] == route}
        if want is None:
            notes.append(f"{route} not in source sheet")
            continue
        if not got:
            notes.append(
                f"{route} has NO atmosphere row (source says {want}) "
                "- negative emissions are missing from the model"
            )
            continue
        unit, val = next(iter(got.items()))
        ok, how = matches(unit, val, want)
        check(val < 0 and ok, f"{route} == {want}", f"found {val} [{how}]")

    print()
    print("=== 3. no unit keeps a bare fuel-content ratio when route data exists ===")
    routes = set(expected)
    offenders = [
        u
        for u, v in ratios.items()
        if u.rsplit("_", 1)[0] in routes and round(v, 2) in FUEL_VALUES
    ]
    check(
        not offenders,
        "no route-backed unit still on a fuel coefficient",
        f"{len(offenders)} offenders e.g. {offenders[:5]}",
    )

    print()
    print("=== 4. fuel fallback preserved for units with no route data ===")
    fallback = [u for u in ratios if u.rsplit("_", 1)[0] not in routes]
    check(len(fallback) > 0, "some units still use the fuel fallback", f"{len(fallback)} units")

    print()
    print("=== 5. no duplicate atmosphere ratios per unit ===")
    dupes = con.execute(
        """
        SELECT e.name, COUNT(*) c
        FROM parameter_value pv
        JOIN parameter_definition pd ON pd.id = pv.parameter_definition_id
        JOIN entity e ON e.id = pv.entity_id
        WHERE pd.name = 'flow_ratio_equality_coefficient' AND e.name LIKE '%atmosphere%'
        GROUP BY e.name HAVING c > 1
        """
    ).fetchall()
    check(not dupes, "no duplicated atmosphere ratio rows", f"{len(dupes)} duplicates")

    con.close()

    print()
    if notes:
        print("notes:")
        for n in notes:
            print(f"  - {n}")
        print()

    if failures:
        print(f"RESULT: {len(failures)} CHECK(S) FAILED")
        for f in failures:
            print(f"  - {f}")
        print()
        print("Do NOT start a long solve. Revert with: pwsh tools/revert_co2_fix.ps1")
        return 1

    print("RESULT: all checks passed - safe to solve")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
