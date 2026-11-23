import sqlite3,json,collections
r=sqlite3.connect("file:%s?mode=ro"%r"checkpoints\Investment_Results.7day_hcco2_co2fix.sqlite",uri=True)
rs=r.execute("""SELECT e.name,cast(pv.value as text) FROM parameter_value pv
  JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
  JOIN entity e ON e.id=pv.entity_id
  WHERE pd.name='unit_flow' AND e.name LIKE '%CO2-injection-NSNL012%'""").fetchall()
for n,v in rs:
    d=json.loads(v); d=d.get("data",d); it=d if isinstance(d,list) else list(d.items())
    per={}
    for k,x in it:
        per.setdefault(k[:4],0.0); per[k[:4]]+=float(x)
    print("%-66s %s"%(n.replace("default_report__","")[:66],{k:round(v,2) for k,v in per.items()}))
r.close()
