import sqlite3, json
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
print("model horizon:")
for p,v in c.execute("""select pd.name,pv.value from parameter_value pv
  join parameter_definition pd on pd.id=pv.parameter_definition_id
  join entity e on e.id=pv.entity_id join entity_class ec on ec.id=e.class_id
  where ec.name='model' and pd.name in ('model_start','model_end')"""):
    print(f"   {p:14s} {bytes(v).decode()}")
print()
print("existing VRE retirement schedule (investment_count_max_cumulative):")
for u in ["solar-PV-existing_NLC3","wind-on-existing_NLC3","solar-PV-existing_BEC6"]:
    r=c.execute("""select pv.value from parameter_value pv
      join parameter_definition pd on pd.id=pv.parameter_definition_id
      join entity e on e.id=pv.entity_id where e.name=? and pd.name='investment_count_max_cumulative'""",(u,)).fetchone()
    if r:
        d=json.loads(bytes(r[0]).decode())["data"]
        print(f"   {u:26s} "+"  ".join(f"{k[:4]}={float(v):7.3f}" for k,v in d.items()))
