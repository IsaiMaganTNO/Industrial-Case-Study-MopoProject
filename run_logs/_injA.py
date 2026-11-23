import sqlite3,json
m=sqlite3.connect("file:%s?mode=ro"%r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.co2div365.sqlite",uri=True)
for u in ["CO2-injection-NSNL012_NLC1","CO2-injection-NSNL031_NLC1"]:
    print("==",u)
    rs=m.execute("""SELECT pd.name,cast(pv.value as text) FROM parameter_value pv
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      JOIN entity e ON e.id=pv.entity_id WHERE e.name LIKE ?""",(u+"%",)).fetchall()
    for p,v in rs: print("    %-34s %s"%(p[:34],v[:46]))
for n in ["CO2-storage-NSNL012","CO2-storage-NSNL031"]:
    print("==",n)
    rs=m.execute("""SELECT pd.name,cast(pv.value as text) FROM parameter_value pv
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      JOIN entity e ON e.id=pv.entity_id WHERE e.name=?""",(n,)).fetchall()
    for p,v in rs: print("    %-34s %s"%(p[:34],v[:46]))
m.close()
