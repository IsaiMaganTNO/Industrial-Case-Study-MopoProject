import sqlite3, json
db = r"runs\ctryco2_mr\output\Investment_Results.ctryco2_mr_ccslow_ccu_cap16_dac0.sqlite"
c = sqlite3.connect(db); q = lambda s, *a: c.execute(s, a).fetchall()
o = open(r"run_logs\_ctryco2_pen.out", "w", encoding="utf8"); P = lambda *a: print(*a, file=o)
P("params", sorted({r[0] for r in q("select pd.name from parameter_definition pd")}))
rows = q("select e.name, pd.name, pv.value from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id where e.name like '%atmosphere%'")
for n, p, v in rows:
    try:
        d = json.loads(v)
        def walk(x):
            if isinstance(x, dict):
                if "data" in x: return walk(x["data"])
                return {k: walk(w) for k, w in x.items()}
            return x
        P(n, p, str(walk(d))[:600])
    except Exception as e: P(n, p, "ERR", e)
o.close()
