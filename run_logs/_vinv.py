import sqlite3, json
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
for u in ["solar-PV-no-tracking_NLC3","wind-on-SP277-HH100_NLC3","solar-PV-existing_NLC3","wind-on-existing_NLC3"]:
    print("="*66); print(u)
    for p,v in c.execute("""select pd.name,pv.value from parameter_value pv
      join parameter_definition pd on pd.id=pv.parameter_definition_id
      join entity e on e.id=pv.entity_id where e.name=? order by pd.name""",(u,)):
        s=bytes(v).decode()
        if len(s)>90: 
            try: s=str(json.loads(s).get("data",s))[:88]
            except: s=s[:88]
        print(f"   {p:44s} {s}")
