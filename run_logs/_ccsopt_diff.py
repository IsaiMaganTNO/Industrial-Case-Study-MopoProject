import sqlite3, json
N = r"runs\3day_mr_ccsopt_ccu_dac0\Final_SpineOpt_Model.tiny.3day.mr_ccsopt_ccu_dac0.sqlite"
O = r"runs\3day_mr_fix\input\Final_SpineOpt_Model.tiny.3day.mr_fix.sqlite"
Q = "select e.name, pd.name, a.name, pv.value from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id join alternative a on a.id=pv.alternative_id where pd.name in ('connection_flow_cost','vom_cost') and e.name like '%CO2%'"
a = {r[:3]: r[3] for r in sqlite3.connect(N).execute(Q)}; b = {r[:3]: r[3] for r in sqlite3.connect(O).execute(Q)}
o = open(r"run_logs\_ccsopt_diff.out", "w", encoding="utf8")
for k in sorted(a):
    if k in b and a[k] != b[k]:
        try: va, vb = json.loads(a[k]), json.loads(b[k])
        except Exception: va, vb = a[k], b[k]
        if va != vb: o.write(f"{k} new={va} mr_fix={vb}\n")
o.close()
