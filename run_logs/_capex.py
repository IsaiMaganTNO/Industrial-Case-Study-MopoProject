import sqlite3, json
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
print("unit_investment_cost trajectories (EUR/kW-ish, model units):")
for u in ["solar-PV-no-tracking_NLC3","wind-on-SP277-HH100_NLC3","CCGT+CC_NLC3","wind-off-FO-SP316-HH155_NSNL031"]:
    r=c.execute("""select pv.value from parameter_value pv
      join parameter_definition pd on pd.id=pv.parameter_definition_id
      join entity e on e.id=pv.entity_id where e.name=? and pd.name='unit_investment_cost'""",(u,)).fetchone()
    if not r: print(f"  {u}: none"); continue
    d=json.loads(bytes(r[0]).decode())["data"]
    print(f"  {u:34s} "+"  ".join(f"{k[:4]}={float(v):8.1f}" for k,v in d.items()))
print()
print("investment_count_fix_new on VRE (blocks new build in a period):")
for p,n in c.execute("""select e.name,pv.value from parameter_value pv
  join parameter_definition pd on pd.id=pv.parameter_definition_id
  join entity e on e.id=pv.entity_id
  where pd.name='investment_count_fix_new' and (e.name like 'solar-PV-no%' or e.name like 'wind-on-SP%') limit 6"""):
    print(f"   {p:40s} {bytes(n).decode()[:60]}")
print("  (none listed above = no restriction)")
