import sqlite3,json
r=sqlite3.connect(r"checkpoints\Investment_Results.3day_mixedres.sqlite")
q="""select e.name,pd.name,pv.value from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id where pd.name in ('node_state_longterm','node_state') and (e.name like '%ATUK031%' or e.name like '%NSNL012%' or e.name like '%storage-DK%' or e.name like 'default_report__atmosphere%')"""
for n,p,v in r.execute(q):
  d=json.loads(v)["data"]; ks=list(d)
  if p=='node_state_longterm': print(n[16:],p,d)
  else:
    vals=list(d.values()); print(n[16:],p,len(ks),"min %.1f max %.1f"%(min(vals),max(vals)), [(k[:13],round(d[k],1)) for k in ks[::24]])
m=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.mixedres.sqlite")
q="""select e.name,pd.name,a.name,substr(pv.value,1,300) from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id join alternative a on a.id=pv.alternative_id where pd.name like '%longterm%' or pd.name like 'representative%' or pd.name like '%weight%' or (e.class_id in (select id from entity_class where name='temporal_block'))"""
for x in m.execute(q): print(x)
