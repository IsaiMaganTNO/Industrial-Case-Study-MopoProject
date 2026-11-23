import sqlite3, json, collections
db = r"runs\ctryco2_mr\output\Investment_Results.ctryco2_mr_ccslow_ccu_cap16_dac0.sqlite"
c = sqlite3.connect(db)
def flat(x):
    while isinstance(x, dict) and "data" in x: x = x["data"]
    return x
W = {"05-14": .287, "09-10": .401, "12-24": .313}  # MR block weights (share of year)
net = collections.defaultdict(float); emis = collections.defaultdict(float); cred = collections.defaultdict(float)
days = collections.defaultdict(set)
for n, v in c.execute("select e.name, pv.value from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id where pd.name='unit_flow' and e.name like '%atmosphere_%'"):
    k = n.split("__atmosphere_")[1][:2]; sign = 1 if "__to_node" in n else -1
    for t, x in flat(json.loads(v)).items():
        y = t[:4]; md = t[5:10]; days[(y)].add(md)
        w = W.get(md)
        if w is None: continue
        val = x * w * 365
        net[(k, y)] += sign * val
        (emis if sign > 0 else cred)[(k, y)] += val
o = open(r"run_logs\_ctryco2_pen3.out", "w", encoding="utf8"); P = lambda *a: print(*a, file=o)
P("dates per year", {y: sorted(s) for y, s in days.items()})
cap = {"NL": 273.43, "BE": 179.80, "NO": 62.52, "DE": 1542.33, "DK": 88.55, "UK": 994.07}
for y in sorted({y for _, y in net}):
    for k in cap:
        cf = 1 if y == "2030" else (0.2222 if y in ("2040", "2041") else 0)
        P(y, k, "emis", round(emis[(k, y)], 1), "credit", round(cred[(k, y)], 1), "net", round(net[(k, y)], 1), "cap", round(cap[k] * cf, 1), "excess", round(net[(k, y)] - cap[k] * cf, 1))
o.close()
