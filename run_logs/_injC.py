import sqlite3,json
m=sqlite3.connect("file:%s?mode=ro"%r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.co2div365.sqlite",uri=True)
sc=m.execute("""SELECT s.name,a.name FROM scenario s
  JOIN scenario_alternative sa ON sa.scenario_id=s.id
  JOIN alternative a ON a.id=sa.alternative_id ORDER BY sa.rank""").fetchall()
print("scenario alternatives (by rank):",sc)
for n in ["CO2-storage-NSNL012","CO2-storage-NSNL031"]:
    rs=m.execute("""SELECT a.name,cast(pv.value as text) FROM parameter_value pv
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      JOIN entity e ON e.id=pv.entity_id
      JOIN alternative a ON a.id=pv.alternative_id
      WHERE e.name=? AND pd.name='storage_investment_count_fix_cumulative'""",(n,)).fetchall()
    for alt,v in rs: print("  %-22s alt=%-22s %s"%(n[-9:],alt[:22],json.loads(v)["data"]))
m.close()
