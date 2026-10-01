"""Rescale the `atmosphere` cumulative CO2 caps for the coarsened tiny model.

WHY THIS IS NEEDED
------------------
tools/make_tiny_model.py coarsens the `operations_y*` blocks from 1h to 8760h,
so each milestone year has ONE operational timestep. A CUMULATIVE budget is
drawn down once per timestep, so after coarsening it is drawn down ONCE PER
YEAR instead of 365 times - leaving the cap 365x too loose.

This fails SILENTLY. The model solves and reports a plausible objective; the
CO2 cap simply never binds. In Run C the `atmosphere` node sat at 965.6 and
1,011.8 against caps of 165.4 and 36.8 (171x and 36x headroom) and nothing
complained, because `atmosphere` carries balance_penalty = 10000.0 and the
violation is absorbed as penalty rather than raised as infeasibility.

Dividing by 365 restores the intended budget: net CO2 then lands on
453.15 / 100.82 / 0.00, matching the caps to 4 decimal places.

See docs/TIME_REPRESENTATION.md section 7 for the full derivation.

WHICH NODES TO PATCH - AND WHICH TO LEAVE ALONE
-----------------------------------------------
Only `atmosphere`. Effective budget is `cap x storage_state_max`, and state_max
differs between nodes (section 7.4):

    node                      cap    state_max   headroom     verdict
    atmosphere 2030        165.40         1000   171 days     annual -> RESCALE
    atmosphere 2040         36.80         1000    36 days     annual -> RESCALE
    biomass-stock_BEC1   1,088.07            1   1.5 days     per-period -> leave
    CH4-geo-formation    1,103.75            1    10 days     per-period -> leave
    CO2-storage-NSNL031    10,000         1000   11,623 days  non-binding -> leave

Rule of thumb:
  * state_max = 1000 AND tens-to-hundreds of days of headroom
        -> an ANNUAL budget drawn down once instead of 365 times. Rescale.
  * state_max = 1 AND a handful of days of headroom
        -> already authored per-period. Leave alone.

USAGE
-----
Run AFTER make_tiny_model.py and BEFORE solving:

    .\.venv\Scripts\python.exe tools\patch_co2_caps.py
    .\.venv\Scripts\python.exe tools\patch_co2_caps.py --db <path> --check

IDEMPOTENCY
-----------
NOT idempotent - running twice divides by 365 twice. It refuses to run when the
values already look patched, so a double-run is an error, not silent corruption.
"""

from __future__ import annotations

import argparse
import os
import sys

from spinedb_api import DatabaseMapping, from_database, to_database
from spinedb_api.parameter_value import TimeSeriesVariableResolution

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB = os.path.join(REPO, "checkpoints", "Final_SpineOpt_Model.tiny.sqlite")

DIVISOR = 365.0
NODE = "atmosphere"
PARAMS = (
    "storage_investment_count_max_cumulative",
    "storage_investment_count_initial_cumulative",
)

# Unpatched caps are O(100); patched caps are O(0.1).
ALREADY_PATCHED_BELOW = 1.0


def _values(val):
    """Plain list of floats for either a time series or a scalar."""
    if isinstance(val, TimeSeriesVariableResolution):
        return [float(x) for x in val.values]
    return [float(val)]


def main() -> None:
    ap = argparse.ArgumentParser(description="Rescale atmosphere CO2 caps by 1/365.")
    ap.add_argument("--db", default=DEFAULT_DB, help="tiny model SQLite path")
    ap.add_argument("--check", action="store_true",
                    help="report values without modifying the database")
    ap.add_argument("--force", action="store_true",
                    help="patch even if values already look rescaled")
    a = ap.parse_args()

    if not os.path.isfile(a.db):
        sys.exit("not found: %s" % a.db)

    url = "sqlite:///" + os.path.abspath(a.db).replace("\\", "/")
    with DatabaseMapping(url) as db:
        targets = [
            pv for pv in db.get_parameter_value_items()
            if pv["parameter_definition_name"] in PARAMS
            and pv["entity_byname"] == (NODE,)
        ]
        if not targets:
            sys.exit("no `%s` cumulative cap parameters found in %s" % (NODE, a.db))

        highest = max(max(_values(from_database(pv["value"], pv["type"])))
                      for pv in targets)
        looks_patched = highest < ALREADY_PATCHED_BELOW

        print("database: %s" % a.db)
        for pv in targets:
            v = from_database(pv["value"], pv["type"])
            print("  %-46s %s" % (pv["parameter_definition_name"],
                                  [round(x, 8) for x in _values(v)]))

        if a.check:
            print("")
            print("status: %s" % ("PATCHED" if looks_patched else "NOT patched"))
            return

        if looks_patched and not a.force:
            sys.exit(
                "\nREFUSING: values are already <= %.1f, so this model looks "
                "patched.\nRunning again would divide by %.0f a second time. "
                "Use --force only if you are certain."
                % (ALREADY_PATCHED_BELOW, DIVISOR))

        print("")
        print("dividing by %.0f ..." % DIVISOR)
        for pv in targets:
            v = from_database(pv["value"], pv["type"])
            if isinstance(v, TimeSeriesVariableResolution):
                new = TimeSeriesVariableResolution(
                    v.indexes, [x / DIVISOR for x in v.values],
                    v.ignore_year, v.repeat)
            else:
                new = float(v) / DIVISOR
            dbv, dbt = to_database(new)
            db.update_parameter_value_item(id=pv["id"], value=dbv, type=dbt)
            print("  %-46s -> %s" % (pv["parameter_definition_name"],
                                     [round(x, 8) for x in _values(new)]))
        db.commit_session(
            "rescale %s cumulative CO2 caps by 1/%.0f for coarsened operations"
            % (NODE, DIVISOR))
        print("")
        print("done. Now run tools/preflight_check.py before solving.")


if __name__ == "__main__":
    main()
