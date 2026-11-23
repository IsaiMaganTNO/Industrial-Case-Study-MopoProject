import sqlite3, json
db = r"runs\3day_mr_ccsopt_ccu_dac0\output\Investment_Results.mr_ccsopt_ccu_dac0.sqlite"
c = sqlite3.connect(db)
def flat(x):
    while isinstance(x, dict) and "data" in x: x = x["data"]
    return x
o = open(r"run_logs\_ccsopt_pen.out", "w", encoding="utf8")
for n, v in c.execute("select pd.name, pv.value from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id where pd.name like '%cost%' or pd.name='penalties' or pd.name like 'objective%'"):
    try:
        d = flat(json.loads(v)); s = sum(d.values()) if isinstance(d, dict) else d
        o.write(f"{n} {s}\n")
    except Exception as e: o.write(f"{n} ? {e}\n")
o.close()
