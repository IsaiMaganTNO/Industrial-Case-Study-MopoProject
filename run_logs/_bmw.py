import pickle, sqlite3, pandas as pd
B=pickle.load(open(r"run_logs\co2bidir.pkl","rb"))
# Is CEM2-(BMW)Oxy-MEA biomass-fired? check its emission/capture coefficients in the model DB
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
print("flow_ratio_equality_coefficient rows for CEM2-(BMW)Oxy-MEA units:")
rows=c.execute("""
 select e.name, pv.value from parameter_value pv
 join parameter_definition pd on pd.id=pv.parameter_definition_id
 join entity e on e.id=pv.entity_id
 where pd.name='flow_ratio_equality_coefficient' and e.name like '%CEM2-(BMW)Oxy-MEA%'
 limit 8""").fetchall()
for n,v in rows: print(f"   {n[:70]:70s} {bytes(v).decode()}")
print()
# what fuel does it draw?
print("inputs (node__to_unit) of one CEM2-(BMW)Oxy-MEA unit:")
u=c.execute("""select e.name from entity e join entity_class ec on ec.id=e.class_id
  where ec.name='unit' and e.name like 'CEM2-(BMW)Oxy-MEA%' limit 1""").fetchone()[0]
print("   unit:",u)
for n, in c.execute("""select e2.name from entity e
  join entity_class ec on ec.id=e.class_id
  join entity_element l0 on l0.entity_id=e.id and l0.position=1
  join entity t on t.id=l0.element_id
  join entity_element l1 on l1.entity_id=e.id and l1.position=0
  join entity e2 on e2.id=l1.element_id
  where ec.name='node__to_unit' and t.name=?""",(u,)):
    print("     input node:",n)
print()
# biomass use across runs
A=pickle.load(open(r"run_logs\routeemis.pkl","rb"))
for tag,D in [("BASELINE",A),("BIDIR   ",B)]:
    s=D["supply"]
    bio=s[s["node"].astype(str).str.contains("bio",case=False,na=False)] if "node" in s.columns else None
    print(f"{tag} supply cols={list(s.columns)}")
    if bio is not None and len(bio):
        print("   bio supply by year:",bio.groupby("year")["value"].sum().round(1).to_dict() if "value" in bio.columns else "n/a")
