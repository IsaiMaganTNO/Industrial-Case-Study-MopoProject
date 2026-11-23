"""Rescale biomass-stock caps so the stock balance matches the weighted fuel flow.

THE DEFECT (verified against SpineOpt source, 2026-10-04)
---------------------------------------------------------
SpineOpt debits long-term storage with a DELTA formulation
(src/constraints/constraint_node_state_longterm_trajectory.jl):

    node_state_longterm[t_after]
      = node_state_longterm[t_before]
      + SUM_blk  representative_block_coefficient[t_after, blk]
                 * (node_state[last_t_blk] - node_state[first_t_blk])

In this model `representative_blocks_by_period` coefficients are
[0.276185, 0.436662, 0.287153] and sum to EXACTLY 1.000000.

Verified reproduction, biomass-stock_BEC1 2041:
    1088.07 + (0.276185*(241.73-1088.07)
             + 0.436662*(0.00-843.72)
             + 0.287153*(0.00-922.62))  =  220.97
    observed node_state_longterm 2041    =  220.97   (exact)

So the STOCK is debited for ONE average day's net change, while the FUEL FLOW
is annualised by the representative-day weights (100.807 + 159.382 + 104.811
= 365.000). Measured on biomass-stock_BEC1 -> bio_BEC1 in 2050:

    fuel delivered (weighted) = 397,144.6
    stock debited             =   1,088.07
    ratio                     =     365.0

The energy balance charges a year of fuel; the stock balance charges a day.

THE FIX
-------
Divide the biomass-stock caps by 365 so one stock unit corresponds to one
weighted-annual unit of fuel. This is the SAME correction already applied to
the `atmosphere` CO2 cap in this very database (165.40 -> 0.45315068...,
36.80 -> 0.10082191..., i.e. /365) - see docs/TIME_REPRESENTATION.md section 7.

Target after patch (NL+BE, medium_bio):
    24,899.4 / 365 = 68.2 stock units  ==  ~86.2 TWh/yr annual_production
                                           x 0.5 biomass_potential_realistic
                                           ~= 43 TWh/yr intended availability

NOTE ON tools/patch_biomass_stock.py
------------------------------------
That script diagnoses the same 365x symptom but attributes it to
`storage_state_fix` refilling, and "fixes" it by REMOVING the refill and
MULTIPLYING by HORIZON_YEARS=10 (its own docstring flags the x10 as a guess).
That remedy does not address the coefficient normalisation and would leave the
model ~36.5x too loose. This script supersedes it. Do not run both.

WHAT THIS SCRIPT DOES NOT TOUCH
-------------------------------
- cross-border connections (the noxborder experiment is NOT carried over;
  verified group1 xborder initial sum = 26.060, i.e. pristine)
- the atmosphere CO2 cap (already /365 in the source DB)
- retirement pins (467 investment_count_fix_cumulative rows, left as-is)
- CH4-geo-formation (same latent defect but never binds: floors at 90% of full)
"""
from __future__ import annotations
import shutil, sqlite3, sys, json
from pathlib import Path

DIVISOR = 365.0
PARAMS = [
    "storage_investment_count_max_cumulative",
    "storage_investment_count_initial_cumulative",
    "storage_investment_count_fix_cumulative",
    "storage_state_fix",
]

def scale(raw: str, factor: float):
    """Scale a float or a time_series parameter value."""
    txt = raw.decode() if isinstance(raw, (bytes, bytearray)) else str(raw)
    s = txt.strip()
    if s.startswith("{"):
        obj = json.loads(s)
        if obj.get("type") == "time_series":
            d = obj["data"]
            if isinstance(d, dict):
                obj["data"] = {k: (None if v is None else v * factor) for k, v in d.items()}
            else:
                obj["data"] = [[k, (None if v is None else v * factor)] for k, v in d]
            return json.dumps(obj)
        return None
    try:
        return repr(float(s) * factor)
    except ValueError:
        return None

def main() -> None:
    if len(sys.argv) != 3:
        print("usage: patch_biomass_cap_div365.py <src.sqlite> <dst.sqlite>")
        raise SystemExit(2)
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    if not src.exists():
        raise SystemExit(f"missing source: {src}")
    if dst.exists():
        print(f"overwriting {dst}")
    shutil.copy2(src, dst)

    con = sqlite3.connect(dst)
    cur = con.cursor()
    before = after = 0.0
    changed = 0
    for pname in PARAMS:
        rows = cur.execute(
            """SELECT pv.id, e.name, al.name, pv.value
               FROM parameter_value pv
               JOIN parameter_definition pd ON pd.id = pv.parameter_definition_id
               JOIN entity e ON e.id = pv.entity_id
               JOIN alternative al ON al.id = pv.alternative_id
               WHERE pd.name = ? AND e.name LIKE 'biomass-stock|_%' ESCAPE '|'""",
            (pname,),
        ).fetchall()
        for pid, ent, alt, val in rows:
            new = scale(val, 1.0 / DIVISOR)
            if new is None:
                print(f"  SKIP (unhandled type) {pname} {ent} {alt}")
                continue
            if pname == "storage_investment_count_initial_cumulative" and alt == "medium_bio":
                before += float(val)
                after += float(new)
            # SpineOpt stores parameter_value.value as BLOB; writing TEXT makes
            # SpineInterface's parse_db_value fail with a MethodError.
            cur.execute(
                "UPDATE parameter_value SET value = ? WHERE id = ?",
                (sqlite3.Binary(new.encode("utf-8")), pid),
            )
            changed += 1
        print(f"  {pname:46s} {len(rows):3d} rows")
    con.commit()

    # HARD GUARD: every patched row must still be a BLOB, or SpineOpt will throw
    # "unable to parse value of ... MethodError: no method matching parse_db_value"
    bad = cur.execute(
        """SELECT COUNT(*) FROM parameter_value pv
           JOIN parameter_definition pd ON pd.id = pv.parameter_definition_id
           JOIN entity e ON e.id = pv.entity_id
           WHERE pd.name IN (?, ?, ?, ?)
             AND e.name LIKE 'biomass-stock|_%' ESCAPE '|'
             AND typeof(pv.value) != 'blob'""",
        tuple(PARAMS),
    ).fetchone()[0]
    if bad:
        con.close()
        raise SystemExit(f"FATAL: {bad} patched rows are not BLOB - SpineOpt would reject this DB")
    print("  GUARD all patched rows are BLOB: OK")

    # verification
    tot = {}
    for alt, v in cur.execute(
        """SELECT al.name, pv.value FROM parameter_value pv
           JOIN parameter_definition pd ON pd.id = pv.parameter_definition_id
           JOIN entity e ON e.id = pv.entity_id
           JOIN alternative al ON al.id = pv.alternative_id
           WHERE pd.name = 'storage_investment_count_initial_cumulative'
             AND e.name LIKE 'biomass-stock|_%' ESCAPE '|'"""):
        tot[alt] = tot.get(alt, 0.0) + float(v)

    # guard: confirm untouched areas
    xb = 0.0
    for nm, v in cur.execute(
        """SELECT e.name, pv.value FROM parameter_value pv
           JOIN parameter_definition pd ON pd.id = pv.parameter_definition_id
           JOIN entity e ON e.id = pv.entity_id
           WHERE pd.name = 'investment_count_initial_cumulative'"""):
        if "_elec_" in nm:
            a, b = nm.split("_elec_")[0], nm.split("_elec_")[-1]
            if a in ("DE","FR","NO","UK","DK","LU") or b in ("DE","FR","NO","UK","DK","LU"):
                xb += float(v)
    con.close()

    print(f"\n  rows changed: {changed}")
    print(f"  medium_bio total: {before:.1f} -> {after:.1f} (/{DIVISOR:.0f})")
    for a in sorted(tot):
        print(f"    {a:12s} {tot[a]:10.2f}")
    print(f"  GUARD cross-border initial sum = {xb:.3f} (expect 26.060 = untouched)")

if __name__ == "__main__":
    main()
