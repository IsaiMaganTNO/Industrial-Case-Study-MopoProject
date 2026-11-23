import sqlite3,json,collections
db=r"checkpoints\Investment_Results.7day_hcco2_co2fix.sqlite"
c=sqlite3.connect("file:%s?mode=ro"%db,uri=True)
rs=c.execute("""SELECT e.name,cast(pv.value as text) FROM parameter_value pv
  JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
  JOIN entity e ON e.id=pv.entity_id
  WHERE pd.name='unit_flow' AND e.name LIKE '%oil-eng%'
    AND e.name LIKE '%elec%'""").fetchall()
print("oil-eng elec flow rows:",len(rs))
byday=collections.defaultdict(float)
for n,v in rs:
    try:
        d=json.loads(v); d=d.get("data",d)
        items=d if isinstance(d,list) else list(d.items())
        for k,x in items:
            f=float(x)
            if f>1e-9: byday[k[:10]]+=f
    except Exception: pass
print("%-14s %12s"%("rep day","oil-eng MW-h"))
for k in sorted(byday): print("  %-12s %12.2f"%(k,byday[k]))
c.close()
