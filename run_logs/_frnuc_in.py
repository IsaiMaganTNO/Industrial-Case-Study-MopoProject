import sqlite3, json
db=r"runs\3day_mr_frlu_ccslow_ccu_cap16_dac0_v3\input\Final_SpineOpt_Model.tiny.3day.mr_frlu_ccslow_ccu_cap16_dac0.v3.sqlite"
c=sqlite3.connect(db)
q="""select e.name, ec.name, pd.name, a.name, cast(pv.value as text) from parameter_value pv
 join parameter_definition pd on pd.id=pv.parameter_definition_id join entity e on e.id=pv.entity_id
 join entity_class ec on ec.id=e.class_id join alternative a on a.id=pv.alternative_id
 where e.name like '%nuclear-3-existing%' and (e.name like '%FR%' or e.name like '%UK%')"""
for r in c.execute(q):
    v=r[4]; print(r[0],"|",r[1],"|",r[2],"|",r[3],"|",(v[:200] if v else v))
