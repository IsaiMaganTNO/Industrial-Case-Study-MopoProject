"""Divide CO2 storage-site caps by 365 (representative-period scaling).

Data (CCS_storage_scenarios_mopo.xlsx) is in Mtpa, cumulative per year.
ines_target.py writes storages_fix_cumulative = Mtpa*1000, storage_capacity 1000
-> SpineOpt storage_investment_count_fix_cumulative = Mtpa units x 1000.
The long-term storage state increments by (annual flow)/365 per year (verified:
ATUK031 2049->2050 rise 370.4 = 135.2 Mt/365), so the cap must be /365, exactly
like the atmosphere budget (patch_co2_cap_div365.py). See
docs/FINDING_co2_storage_cap_365x.md.

Scope: storage_investment_count_fix_cumulative on nodes CO2-storage-*, all
alternatives (low/medium/high_CO2). Refuses to run twice (max value < 1 => done).
Usage: patch_co2_storage_div365.py SRC DST [--dry-run]
"""
import argparse, shutil, sqlite3, json, sys
DIV = 365.0
ap = argparse.ArgumentParser(); ap.add_argument("src"); ap.add_argument("dst")
ap.add_argument("--dry-run", action="store_true"); a = ap.parse_args()
if not a.dry_run: shutil.copyfile(a.src, a.dst)
con = sqlite3.connect(a.src if a.dry_run else a.dst)
def guard():
    return con.execute("""select count(*), coalesce(sum(cast(pv.value as text)+0),0) from parameter_value pv
      join parameter_definition pd on pd.id=pv.parameter_definition_id join entity e on e.id=pv.entity_id
      join entity_class ec on ec.id=e.class_id where pd.name='investment_count_initial_cumulative' and ec.name='connection'""").fetchone()
g0 = guard()
rows = con.execute("""select pv.id, e.name, a.name, cast(pv.value as text), pv.type from parameter_value pv
  join parameter_definition pd on pd.id=pv.parameter_definition_id join entity e on e.id=pv.entity_id
  join alternative a on a.id=pv.alternative_id
  where pd.name='storage_investment_count_fix_cumulative' and e.name like 'CO2-storage-%'""").fetchall()
assert rows, "no CO2-storage cap rows found"
allv = [float(v) for _,_,_,t,_ in rows for v in json.loads(t)["data"].values() if v is not None]
if max(allv) < 1.0: sys.exit("ABORT: max cap %.4f < 1 - already divided?" % max(allv))
new = {}
for pid, n, alt, t, typ in rows:
    o = json.loads(t); o["data"] = {k: (None if v is None else float(v)/DIV) for k, v in o["data"].items()}
    new[pid] = o
    if alt == "high_CO2": print("%-22s %-10s %s" % (n, alt, {k[:4]: round(v*DIV,2) for k, v in o["data"].items()}), "->", {k[:4]: round(v,4) for k, v in o["data"].items()})
print("rows: %d" % len(rows))
if a.dry_run: print("DRY RUN"); sys.exit()
for pid, o in new.items():
    con.execute("update parameter_value set value=? where id=?", (sqlite3.Binary(json.dumps(o).encode()), pid))
con.commit()
for pid, o in new.items():
    rt = json.loads(con.execute("select cast(value as text) from parameter_value where id=?", (pid,)).fetchone()[0])["data"]
    assert all((rt[k] is None and v is None) or abs(rt[k]-v) < 1e-12 for k, v in o["data"].items())
g1 = guard(); assert g0[0] == g1[0] and abs(g0[1]-g1[1]) < 1e-9, "guard changed"
print("GUARD cross-border %d rows sum %.4f unchanged; readback OK; integrity:", g1[0], g1[1], con.execute("pragma integrity_check").fetchone()[0]) if False else None
print("GUARD cross-border %d rows sum %.4f unchanged; readback OK; integrity: %s" % (g1[0], g1[1], con.execute("pragma integrity_check").fetchone()[0]))
print("WROTE", a.dst)
