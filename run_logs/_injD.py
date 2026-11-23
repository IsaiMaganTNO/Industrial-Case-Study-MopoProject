import sqlite3,json
m=sqlite3.connect("file:%s?mode=ro"%r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.co2div365.sqlite",uri=True)
active={a for (s,a) in m.execute("""SELECT s.name,a.name FROM scenario s
  JOIN scenario_alternative sa ON sa.scenario_id=s.id
  JOIN alternative a ON a.id=sa.alternative_id""")}
print("ACTIVE alts:",sorted(active))
for n in ["CO2-storage-NSNL012","CO2-storage-NSNL031"]:
    rs=m.execute("""SELECT a.name FROM parameter_value pv
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      JOIN entity e ON e.id=pv.entity_id
      JOIN alternative a ON a.id=pv.alternative_id
      WHERE e.name=? AND pd.name='storage_investment_count_fix_cumulative'""",(n,)).fetchall()
    alts={a for (a,) in rs}
    print("%-20s alts=%s  ACTIVE-OVERLAP=%s"%(n[-10:],sorted(alts),sorted(alts&active)))
m.close()
