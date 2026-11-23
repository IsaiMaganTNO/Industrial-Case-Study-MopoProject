import sqlite3,json,collections,re
r=sqlite3.connect("file:%s?mode=ro"%r"checkpoints\Investment_Results.7day_hcco2_co2fix.sqlite",uri=True)
rs=r.execute("""SELECT e.name,cast(pv.value as text) FROM parameter_value pv
  JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
  JOIN entity e ON e.id=pv.entity_id
  WHERE pd.name='unit_flow' AND e.name LIKE '%CO2_%'""").fetchall()
src=collections.defaultdict(float); snk=collections.defaultdict(float)
for n,v in rs:
    core=n.replace("default_report__","").replace("__realization","")
    parts=core.split("__")
    unit=re.sub(r'_(NL|BE)C\d+$','',parts[0])
    try:
        d=json.loads(v); d=d.get("data",d); it=d if isinstance(d,list) else list(d.items())
        s=sum(float(x) for k,x in it if k[:4]=="2050")
    except Exception: continue
    if s<=1e-9: continue
    if core.endswith("to_node"): src[unit]+=s
    else: snk[unit]+=s
print("2050 CAPTURE into CO2 nodes (to_node):   total %.1f"%sum(src.values()))
for k,v in sorted(src.items(),key=lambda z:-z[1])[:14]: print("   %-32s %10.1f"%(k[:32],v))
print("\n2050 DRAW from CO2 nodes (from_node):   total %.1f"%sum(snk.values()))
for k,v in sorted(snk.items(),key=lambda z:-z[1])[:14]: print("   %-32s %10.1f"%(k[:32],v))
r.close()
