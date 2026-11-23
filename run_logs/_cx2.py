import sqlite3, json
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
def cost(u):
    r=c.execute("""select pv.value from parameter_value pv
      join parameter_definition pd on pd.id=pv.parameter_definition_id
      join entity e on e.id=pv.entity_id where e.name=? and pd.name='unit_investment_cost'""",(u,)).fetchone()
    return {k[:4]:float(v) for k,v in json.loads(bytes(r[0]).decode())["data"].items()} if r else None
s=cost("solar-PV-no-tracking_NLC3"); w=cost("wind-on-SP277-HH100_NLC3")
print("CAPEX DECLINE 2030 -> 2050:")
for n,d in [("solar",s),("wind-on",w)]:
    print(f"  {n:8s} {d['2030']:8.1f} -> {d['2050']:7.1f}  = -{(1-d['2050']/d['2030'])*100:.1f}%")
print()
# lifetime + discount
for u in ["solar-PV-no-tracking_NLC3","wind-on-SP277-HH100_NLC3"]:
    ps={p:bytes(v).decode() for p,v in c.execute("""select pd.name,pv.value from parameter_value pv
      join parameter_definition pd on pd.id=pv.parameter_definition_id
      join entity e on e.id=pv.entity_id where e.name=?""",(u,))}
    print(f"{u:30s} lifetime_econ={ps.get('lifetime_economic','')} disc={ps.get('discount_rate_technology_specific','default')}")
print()
# model-level discount
for p,v in c.execute("""select pd.name,pv.value from parameter_value pv
  join parameter_definition pd on pd.id=pv.parameter_definition_id
  join entity e on e.id=pv.entity_id join entity_class ec on ec.id=e.class_id
  where ec.name='model' and pd.name like '%discount%'"""):
    print(f"model {p:38s} {bytes(v).decode()[:40]}")
