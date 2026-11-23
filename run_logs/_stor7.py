import sqlite3,json
db=r"checkpoints\Investment_Results.7day_hcco2_co2fix.sqlite"
c=sqlite3.connect("file:%s?mode=ro"%db,uri=True)
rs=c.execute("""SELECT e.name,cast(pv.value as text) FROM parameter_value pv
  JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
  JOIN entity e ON e.id=pv.entity_id
  WHERE pd.name='storages_invested_available'""").fetchall()
agg={}
for n,v in rs:
    core=n.replace("default_report__","").replace("__realization","")
    try:
        d=json.loads(v); d=d.get("data",d)
        items=d if isinstance(d,list) else list(d.items())
        for k,x in items:
            f=float(x)
            if f>1e-6: agg[(core,k[:10])]=agg.get((core,k[:10]),0)+f
    except Exception: pass
print("nonzero storage investments:",len(agg))
for (n,y),f in sorted(agg.items(),key=lambda z:-z[1])[:25]:
    print("  %-46s %-10s %12.4f"%(n[:46],y,f))
c.close()
