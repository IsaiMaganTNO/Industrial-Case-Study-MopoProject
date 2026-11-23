import sqlite3,json
r=sqlite3.connect("file:%s?mode=ro"%r"checkpoints\Investment_Results.7day_hcco2_co2fix.sqlite",uri=True)
for res in ("NSNL031","NSNL012"):
    v=r.execute("""SELECT cast(pv.value as text) FROM parameter_value pv
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      JOIN entity e ON e.id=pv.entity_id
      WHERE e.name LIKE ? AND pd.name='node_state'""",("%CO2-storage-"+res+"%",)).fetchone()
    if not v: print(res,"no node_state"); continue
    d=json.loads(v[0])["data"]; it=d if isinstance(d,list) else list(d.items())
    vals=[(k,float(x)) for k,x in it]
    v50=[x for k,x in vals if k[:4]=="2050"]
    print("%s node_state 2050: n=%d min=%.2f max=%.2f"%(res,len(v50),min(v50),max(v50)))
r.close()
