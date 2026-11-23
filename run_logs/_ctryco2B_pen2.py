import sqlite3, json
o = open(r"run_logs\_ctryco2B_pen2.out", "w", encoding="utf8"); P = lambda *a: print(*a, file=o)
def flat(x):
    while isinstance(x, dict) and "data" in x: x = x["data"]
    return x
for tag, db in [("ctry", r"runs\ctryco2B_mr\output\Investment_Results.ctryco2B_mr_ccslow_ccu_cap16_dac0.sqlite"),
                ("3day", __import__("glob").glob(r"final_runs_pessimistic_ccs\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK\output\*.sqlite")[0])]:
    c = sqlite3.connect(db)
    for n, p, v in c.execute("select e.name, pd.name, pv.value from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id where pd.name like 'objective_%' or pd.name='total_costs'"):
        d = flat(json.loads(v)); s = sum(d.values()) if isinstance(d, dict) else d
        P(tag, n[:60], p, round(s, 1))
    for n, p, v in c.execute("select e.name, pd.name, pv.value from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id where pd.name in ('node_state','node_state_longterm','storages_invested_available','node_injection') and e.name like '%atmosphere%' and e.name not like '%__to_node%' and e.name not like '%__from_node%'"):
        d = flat(json.loads(v))
        if isinstance(d, dict):
            ks = sorted(d); P(tag, n[:70], p, "n", len(ks), "first", ks[0], round(d[ks[0]], 4), "min", round(min(d.values()), 4), "max", round(max(d.values()), 4), "last", ks[-1], round(d[ks[-1]], 4))
        else: P(tag, n[:70], p, d)
o.close()

