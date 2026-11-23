import sqlite3
c=sqlite3.connect(r"share_frlu_xpress\input.sqlite")
q="""select ec.name,e.name,pd.name,a.name,cast(pv.value as text) from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id join entity e on e.id=pv.entity_id join entity_class ec on ec.id=e.class_id join alternative a on a.id=pv.alternative_id where a.name in ('limited_nuclear-3','limited_fossil-CH4')"""
for r in c.execute(q): print(r[0],r[1],r[2],r[3],r[4][:300])
for n in ["nuclear-3"]:
  print(c.execute("select count(*) from entity e where e.name like 'nuclear-3%'").fetchone())
