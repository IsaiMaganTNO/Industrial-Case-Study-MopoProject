"""Insert a 2040-01-01 point (= the 2041 value) into every yearly milestone series.

SpineOpt evaluates the 2040 investment slice [2040-01-01, 2050-01-01) as the
mean of the value at the slice start (step: 2030 value) and the points inside
it (2041), i.e. the 2030/2041 midpoint. Adding a 2040-01-01 point equal to the
2041 value makes the 2040 investment slice see the 2041 value. Operational
2040 blocks (calendar 2041) are unaffected.
Scope: time_series/map whose index is exactly the milestone pattern
(2030, 2041, 2050[, 2060]). Biomass step series (2029-12-31...) and the
temporal_block map are left alone.
Usage: patch_restamp_2041.py SRC DST [--dry-run]
"""
import sys, shutil, os, numpy as np
from spinedb_api import DatabaseMapping, from_database, to_database, TimeSeriesVariableResolution, Map
src, dst = sys.argv[1], sys.argv[2]; dry = "--dry-run" in sys.argv
PAT = {("2030-01-01","2041-01-01","2050-01-01","2060-01-01"), ("2030-01-01","2041-01-01","2050-01-01")}
if not dry:
    if os.path.exists(dst): sys.exit(f"{dst} exists")
    shutil.copy(src, dst)
db = "sqlite:///" + (src if dry else dst).replace("\\", "/")
n = 0; skipped = 0; byp = {}
with DatabaseMapping(db) as m:
    for v in m.get_parameter_value_items():
        if v["type"] not in ("time_series", "map") or v["entity_class_name"] == "temporal_block": continue
        x = from_database(v["value"], v["type"])
        idx = [str(i)[:10] for i in x.indexes]
        if "2040-01-01" in idx: skipped += 1; continue
        if tuple(idx) not in PAT: continue
        k = idx.index("2041-01-01"); vals = list(x.values)
        if not all(isinstance(y, (int, float, np.floating)) for y in vals): continue
        if isinstance(x, TimeSeriesVariableResolution):
            ni = list(x.indexes); ni.insert(k, np.datetime64("2040-01-01T00:00:00"))
            vals.insert(k, vals[k])
            nx = TimeSeriesVariableResolution(np.array(ni, dtype="datetime64[s]"), np.array(vals, dtype=float), x.ignore_year, x.repeat, index_name=x.index_name)
        else:
            ni = list(x.indexes); ni.insert(k, type(ni[k])("2040-01-01T00:00:00")); vals.insert(k, vals[k])
            nx = Map(ni, vals, index_name=x.index_name)
        n += 1; byp[v["parameter_definition_name"]] = byp.get(v["parameter_definition_name"], 0) + 1
        if not dry:
            val, typ = to_database(nx)
            m.update_item("parameter_value", id=v["id"], value=val, type=typ)
    print("patched", n, "already-2040", skipped); [print(" ", p, c) for p, c in sorted(byp.items())]
    if not dry: m.commit_session("restamp 2041 -> add 2040-01-01 point")
