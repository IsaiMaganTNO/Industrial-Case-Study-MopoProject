# filepath: c:\Users\maganih\Documents\github-repos\Industrial-Case-Study-MopoProject\tools\patch_biomass_stock.py
r"""Stop the biomass stock from refilling on every representative day.

THE DEFECT
----------
`biomass-stock_*` are SpineOpt storage nodes holding each region's annual
biomass availability (already reduced to 50% of technical potential upstream by
scenario_run.biomass_limitations, matching the EU case).

Measured from run_logs/3rep_gurobi_solve.out results, node_state for
biomass-stock_BEC1:

    2030-01-11T23:59   1,088.0673   <- full
    2030-01-12T00:00   1,041.9423
    ... monotonic drawdown over 24 h ...
    2050-08-19T23:00       0.0000   <- exactly empty

The stock is emptied EXACTLY to the cap within each representative day
(daily_total / cap = 1.000000 to 16 s.f.), and `storage_state_fix` then refills
it to full before the next one. Each representative day is weighted to stand for
~108-154 real days, so the effective ANNUAL availability is 365x the intended
cap:

    region   annual use (weighted)        cap      ratio
    BEC1               397,144.6      1,088.1   36,500%
    NLC4               608,224.0      1,689.9   36,500%
    TOTAL 2050       2,129,209.3     24,899.4    8,551%

36,500% = exactly 365x. Same root cause as the atmosphere CO2 cap
(docs/TIME_REPRESENTATION.md section 7): make_tiny_model.py coarsens
`operations_y*` from 1h to 8760h, so cumulative budgets are drawn down once per
representative period instead of 365 times per year.

WHY atmosphere WORKS AND BIOMASS DOES NOT
-----------------------------------------
`atmosphere` has NO storage_state_fix, so its state accumulates across the whole
horizon and ends at 0.000000 - the cap binds cumulatively, as intended.
`biomass-stock_*` has storage_state_fix AND storage_investment_count_fix_cumulative,
which re-pin it every milestone. Same coarsening, opposite handling.

This corrects docs/TIME_REPRESENTATION.md section 7.4, which said biomass was
"already per-period -> leave" on the basis of "1.5 days of headroom". 1.5 days
of headroom is exactly what a per-day-binding budget looks like; the doc
mistook the symptom for authoring intent.

THE FIX (option 1 - structural)
-------------------------------
1. REMOVE `storage_state_fix`                       (the daily/milestone refill)
2. REMOVE `storage_investment_count_fix_cumulative` (the second pin)
   Neither is present on `atmosphere`, which behaves correctly.
3. SCALE `storage_investment_count_max_cumulative` and
   `storage_investment_count_initial_cumulative` by HORIZON_YEARS (default 10).
   The authored cap is ANNUAL availability. Without the refill the stock must
   now cover its entire milestone, and each milestone represents 10 years. Skip
   this and we swing from 365x too loose to 10x too tight.

   *** THE x10 IS A GUESS. TREAT IT AS PROVISIONAL. ***

   It is NOT verified against any specification, upstream data file, or the EU
   case. It rests on one inference: that the authored cap is ANNUAL
   availability and that each milestone stands for 10 years. Neither half of
   that has been confirmed.

   Reasons it may be wrong:
     * the cap may already be a milestone/horizon figure, in which case x10
       over-supplies biomass by 10x and this patch fixes nothing;
     * milestones may not represent exactly 10 years each (2030/2040/2050 with
       model_end 2060 suggests 10, but `years_represented` is ABSENT from the
       model, so this is read off the milestone spacing, not a parameter);
     * availability may legitimately differ per milestone (rising/falling
       biomass potential), which a single flat multiplier cannot express.

   The structural half of this patch - removing the per-period refill - is
   well-evidenced and is the actual defect. The x10 is a stop-gap so the fix
   can be TESTED without swinging to an obviously over-tight limit. It is a
   separate decision from the removal and should be revisited on its own.

   PREFERRED RESOLUTION: trace where biomass availability is authored upstream
   (data-pipelines/europe/_ines-builder/ines_target.py:add_biomass_production,
   and the biomass_db source) and replace this multiplier with the real
   per-milestone figures. Until then, report any run made with it as
   "biomass availability scaled by an unverified factor of 10".

   Use --horizon-years to change it, or --horizon-years 1 to omit it entirely
   and test the refill removal in isolation.

storage_state_max is deliberately LEFT ALONE. It bounds the state variable, not
the budget, and changing both at once would make attribution impossible.

WARNING - FAILURE IS SILENT
---------------------------
`atmosphere` carries balance_penalty = 10000.0, so a biomass limit that is too
TIGHT does not report infeasible. The model buys its way out and still reports
OPTIMAL. After solving, check FIRST:

    objective_objective_penalties   # must be 0.00

A non-zero value means the limit was violated and paid for, and the objective is
meaningless however healthy the termination status looks.

USAGE
-----
    .\.venv\Scripts\python.exe tools\patch_biomass_stock.py --db <in> --check
    .\.venv\Scripts\python.exe tools\patch_biomass_stock.py --db <in> --out <out>

Writes a NEW database; the input is never modified.

IDEMPOTENCY
-----------
Not idempotent. It refuses to run if storage_state_fix is already absent, so a
double-run is an error rather than silent corruption.
"""  # noqa: W605

from __future__ import annotations

import argparse
import os
import shutil
import sys

from spinedb_api import DatabaseMapping, from_database, to_database

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NODE_PREFIX = "biomass-stock"
REMOVE = ("storage_state_fix", "storage_investment_count_fix_cumulative")
SCALE = ("storage_investment_count_max_cumulative",
         "storage_investment_count_initial_cumulative")
HORIZON_YEARS = 10.0


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Remove the biomass-stock refill and scale caps to the milestone.")
    ap.add_argument("--db", required=True, help="input model SQLite")
    ap.add_argument("--out", help="output SQLite (required unless --check)")
    ap.add_argument("--check", action="store_true",
                    help="report current state without modifying anything")
    ap.add_argument("--horizon-years", type=float, default=HORIZON_YEARS,
                    help="scale factor for the caps (default 10; use 1 to skip)")
    a = ap.parse_args()

    if not os.path.isfile(a.db):
        sys.exit("not found: %s" % a.db)

    if a.check:
        target = a.db
    else:
        if not a.out:
            sys.exit("--out is required unless --check")
        if os.path.exists(a.out):
            sys.exit("refusing to overwrite existing file: %s" % a.out)
        print("copying %s\n     -> %s" % (a.db, a.out))
        shutil.copy2(a.db, a.out)
        target = a.out

    url = "sqlite:///" + os.path.abspath(target).replace("\\", "/")
    with DatabaseMapping(url) as db:
        items = [pv for pv in db.get_parameter_value_items()
                 if pv["entity_class_name"] == "node"
                 and pv["entity_byname"]
                 and str(pv["entity_byname"][0]).startswith(NODE_PREFIX)]
        if not items:
            sys.exit("no `%s*` parameters found in %s" % (NODE_PREFIX, target))

        to_remove = [pv for pv in items
                     if pv["parameter_definition_name"] in REMOVE]
        to_scale = [pv for pv in items
                    if pv["parameter_definition_name"] in SCALE]

        nodes = sorted({pv["entity_byname"][0] for pv in items})
        print("\ndatabase : %s" % target)
        print("nodes    : %d" % len(nodes))
        print("to remove: %d parameter values (%s)" % (len(to_remove), ", ".join(REMOVE)))
        print("to scale : %d parameter values x %.0f" % (len(to_scale), a.horizon_years))
        if a.horizon_years != 1.0:
            print("")
            print("  *** WARNING: the x%.0f cap scaling is an UNVERIFIED GUESS. ***"
                  % a.horizon_years)
            print("  It assumes the authored cap is ANNUAL and that each milestone")
            print("  represents %.0f years. `years_represented` is NOT in the model, so"
                  % a.horizon_years)
            print("  this is inferred from milestone spacing alone. Any run made with")
            print("  it must be reported as 'biomass scaled by an unverified factor'.")
            print("  Use --horizon-years 1 to test the refill removal in isolation.")

        if not to_remove:
            print("\nstatus: ALREADY PATCHED (no %s present)" % REMOVE[0])
            if not a.check:
                sys.exit("refusing to patch a model that looks already patched")
            return

        # Show medium_bio (the alternative the active scenario uses) before/after.
        print("\n  %-24s %14s %14s" % ("node", "cap(medium)", "-> new"))
        for pv in sorted(to_scale, key=lambda p: str(p["entity_byname"][0])):
            if pv["alternative_name"] != "medium_bio":
                continue
            if pv["parameter_definition_name"] != SCALE[0]:
                continue
            old = float(from_database(pv["value"], pv["type"]))
            print("  %-24s %14s %14s"
                  % (pv["entity_byname"][0], "{:,.2f}".format(old),
                     "{:,.2f}".format(old * a.horizon_years)))

        if a.check:
            print("\nstatus: NOT patched")
            return

        for pv in to_remove:
            db.remove_item("parameter_value", pv["id"])
        print("\nremoved %d pinning parameter values" % len(to_remove))

        if a.horizon_years != 1.0:
            for pv in to_scale:
                new = float(from_database(pv["value"], pv["type"])) * a.horizon_years
                dbv, dbt = to_database(new)
                db.update_parameter_value_item(id=pv["id"], value=dbv, type=dbt)
            print("scaled  %d cap values by %.0f" % (len(to_scale), a.horizon_years))

        db.commit_session(
            "biomass-stock: remove per-period refill (storage_state_fix, "
            "fix_cumulative); caps scaled x%.0f (UNVERIFIED GUESS - assumes "
            "annual cap and %.0f-year milestones; see tools/patch_biomass_stock.py)"
            % (a.horizon_years, a.horizon_years))
        print("\nwrote %s" % target)
        print("\nAFTER SOLVING, CHECK objective_objective_penalties == 0.00 FIRST.")


if __name__ == "__main__":
    main()
