import sqlite3, json
B = r"final_runs_pessimistic_ccs\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK\input\Final_SpineOpt_Model.tiny.3day.mr_ccslow_ccu_cap16_dac0.sqlite"
N = r"checkpoints\frlu\Final_SpineOpt_Model.tiny.3day.mr_frlu_ccslow_ccu_cap16_dac0.sqlite"
q = """select e.name, a.name, cast(pv.value as text) from parameter_value pv join entity e on e.id=pv.entity_id
 join parameter_definition pd on pd.id=pv.parameter_definition_id join alternative a on a.id=pv.alternative_id
 where e.name like 'CO2-storage-%' and pd.name='storage_investment_count_fix_cumulative' and a.name='low_CO2' order by e.name"""
for tag, db in (("BASE", B), ("FRLU", N)):
    print("==", tag)
    for e, a, t in sqlite3.connect(db).execute(q):
        d = json.loads(t); print(f"  {e:28s}", {k[:4]: round(v, 4) for k, v in d["data"].items()} if isinstance(d, dict) else d)
