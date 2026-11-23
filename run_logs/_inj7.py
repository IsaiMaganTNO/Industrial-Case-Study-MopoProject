import sqlite3,json
db=r"checkpoints\Investment_Results.7day_hcco2_co2fix.sqlite"
c=sqlite3.connect("file:%s?mode=ro"%db,uri=True)
for res in ("CO2-storage-NSNL031","CO2-storage-NSNL012"):
    r=c.execute("""SELECT cast(pv.value as text) FROM parameter_value pv
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      JOIN entity e ON e.id=pv.entity_id
      WHERE e.name LIKE ? AND pd.name='node_state_longterm'""",("%"+res+"%",)).fetchone()
    if not r: print(res,"no state"); continue
    d=json.loads(r[0])["data"]
    it=d if isinstance(d,list) else list(d.items())
    print(res,{k[:4]:round(float(x),1) for k,x in it})
# cap: fix_cumulative x state_max
m=sqlite3.connect("file:%s?mode=ro"%r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.co2div365.sqlite",uri=True)
for res in ("CO2-storage-NSNL031","CO2-storage-NSNL012"):
    v=m.execute("""SELECT cast(pv.value as text) FROM parameter_value pv
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      JOIN entity e ON e.id=pv.entity_id
      WHERE e.name=? AND pd.name='storage_investment_count_fix_cumulative'""",(res,)).fetchone()
    sm=m.execute("""SELECT cast(pv.value as text) FROM parameter_value pv
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      JOIN entity e ON e.id=pv.entity_id
      WHERE e.name=? AND pd.name='storage_state_max'""",(res,)).fetchone()
    d=json.loads(v[0])["data"]
    print(res,"cap2050 =",d.get("2050-01-01T00:00:00"),"x",sm[0],"=",
          float(d.get("2050-01-01T00:00:00"))*float(sm[0]))
c.close(); m.close()
