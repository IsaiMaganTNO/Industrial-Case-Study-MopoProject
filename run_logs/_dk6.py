import sqlite3,json
r=sqlite3.connect(r"checkpoints\Investment_Results.3day_mixedres.sqlite")
q="""select e.name,pd.name,pv.value from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id where pd.name in ('node_state_longterm','storages_invested_available') and (e.name like '%CO2-storage%' or e.name like '%atmosphere%')"""
for n,p,v in r.execute(q):
  d=json.loads(v)["data"]; print(n.replace("default_report__",""),p,{k[:10]:round(x,1) for k,x in d.items()})
