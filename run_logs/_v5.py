import sqlite3, json
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.gascap.vre15.sqlite")
print("=== NUCLEAR buildout: verification sheet says NL 0/4/5 GW, BE 0/6/6 GW ===")
for p,v,a in c.execute("""select pd.name,pv.value,al.name from parameter_value pv
  join parameter_definition pd on pd.id=pv.parameter_definition_id
  join entity e on e.id=pv.entity_id join alternative al on al.id=pv.alternative_id
  where e.name='nuclear-3'"""):
    print(f"   [{a}] {p} = {bytes(v).decode()[:180]}")
print()
print("  -> verification intends a nuclear FLOOR/CAP per country (NL 4 GW by 2040, 5 by 2050;")
print("     BE 6 GW by 2040 and 2050). Model has ONE pan-EU cap 120 in an INACTIVE alternative.")
print("     Model builds ZERO nuclear in every run.")
