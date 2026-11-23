import sqlite3,json
r=sqlite3.connect("file:%s?mode=ro"%r"checkpoints\Investment_Results.7day_hcco2_co2fix.sqlite",uri=True)
v=r.execute("""SELECT cast(pv.value as text) FROM parameter_value pv
  JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
  JOIN entity e ON e.id=pv.entity_id
  WHERE e.name LIKE '%CO2-storage-NSNL012%' AND pd.name='node_state_longterm'""").fetchone()
d=json.loads(v[0])["data"]; it=d if isinstance(d,list) else list(d.items())
print("NSNL012 state:",{k[:4]:round(float(x),2) for k,x in it},"cap2050=21000")
v=r.execute("""SELECT cast(pv.value as text) FROM parameter_value pv
  JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
  JOIN entity e ON e.id=pv.entity_id
  WHERE e.name LIKE '%CO2-storage-NSNL031%' AND pd.name='node_state_longterm'""").fetchone()
d=json.loads(v[0])["data"]; it=d if isinstance(d,list) else list(d.items())
print("NSNL031 state:",{k[:4]:round(float(x),2) for k,x in it},"cap2050=6200")
r.close()
