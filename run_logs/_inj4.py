import sqlite3,json,collections
db=r"checkpoints\Investment_Results.7day_hcco2_co2fix.sqlite"
c=sqlite3.connect("file:%s?mode=ro"%db,uri=True)
rs=c.execute("""SELECT e.name,cast(pv.value as text) FROM parameter_value pv
  JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
  JOIN entity e ON e.id=pv.entity_id
  WHERE pd.name='unit_flow' AND e.name LIKE '%CO2-injection%'""").fetchall()
agg=collections.defaultdict(float)
for n,v in rs:
    src="atmosphere" if "atmosphere" in n else "CO2pipe"
    try:
        d=json.loads(v); d=d.get("data",d)
        it=d if isinstance(d,list) else list(d.items())
        for k,x in it:
            if k[:4]=="2050": agg[src]+=float(x)
    except Exception: pass
print("2050 CO2-injection inflow by source (rep-period units):")
for k,v in agg.items(): print("   %-12s %14.2f"%(k,v))
t=sum(agg.values())
for k,v in agg.items(): print("   %-12s %5.1f%%"%(k,100*v/t))
c.close()
