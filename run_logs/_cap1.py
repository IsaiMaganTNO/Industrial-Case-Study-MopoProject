import sqlite3,json,collections
r=sqlite3.connect("file:%s?mode=ro"%r"checkpoints\Investment_Results.7day_hcco2_co2fix.sqlite",uri=True)
# what feeds the CO2_* nodes (captured carbon) and where does it go
rs=r.execute("""SELECT e.name,cast(pv.value as text) FROM parameter_value pv
  JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
  JOIN entity e ON e.id=pv.entity_id
  WHERE pd.name='unit_flow' AND e.name LIKE '%__CO2_%'""").fetchall()
src=collections.defaultdict(float); snk=collections.defaultdict(float)
for n,v in rs:
    core=n.replace("default_report__","").replace("__realization","")
    try:
        d=json.loads(v); d=d.get("data",d); it=d if isinstance(d,list) else list(d.items())
        s=sum(float(x) for k,x in it if k[:4]=="2050")
    except Exception: continue
    if s<=0: continue
    unit=core.split("__")[0]
    if "__to_node__" in core: src[unit]+=s
    elif "__from_node__" in core: snk[unit]+=s
print("2050 CO2 node PRODUCERS (capture):")
for k,v in sorted(src.items(),key=lambda z:-z[1])[:12]: print("   %-34s %10.1f"%(k[:34],v))
print("2050 CO2 node CONSUMERS:")
for k,v in sorted(snk.items(),key=lambda z:-z[1])[:12]: print("   %-34s %10.1f"%(k[:34],v))
r.close()
