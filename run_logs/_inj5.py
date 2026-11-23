import sqlite3,json,collections
db=r"checkpoints\Investment_Results.7day_hcco2_co2fix.sqlite"
c=sqlite3.connect("file:%s?mode=ro"%db,uri=True)
rs=c.execute("""SELECT e.name,cast(pv.value as text) FROM parameter_value pv
  JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
  JOIN entity e ON e.id=pv.entity_id
  WHERE pd.name='unit_flow' AND e.name LIKE '%CO2-injection%'""").fetchall()
print("distinct injection flow entities:",len(rs))
for n,v in rs[:10]:
    d=json.loads(v); d=d.get("data",d)
    it=d if isinstance(d,list) else list(d.items())
    s=sum(float(x) for k,x in it if k[:4]=="2050")
    print("   %-72s 2050=%.2f"%(n.replace("default_report__","")[:72],s))
c.close()
