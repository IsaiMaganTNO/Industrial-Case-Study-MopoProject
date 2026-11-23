import sqlite3,json
db=r"checkpoints\Investment_Results.7day_hcco2_co2fix.sqlite"
c=sqlite3.connect("file:%s?mode=ro"%db,uri=True)
v=c.execute("""SELECT cast(pv.value as text) FROM parameter_value pv
  JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
  JOIN entity e ON e.id=pv.entity_id WHERE pd.name='node_state_longterm'
    AND e.name='default_report__atmosphere__realization'""").fetchone()[0]
d=json.loads(v)["data"]
items=d if isinstance(d,list) else list(d.items())
print("%-24s %12s %14s"%("timestamp","state","x365"))
for k,x in items:
    f=float(x); print("%-24s %12.4f %14.1f"%(k[:24],f,f*365))
c.close()
