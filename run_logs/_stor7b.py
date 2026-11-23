import sqlite3,json,re
db=r"checkpoints\Investment_Results.7day_hcco2_co2fix.sqlite"
c=sqlite3.connect("file:%s?mode=ro"%db,uri=True)
rs=c.execute("""SELECT e.name,cast(pv.value as text) FROM parameter_value pv
  JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
  JOIN entity e ON e.id=pv.entity_id
  WHERE pd.name='storages_invested_available'""").fetchall()
fams={}
for n,v in rs:
    core=n.replace("default_report__","").replace("__realization","")
    fam=re.sub(r'_(NL|BE)C\d+$','',core)
    try:
        d=json.loads(v); d=d.get("data",d)
        items=d if isinstance(d,list) else list(d.items())
        for k,x in items:
            y=k[:4]
            if y not in ("2030","2040","2050"): continue
            fams.setdefault(fam,{}).setdefault(y,0.0)
            fams[fam][y]+=float(x)
    except Exception: pass
print("%-34s %12s %12s %12s"%("family","2030","2040","2050"))
for f,d in sorted(fams.items(),key=lambda z:-max(z[1].values())):
    print("%-34s %12.2f %12.2f %12.2f"%(f[:34],d.get("2030",0),d.get("2040",0),d.get("2050",0)))
c.close()
