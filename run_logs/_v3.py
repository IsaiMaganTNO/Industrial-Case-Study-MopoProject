import sqlite3, json
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.gascap.vre15.sqlite")
print("=== 1. CO2 BUDGET: model atmosphere storage_state_max vs verification sheet ===")
for p,v,a in c.execute("""select pd.name,pv.value,al.name from parameter_value pv
  join parameter_definition pd on pd.id=pv.parameter_definition_id
  join entity e on e.id=pv.entity_id join alternative al on al.id=pv.alternative_id
  where e.name='atmosphere' and pd.name in ('storage_state_max','storage_state_fix')"""):
    print(f"   [{a}] {p} = {bytes(v).decode()[:200]}")
print()
print("   verification NL+BE: 2030 99.801+65.628 = 165.429 Mt ; 2040 22.178+14.584 = 36.762 Mt ; 2050 0")
print("   model atm levels observed in runs: 2030 453.1507, 2040 100.8219, 2050 0.0  (these are /365 day-units)")
print("   -> x365:", 453.1506849315068*365, 100.82191780821918*365)
