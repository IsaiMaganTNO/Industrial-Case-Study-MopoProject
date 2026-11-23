import sqlite3
B=r"final_runs_pessimistic_ccs\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK\input\Final_SpineOpt_Model.tiny.3day.mr_ccslow_ccu_cap16_dac0.sqlite"
N=r"runs\3day_mr_frlu_ccslow_ccu_cap16_dac0_v3\input\Final_SpineOpt_Model.tiny.3day.mr_frlu_ccslow_ccu_cap16_dac0.v3.sqlite"
q="""select e.name, pd.name, a.name, cast(pv.value as text) from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id
 join entity e on e.id=pv.entity_id join entity_class ec on ec.id=e.class_id join alternative a on a.id=pv.alternative_id
 where ec.name in ('unit','user_constraint') and (e.name like 'nuclear-3\_%' escape '\\' or e.name like '%nuc%') and pd.name not in ('fom_cost')"""
for lab,db in (("BASE",B),("FRLU",N)):
    c=sqlite3.connect(db); rows=c.execute(q).fetchall()
    print("==",lab,len(rows))
    for r in rows:
        if any(t in r[0] for t in ("NLC","BEC","_NL","_BE","nuc_cap","cap")) : print(" ",r[0],"|",r[1],"|",r[2],"|",(r[3] or "")[:160])
