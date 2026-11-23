import sqlite3,json,pandas as pd,re
lo=pd.read_excel(r"verification\CO2_data_IC1_low_cost.xlsx",sheet_name=None); hi=pd.read_excel(r"verification\CO2_data_IC1_high_cost.xlsx",sheet_name=None)
net={(r["from"],r["to"]):r.tariff for _,r in lo["network"].iterrows()}
d=sqlite3.connect(r"runs\3day_nb_v2\input\Final_SpineOpt_Model.tiny.3day.nb_v2.sqlite")
rows=d.execute("""select e.name,pv.value from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id
 join entity e on e.id=pv.entity_id where pd.name='connection_flow_cost' and e.name like '%CO2%'""").fetchall()
m=0;un=[]
for n,v in rows:
  c=n.split("__")[0]; a,_,b=c.partition("_CO2_"); x=float(json.loads(v))*1000
  t=net.get((a,b)) or net.get((b,a))
  if t is not None and abs(t-x)<1e-6: m+=1
  else: un.append((c,round(x,3)))
print("connection_flow_cost rows",len(rows),"matching file network sheet",m)
print("not in file (sample):",un[:8]); print("unmatched pairs kinds:",sorted({re.sub(r"\d","",c) for c,_ in un}))
