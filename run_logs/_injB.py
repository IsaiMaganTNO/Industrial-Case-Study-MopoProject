import sqlite3,json
m=sqlite3.connect("file:%s?mode=ro"%r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.co2div365.sqlite",uri=True)
for n in ["CO2-storage-NSNL012","CO2-storage-NSNL031"]:
    rs=m.execute("""SELECT DISTINCT cast(pv.value as text) FROM parameter_value pv
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      JOIN entity e ON e.id=pv.entity_id
      WHERE e.name=? AND pd.name='storage_investment_count_fix_cumulative'""",(n,)).fetchall()
    for (v,) in rs: print(n, json.loads(v)["data"])
m.close()
