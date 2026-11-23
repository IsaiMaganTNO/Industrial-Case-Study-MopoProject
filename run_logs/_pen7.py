import sqlite3,json
db=r"checkpoints\Investment_Results.7day_hcco2_co2fix.sqlite"
c=sqlite3.connect("file:%s?mode=ro"%db,uri=True)
rs=c.execute("""SELECT e.name,pd.name,cast(pv.value as text) FROM parameter_value pv
  JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
  JOIN entity e ON e.id=pv.entity_id
  WHERE pd.name LIKE '%penalt%' OR e.name LIKE '%penalt%'""").fetchall()
tot=0.0
for n,p,v in rs:
    try:
        d=json.loads(v); d=d.get("data",d)
        vals=[x[1] for x in d] if isinstance(d,list) else list(d.values())
        s=sum(float(x) for x in vals)
    except Exception:
        try: s=float(v)
        except Exception: continue
    tot+=s
    if abs(s)>1e-9: print("NONZERO",n[:55],p,s)
print("penalty rows:",len(rs),"TOTAL=%.6f"%tot)
c.close()
