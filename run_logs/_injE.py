import sqlite3,json
m=sqlite3.connect("file:%s?mode=ro"%r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.co2div365.sqlite",uri=True)
# unit capacity limits on injection units
for u in ["CO2-injection-NSNL012_NLC1","CO2-injection-NSNL012_NLC5","CO2-injection-NSNL012_NLC6",
          "CO2-injection-NSNL031_NLC5"]:
    rs=m.execute("""SELECT pd.name,a.name,cast(pv.value as text) FROM parameter_value pv
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      JOIN entity e ON e.id=pv.entity_id
      JOIN alternative a ON a.id=pv.alternative_id
      WHERE e.name LIKE ?""",(u+"%",)).fetchall()
    print("==",u)
    for p,a,v in rs: print("    %-32s %-12s %s"%(p[:32],a[:12],v[:40]))
m.close()
