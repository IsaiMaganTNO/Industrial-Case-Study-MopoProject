import sqlite3, pickle
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.gascap.sqlite")
tot=0
print("Offshore wind headroom (investment_count_total_max_cumulative):")
for n,v in c.execute("""select e.name,pv.value from parameter_value pv
  join parameter_definition pd on pd.id=pv.parameter_definition_id
  join entity e on e.id=pv.entity_id join entity_class ec on ec.id=e.class_id
  where pd.name='investment_count_total_max_cumulative' and ec.name='investment_group'
  and e.name like 'wind-off%' order by e.name"""):
    val=float(bytes(v).decode()); tot+=val
    print(f"   {n:26s} {val:8.4f}")
print(f"   TOTAL offshore cap {tot:.2f} GW")
d=pickle.load(open(r"run_logs\gascap.pkl","rb"))
fl=d["fleet"]; used=fl[(fl.year==2050)&fl.tech.str.startswith("wind-off-FB-SP")]["units"].sum()
print(f"   used in gascap 2050 {used:.2f} GW -> headroom {tot-used:.2f} GW")
print(f"   extra generation if fully built @CF0.50: {(tot-used)*0.50*8760:,.0f} GWh")
print()
print("   (gap to fill was ~190,007 GWh)")
print()
print("Nuclear: investment_count_max_cumulative 1000.0 per unit, 17 units, NO active cap")
print("   -> nuclear is the only other unconstrained firm option")
