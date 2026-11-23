import sqlite3, json
db=r"final_runs_pessimistic_ccs\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK\input\Final_SpineOpt_Model.tiny.3day.mr_ccslow_ccu_cap16_dac0.sqlite"
c=sqlite3.connect(db)
q="""select e.name, pd.name, pv.type, pv.value from parameter_value pv join entity e on e.id=pv.entity_id
join parameter_definition pd on pd.id=pv.parameter_definition_id
where e.name like '%LH2%' or e.name like '%Non-EU%' or e.name like '%import%H2%' or e.name like '%H2%import%'"""
for n,p,t,v in c.execute(q):
    v=v.decode() if isinstance(v,bytes) else v
    print(n,"|",p,"|",t,"|",str(v)[:200])
