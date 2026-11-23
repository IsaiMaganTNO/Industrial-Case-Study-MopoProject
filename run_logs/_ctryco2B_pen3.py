import sqlite3, json, collections
db = r"runs\ctryco2B_mr\output\Investment_Results.ctryco2B_mr_ccslow_ccu_cap16_dac0.sqlite"
c = sqlite3.connect(db)
def flat(x):
    while isinstance(x, dict) and "data" in x: x = x["data"]
    return x
W = {"05-14": .287, "09-10": .401, "12-24": .313}
emis = collections.defaultdict(float); cred = collections.defaultdict(float)
xin = collections.defaultdict(float); xout = collections.defaultdict(float)
q = ("select pd.name, e.name, pv.value from parameter_value pv join entity e on e.id=pv.entity_id "
     "join parameter_definition pd on pd.id=pv.parameter_definition_id "
     "where pd.name in ('unit_flow','connection_flow') and e.name like '%atmosphere_%'")
for p, n, v in c.execute(q):
    k = n.split("__atmosphere_")[1][:2]; to = "__to_node" in n
    for t, x in flat(json.loads(v)).items():
        w = W.get(t[5:10])
        if w is None: continue
        val = x * w * 365 / 1000.0  # Mt
        key = (k, t[:4])
        if p == "unit_flow": (emis if to else cred)[key] += val
        else: (xin if to else xout)[key] += val
cap = {"2030": {"NL":99.8,"BE":65.6,"NO":22.8,"DE":563.0,"DK":32.3,"UK":362.8},
       "2041": {"NL":22.2,"BE":14.6,"NO":5.1,"DE":125.1,"DK":7.2,"UK":80.6},
       "2050": {k:0.0 for k in ["NL","BE","NO","DE","DK","UK"]}}
o = open(r"run_logs\_ctryco2B_pen3.out", "w", encoding="utf8")
o.write("year ctry emis_Mt inj_credit xfer_in xfer_out net cap excess\n")
for y in ["2030","2041","2050"]:
    for k in cap[y]:
        key=(k,y); net = emis[key]-cred[key]+xin[key]-xout[key]
        o.write(f"{y} {k} {emis[key]:.2f} {cred[key]:.2f} {xin[key]:.2f} {xout[key]:.2f} {net:.2f} {cap[y][k]:.1f} {net-cap[y][k]:.2f}\n")
o.close()
