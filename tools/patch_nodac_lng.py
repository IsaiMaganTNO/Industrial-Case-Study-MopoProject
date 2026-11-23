"""Scenario settings for the 'noDAC + LNG 1.0' runs (2026-10-09, user decision).
1. LNG-terminal_* availability_factor -> 1.0 (reverts the 0.5 from patch_gas_availability.py).
   gas-extraction_NL* stays 0.0 (Groningen closed) - not touched.
2. DAC_* units: investment_count_max_cumulative -> 0.0 (no DAC can be built).
   Aborts if any DAC unit has existing capacity (initial units / number_of_units > 0).
Usage: patch_nodac_lng.py SRC DST [--dry-run]
"""
import argparse, shutil, sqlite3, sys
ap = argparse.ArgumentParser(); ap.add_argument("src"); ap.add_argument("dst")
ap.add_argument("--dry-run", action="store_true"); a = ap.parse_args()
if not a.dry_run: shutil.copyfile(a.src, a.dst)
con = sqlite3.connect(a.src if a.dry_run else a.dst)
def q(sql, *p): return con.execute(sql, p).fetchall()
def guard():
    return q("""select count(*), coalesce(sum(cast(pv.value as text)+0),0) from parameter_value pv
      join parameter_definition pd on pd.id=pv.parameter_definition_id join entity e on e.id=pv.entity_id
      join entity_class ec on ec.id=e.class_id where pd.name='investment_count_initial_cumulative' and ec.name='connection'""")[0]
g0 = guard()
base = "join parameter_definition pd on pd.id=pv.parameter_definition_id join entity e on e.id=pv.entity_id join alternative a on a.id=pv.alternative_id"
lng = q(f"select pv.id,e.name,a.name,cast(pv.value as text) from parameter_value pv {base} where pd.name='availability_factor' and e.name like 'LNG-terminal_%'")
assert lng and all(r[2] == "Base" for r in lng), lng
print("LNG rows: %d, values before %s" % (len(lng), sorted({r[3] for r in lng})))
ex = q(f"select e.name,cast(pv.value as text) from parameter_value pv {base} where e.name like 'DAC_%' and pd.name in ('initial_units_invested_available','number_of_units','investment_count_initial_cumulative','existing_units')")
nz = [r for r in ex if r[1] not in ("0", "0.0")]
if nz: sys.exit("ABORT: DAC has existing capacity: %s" % nz[:5])
dac = q(f"select pv.id,e.name,a.name,cast(pv.value as text) from parameter_value pv {base} where pd.name='investment_count_max_cumulative' and e.name like 'DAC_%'")
units = q("select e.name from entity e join entity_class ec on ec.id=e.class_id where ec.name='unit' and e.name like 'DAC_%'")
assert len(dac) == len(units) and all(r[2] == "Base" for r in dac), (len(dac), len(units))
print("DAC units: %d, max_cumulative before %s" % (len(dac), sorted({r[3] for r in dac})))
if a.dry_run: print("DRY RUN"); sys.exit()
for pid, *_ in lng: con.execute("update parameter_value set value=?, type='float' where id=?", (sqlite3.Binary(b"1.0"), pid))
for pid, *_ in dac: con.execute("update parameter_value set value=?, type='float' where id=?", (sqlite3.Binary(b"0.0"), pid))
con.commit()
assert {r[3] for r in q(f"select pv.id,e.name,a.name,cast(pv.value as text) from parameter_value pv {base} where pd.name='availability_factor' and e.name like 'LNG-terminal_%'")} == {"1.0"}
assert {r[3] for r in q(f"select pv.id,e.name,a.name,cast(pv.value as text) from parameter_value pv {base} where pd.name='investment_count_max_cumulative' and e.name like 'DAC_%'")} == {"0.0"}
ext = q(f"select e.name,cast(pv.value as text) from parameter_value pv {base} where pd.name='availability_factor' and e.name like 'gas-extraction_%'")
print("gas-extraction availability (unchanged):", sorted(set(ext))[:3], "... n=%d" % len(ext))
g1 = guard(); assert g0[0] == g1[0] and abs(g0[1]-g1[1]) < 1e-9
print("GUARD %d rows sum %.4f unchanged; integrity: %s" % (g1[0], g1[1], q("pragma integrity_check")[0][0]))
print("WROTE", a.dst)
