import sqlite3,json,pandas as pd,re
low=pd.read_excel(r"verification\CO2_data_IC1_low_cost.xlsx",sheet_name=None); high=pd.read_excel(r"verification\CO2_data_IC1_high_cost.xlsx",sheet_name=None)
for run in ["3day_mr_fix","3day_nb_v2"]:
  db=rf"runs\{run}\input\Final_SpineOpt_Model.tiny.3day.{run[5:]}.sqlite"; d=sqlite3.connect(db)
  rows=d.execute("""select c.name,e.name,pd.name,pv.type,pv.value from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id
   join entity e on e.id=pv.entity_id join entity_class c on c.id=e.class_id
   where (e.name like '%CO2%' or e.name like '%injection%') and (pd.name like '%cost%')""").fetchall()
  print("=====",run,len(rows))
  seen=set()
  for c,n,p,t,v in rows:
    k=(c,p); 
    if k in seen and not re.search(r"NLC6_CO2_DE|DE_CO2_NLC6|NSNL031|ATUK031|NSDKW12",n): continue
    seen.add(k); print(f"  {c:28s} {p:28s} {n[:60]:60s} {v[:60]!r}")
