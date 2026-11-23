import sqlite3,json,collections
db=r"checkpoints\Investment_Results.7day_hcco2_co2fix.sqlite"
c=sqlite3.connect("file:%s?mode=ro"%db,uri=True)
rs=c.execute("""SELECT e.name,cast(pv.value as text) FROM parameter_value pv
  JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
  JOIN entity e ON e.id=pv.entity_id
  WHERE pd.name='unit_flow' AND e.name LIKE '%CO2-injection%'""").fetchall()
g=collections.defaultdict(dict)
for n,v in rs:
    core=n.replace("default_report__","").replace("__realization","")
    unit=core.split("__")[0]
    leg=("atm" if "atmosphere" in core else ("co2" if "__CO2_" in core else "out"))
    d=json.loads(v); d=d.get("data",d)
    it=d if isinstance(d,list) else list(d.items())
    g[unit][leg]=sum(float(x) for k,x in it if k[:4]=="2050")
print("%-34s %10s %10s %10s"%("injection unit","atm_in","co2_in","out"))
for u in sorted(g):
    r=g[u]; print("%-34s %10.2f %10.2f %10.2f"%(u[:34],r.get("atm",0),r.get("co2",0),r.get("out",0)))
c.close()
