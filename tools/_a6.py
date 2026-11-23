import sqlite3
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.group1.biocap365.sqlite")
n=c.execute("SELECT COUNT(*) FROM parameter_value WHERE typeof(value)!='blob'").fetchone()[0]
print("non-blob rows in WHOLE db:",n)
for r in c.execute("""SELECT typeof(pv.value),CAST(pv.value AS TEXT) FROM parameter_value pv
  JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
  JOIN entity e ON e.id=pv.entity_id JOIN alternative al ON al.id=pv.alternative_id
  WHERE pd.name IN ('storage_investment_count_fix_cumulative','storage_state_fix')
    AND e.name='biomass-stock_BEC1' AND al.name='medium_bio'"""): print(r[0],r[1][:70])
