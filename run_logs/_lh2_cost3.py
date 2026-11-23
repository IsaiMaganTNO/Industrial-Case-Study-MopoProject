import sqlite3, json
db=r"final_runs_pessimistic_ccs\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK\input\Final_SpineOpt_Model.tiny.3day.mr_ccslow_ccu_cap16_dac0.sqlite"
c=sqlite3.connect(db)
q="""select e.name, pv.value from parameter_value pv join entity e on e.id=pv.entity_id
join parameter_definition pd on pd.id=pv.parameter_definition_id where pd.name='tax_out_unit_flow' and e.name like 'global-%'"""
for n,v in c.execute(q):
    v=v.decode() if isinstance(v,bytes) else v
    try: d=json.loads(v)["data"]; print(n, {k[:4]:round(x*1e3,1) for k,x in d.items() if k[:4] in ("2030","2040","2050")}, "EUR/MWh")
    except Exception: print(n,v[:100])
