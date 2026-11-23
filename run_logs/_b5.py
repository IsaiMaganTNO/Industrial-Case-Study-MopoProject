import sqlite3, pickle, pandas as pd
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.group1.biocap365.retireall.sqlite"
c=sqlite3.connect(db)
print("== SMR+CC initial endowments ==")
q="""SELECT e.name, CAST(pv.value AS TEXT) FROM parameter_value pv
 JOIN entity e ON e.id=pv.entity_id
 JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
 WHERE pd.name='investment_count_initial_cumulative' AND e.name LIKE 'SMR%'"""
tot=0
for n,v in c.execute(q):
    print(" ",n,v); tot+=float(v)
print(" TOTAL SMR+CC endowed:",round(tot,3))
print()
print("== LH2-terminal cost ==")
q2="""SELECT e.name, pd.name, CAST(pv.value AS TEXT) FROM parameter_value pv
 JOIN entity e ON e.id=pv.entity_id
 JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
 WHERE e.name LIKE 'LH2-terminal%' AND pd.name IN
  ('vom_cost','unit_investment_cost','fom_cost','investment_count_initial_cumulative',
   'investment_count_max_cumulative')"""
seen=set()
for n,p,v in c.execute(q2):
    if p in seen and 'NLC1' not in n: continue
    seen.add(p); print(" ",n[:40],"|",p[:32],"|",str(v)[:62])
