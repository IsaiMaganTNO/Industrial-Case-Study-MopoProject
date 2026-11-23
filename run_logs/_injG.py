import sqlite3,json
m=sqlite3.connect("file:%s?mode=ro"%r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.co2div365.sqlite",uri=True)
# cyclic / longterm settings differ?
for n in ["CO2-storage-NSNL012","CO2-storage-NSNL031"]:
    rs=m.execute("""SELECT pd.name,a.name,cast(pv.value as text) FROM parameter_value pv
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      JOIN entity e ON e.id=pv.entity_id JOIN alternative a ON a.id=pv.alternative_id
      WHERE e.name=? ORDER BY pd.name""",(n,)).fetchall()
    print("==",n)
    for p,a,v in rs: print("    %-36s %-10s %s"%(p[:36],a[:10],v[:34]))
m.close()
