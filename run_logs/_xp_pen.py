import sqlite3, json
db = r"xpress_server\Investment_Results.3day_mr_frlu_ccslow_ccu_cap16_dac0.v3.xpress.sqlite"
c = sqlite3.connect(db)
names = [r[0] for r in c.execute("select name from parameter_definition")]
print([n for n in names if 'penal' in n or 'slack' in n or 'cost' in n])
for n in [n for n in names if 'penal' in n or 'slack' in n]:
    tot = 0; cnt = 0
    for (t,) in c.execute("select cast(pv.value as text) from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id where pd.name=?", (n,)):
        d = json.loads(t)["data"]; vals = d.values() if isinstance(d, dict) else [y[1] for y in d]
        tot += sum(abs(x) for x in vals if isinstance(x, (int, float))); cnt += 1
    print(n, "rows", cnt, "sum|.|", tot)

