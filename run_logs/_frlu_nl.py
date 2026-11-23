import sqlite3, json
for db in [r"checkpoints\frlu\t9_nuc.sqlite", r"checkpoints\frlu\Final_SpineOpt_Model.tiny.3day.mr_frlu_ccslow_ccu_cap16_dac0.sqlite"]:
    c = sqlite3.connect(db); tot = {}
    for e, t in c.execute("""select e.name, cast(pv.value as text) from parameter_value pv join entity e on e.id=pv.entity_id
     join parameter_definition pd on pd.id=pv.parameter_definition_id join alternative a on a.id=pv.alternative_id
     where e.name like 'CO2-storage-NSNL%' and pd.name='storage_investment_count_fix_cumulative' and a.name='low_CO2'"""):
        d = json.loads(t)["data"]; f = 1 if max(d.values()) > 1 else 365
        print(db.split("\\")[-1][:12], e, {k[:4]: round(v*f, 2) for k, v in d.items()}, "Mt/yr")
