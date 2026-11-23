import sqlite3, json
db = r"final_runs_pessimistic_ccs\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK\input\Final_SpineOpt_Model.tiny.3day.mr_ccslow_ccu_cap16_dac0.sqlite"
c = sqlite3.connect(db)
for n, t in c.execute("""select a.name, cast(pv.value as text) from parameter_value pv join entity e on e.id=pv.entity_id
 join parameter_definition pd on pd.id=pv.parameter_definition_id join alternative a on a.id=pv.alternative_id
 where e.name='CO2-storage-NSNL012' and pd.name='storage_investment_count_fix_cumulative'"""):
    print(n, {k[:4]: round(v*365, 3) for k, v in json.loads(t)["data"].items()})
