import sqlite3,json
r=sqlite3.connect(r"checkpoints\Investment_Results.3day_mixedres.sqlite")
print([x[0] for x in r.execute("select distinct pd.name from parameter_definition pd")][:80])
q="""select e.name,pd.name,pv.value from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id where e.name like '%CO2-storage-DK%'"""
for n,p,v in r.execute(q):
  try:
    d=json.loads(v); s=d.get("data",d)
    if isinstance(s,dict): ks=list(s); vals=list(s.values()); print(n,p,len(ks),ks[:2],"min",min(vals),"max",max(vals),"first",vals[:3],"last",vals[-3:])
    else: print(n,p,str(s)[:200])
  except Exception as e: print(n,p,str(v)[:200])
