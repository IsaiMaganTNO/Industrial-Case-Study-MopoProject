"""Create a TINY test model from the full SpineOpt input DB.

Problem it solves
-----------------
The three `operations_y*` temporal blocks each span a FULL YEAR at `1h`
resolution (2030-2031, 2041-2042, 2050-2051), i.e. 3 x 8760 = 26,280
operational timesteps - even though the 6 representative blocks are only
1 hour each. That is why the build ran for 15-30 CPU-minutes.

What this does
--------------
Coarsens ONLY the `operations_y*` resolution from `1h` to `8760h`, so each
operational block becomes a SINGLE timestep covering its year, and truncates
`representative_blocks_by_period` from 8760 entries to the 1 entry that
remains meaningful.

Why coarsen rather than shorten the span
----------------------------------------
`block_start` of the operations blocks defines the INVESTMENT PERIOD
boundaries used for annuity/discounting maths in
scenario_run.py:investment_cost_update(). Moving or deleting those dates would
silently change the economics. Coarsening the resolution leaves every date,
entity, alternative and the total weight (8760 h/yr) untouched.

Writes to a COPY. The original DB is never modified.
"""
import shutil, sys
from pathlib import Path
from spinedb_api import DatabaseMapping, to_database

SRC = Path(".spinetoolbox/items/final_spineopt_model/Final_SpineOpt_Model.sqlite")
DST = Path("checkpoints/Final_SpineOpt_Model.tiny.sqlite")

DST.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(SRC, DST)
print(f"copied -> {DST}")

with DatabaseMapping(f"sqlite:///{DST.as_posix()}") as db:
    # 1. coarsen operations block resolution: 1h -> 8760h (one timestep per year)
    for pv in list(db.get_parameter_value_items(entity_class_name="temporal_block",
                                                parameter_definition_name="resolution")):
        name = pv["entity_byname"][0]
        if not name.startswith("operations"):
            continue
        val, typ = to_database({"type": "duration", "data": "8760h"})
        db.update_item("parameter_value", id=pv["id"], value=val, type=typ)
        print(f"  {name}: resolution 1h -> 8760h")

    # 2. Collapse the period->representative weight map to a single entry.
    #
    #    These coefficients are SHARES OF THE REPRESENTED INTERVAL, not hours.
    #    SpineOpt enforces this in temporal_structure.jl
    #    (_blocks_and_mapping_by_represented_interval):
    #        "sum of coefficients for <interval> from '<block>' must be 1"
    #    so each entry must sum to 1.0. The original 8760 hourly entries each
    #    already sum to 1; collapsing to one entry therefore means AVERAGING
    #    the per-representative shares over the year, not summing them.
    #    (Summing gives 8760 and SpineOpt rejects it outright - which is how
    #    this was caught.)
    for pv in list(db.get_parameter_value_items(
            entity_class_name="temporal_block",
            parameter_definition_name="representative_blocks_by_period")):
        m = pv["parsed_value"]
        idx = list(m.indexes)
        n_rep = len(m.values[0].values)
        totals = [0.0] * n_rep
        for v in m.values:
            for i, w in enumerate(v.values):
                totals[i] += w
        shares = [t / len(idx) for t in totals]          # average share over the year
        s = sum(shares)
        shares = [x / s for x in shares]                 # normalise to exactly 1.0
        data = [(str(idx[0]), {"type": "array", "value_type": "float", "data": shares})]
        new_map = {"type": "map", "index_type": "date_time", "index_name": "t", "data": data}
        val, typ = to_database(new_map)
        db.update_item("parameter_value", id=pv["id"], value=val, type=typ)
        print(f"  {pv['entity_byname'][0]} [{pv['alternative_name']}]: "
              f"map {len(idx)} -> 1 entry, coefficient sum {round(sum(shares), 6)}")

    db.commit_session("Tiny test model: coarsen operations blocks to one timestep per year")

print("\nTiny model written. Operational timesteps: 3 (was 26,280)")
print("Representative timesteps: 6 (unchanged)")
