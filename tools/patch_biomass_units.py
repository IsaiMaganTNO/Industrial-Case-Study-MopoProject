r"""Fix the biomass annual-potential UNIT MISMATCH in a SpineOpt model DB.

THE BUG
-------
`storage_investment_count_max_cumulative` on the 17 `biomass-stock_*` nodes is
authored with the EU-case ANNUAL biomass potential (e.g. BEC1 = 1088.0673).
SpineOpt reads that number as a PER-AVERAGE-DAY allowance, so the model gets
365 years of biomass every year.

WHY PER-AVERAGE-DAY: with representative periods, the long-term storage
trajectory constraint (constraint_node_state_longterm_trajectory.jl) is

    lt[t_after] = lt[t_before] + sum_blk coef[blk] * (state[last] - state[first])

and the coefficients in `representative_blocks_by_period` are weight/365 --
verified exactly: [108.493, 154.000, 102.507] / 365 = [0.29724, 0.42192, 0.28084],
which sum to 1.0. So one unit of `max_cumulative` buys one unit on an AVERAGE
DAY, i.e. 365 units per year.

EVIDENCE THIS IS THE RIGHT READING
----------------------------------
1. Closed loop. Predicted annual use = 365 * state_max * max_cumulative
   = 365 * 1.0 * 1088.0673 = 397,144.6. Measured (3rep, BEC1, 2050, weighted)
   = 397,144.6. Ratio 1.000000.
2. The `atmosphere` node in the SAME model is authored CORRECTLY, in exactly
   these units: annual CO2 budget 165.4 is stored as 165.4/365 =
   0.45315068493150684, matching the DB value to 17 significant figures. Its
   measured weighted 2030 net emissions come to exactly 165,400.0.
3. Non-binding nodes are predicted too, not just saturated ones: NLC5 uses
   71.9% of its theoretical maximum.

WHAT THIS SCRIPT DOES
---------------------
Divides the three biomass stock-sizing parameters by --divisor (default 365):
    storage_investment_count_max_cumulative
    storage_investment_count_initial_cumulative
    storage_investment_count_fix_cumulative
All three are scaled TOGETHER and by the SAME factor, so the tank stays
internally consistent (fix == initial == max, as authored). `storage_state_fix`
is a STATE (a level, in the same units as the tank) and is scaled too.

`storage_state_max` is deliberately NOT touched: it is a multiplier on the tank,
not a quantity.

SEASONAL FLEXIBILITY IS PRESERVED. `node_state` (within representative days) and
`node_state_longterm` (between milestones) live on DISJOINT timestamps. The
annual restriction is the pure sum  sum_d weight_d * drain_d <= C, with no
per-day term, so winter and summer days may drain by different amounts.

USAGE
    .\.venv\Scripts\python.exe tools\patch_biomass_units.py --in SRC.sqlite --out DST.sqlite
    ... --divisor 365            (default)
    ... --dry-run                (report only, write nothing)
"""
from __future__ import annotations
import argparse
import os
import shutil
import sys

from spinedb_api import DatabaseMapping
from spinedb_api.parameter_value import from_database, to_database

PREFIX = "biomass-stock_"

# Quantities measured in "tank units". All are scaled by the same divisor.
SCALE_SCALAR = (
    "storage_investment_count_max_cumulative",
    "storage_investment_count_initial_cumulative",
    "storage_investment_count_fix_cumulative",
)
SCALE_SERIES = ("storage_state_fix",)

# NOT scaled: storage_state_max is a multiplier, not a quantity.
LEAVE = ("storage_state_max", "storage_active", "storage_longterm_active",
         "storage_investment_count_fix_new")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="src", required=True)
    ap.add_argument("--out", dest="dst", required=True)
    ap.add_argument("--divisor", type=float, default=365.0)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if a.divisor <= 0:
        print("divisor must be > 0")
        return 2
    if not os.path.exists(a.src):
        print("no such file: " + a.src)
        return 2

    if not a.dry_run:
        if os.path.exists(a.dst):
            print("refusing to overwrite existing " + a.dst)
            return 2
        shutil.copyfile(a.src, a.dst)
        target = a.dst
    else:
        target = a.src

    n_scalar = n_series = 0
    nodes = set()
    with DatabaseMapping("sqlite:///" + os.path.abspath(target)) as db:
        for v in db.get_parameter_value_items():
            if v["entity_class_name"] != "node":
                continue
            name = str(v["entity_name"])
            if not name.startswith(PREFIX):
                continue
            pn = v["parameter_definition_name"]
            val = from_database(v["value"], v["type"])

            if pn in SCALE_SCALAR:
                old = float(getattr(val, "value", val))
                new = old / a.divisor
                nodes.add(name)
                n_scalar += 1
                if n_scalar <= 6:
                    print("  %-22s %-44s %14.4f -> %14.8f"
                          % (name, pn, old, new))
                if not a.dry_run:
                    nv, nt = to_database(new)
                    db.update_item("parameter_value", id=v["id"], value=nv, type=nt)

            elif pn in SCALE_SERIES:
                if not hasattr(val, "indexes"):
                    continue
                vals = []
                for x in val.values:
                    x = float(x)
                    vals.append(x if x != x else x / a.divisor)  # keep NaN as NaN
                new_series = type(val)(list(val.indexes), vals,
                                       getattr(val, "ignore_year", False),
                                       getattr(val, "repeat", False))
                n_series += 1
                if not a.dry_run:
                    nv, nt = to_database(new_series)
                    db.update_item("parameter_value", id=v["id"], value=nv, type=nt)

        if not a.dry_run:
            db.commit_session("scale biomass stock units by 1/%g" % a.divisor)

    print("")
    print("nodes touched        : %d  (expect 17)" % len(nodes))
    print("scalar rows scaled   : %d  (expect 153 = 17 nodes x 3 alternatives x 3 params)"
          % n_scalar)
    print("state_fix rows scaled: %d  (expect 51 = 17 nodes x 3 alternatives)" % n_series)
    print("divisor              : %g" % a.divisor)
    print("mode                 : %s" % ("DRY RUN (nothing written)" if a.dry_run else "written to " + a.dst))
    return 0


if __name__ == "__main__":
    sys.exit(main())
