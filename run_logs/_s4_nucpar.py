import sqlite3,glob
for n,db in [("MR",glob.glob(r"final_runs_pessimistic_ccs\3_*\input\*.sqlite")[0]),("S4",r"share_frlu_xpress\input.sqlite")]:
  c=sqlite3.connect(db)
  q="""select e.name,pd.name,a.name,substr(cast(pv.value as text),1,140) from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id join entity e on e.id=pv.entity_id join alternative a on a.id=pv.alternative_id join entity_class ec on ec.id=e.class_id where e.name in ('nuclear-3','nuclear-3_NLC8') or (ec.name='unit' and e.name like 'nuclear-3' )"""
  print("==",n); [print(*r) for r in c.execute(q)]
  print(c.execute("select group_concat(e.name) from entity e join entity_class ec on ec.id=e.class_id where ec.name='unit' and e.name like 'nuclear-3%' and e.name not like '%existing%'").fetchone()[0][:300])
