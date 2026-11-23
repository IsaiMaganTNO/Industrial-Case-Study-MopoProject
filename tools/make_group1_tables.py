"""Group 1 retirement run -- comparison tables vs the 3-day baseline."""
import sqlite3, json, collections, csv, os

BASE = r"reports_3day_co2rebuild\RESULTS_Investment_Results.3day_co2rebuild.sqlite"
GRP1 = r"reports_3day_group1\RESULTS_Investment_Results.3day_group1.sqlite"
OUT  = r"reports_3day_group1\tables"
YRS  = ("2030", "2041", "2050")

def rows(db, param):
    c = sqlite3.connect(db)
    q = """SELECT e.name, pv.value FROM parameter_value pv
           JOIN entity e ON e.id=pv.entity_id
           JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
           WHERE pd.name=?"""
    for n, v in c.execute(q, (param,)):
        v = v.decode() if isinstance(v, bytes) else v
        try: d = json.loads(v)["data"]
        except Exception: continue
        yield n, d

def by_tech(db, param):
    agg = collections.defaultdict(lambda: collections.defaultdict(float))
    for n, d in rows(db, param):
        p = n.split("__")
        if len(p) < 3: continue
        tech = p[1].rsplit("_", 1)[0]
        for k, x in d.items(): agg[tech][k[:4]] += float(x)
    return agg

def write(fn, header, data):
    path = os.path.join(OUT, fn)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(data)
    print("wrote", path, len(data), "rows")

# 1. fleet by tech
b, g = by_tech(BASE, "units_invested_available"), by_tech(GRP1, "units_invested_available")
out = []
for t in sorted(set(b) | set(g)):
    r = [t]
    for y in YRS: r += [round(b[t].get(y, 0.0), 4), round(g[t].get(y, 0.0), 4),
                        round(g[t].get(y, 0.0) - b[t].get(y, 0.0), 4)]
    if any(abs(x) > 1e-9 for x in r[1:]): out.append(r)
hdr = ["tech"] + [f"{y}_{s}" for y in YRS for s in ("base", "group1", "delta")]
write("fleet_by_tech_base_vs_group1.csv", hdr, out)

# 2. objective components
PARAMS = ["objective_objective_penalties","objective_connection_flow_costs",
 "objective_connection_investment_costs","objective_fixed_om_costs","objective_fuel_costs",
 "objective_storage_investment_costs","objective_taxes","objective_unit_investment_costs",
 "objective_variable_om_costs","total_costs"]
def costs(db):
    c = sqlite3.connect(db); o = collections.defaultdict(float)
    q = ("SELECT pd.name, pv.value FROM parameter_value pv JOIN parameter_definition pd "
         "ON pd.id=pv.parameter_definition_id WHERE pd.name IN (%s)" % ",".join("?"*len(PARAMS)))
    for p, v in c.execute(q, PARAMS):
        v = v.decode() if isinstance(v, bytes) else v
        try:
            d = json.loads(v)
            for x in (d["data"].values() if isinstance(d, dict) and "data" in d else [d]):
                o[p] += float(x)
        except Exception:
            try: o[p] += float(v)
            except Exception: pass
    return o
cb, cg = costs(BASE), costs(GRP1)
write("objective_components.csv", ["component","base","group1","delta"],
      [[p, round(cb.get(p,0),2), round(cg.get(p,0),2), round(cg.get(p,0)-cb.get(p,0),2)] for p in PARAMS])

# 3. atmosphere gross/captured/net
def atm(db):
    a = collections.defaultdict(lambda: collections.defaultdict(float))
    for n, d in rows(db, "unit_flow"):
        if "__atmosphere__" not in n: continue
        direc = n.split("__")[3]
        for k, x in d.items(): a[direc][k[:4]] += float(x)
    return a
ab, ag = atm(BASE), atm(GRP1)
out = []
for y in YRS:
    bt, bf = ab["to_node"].get(y,0), ab["from_node"].get(y,0)
    gt, gf = ag["to_node"].get(y,0), ag["from_node"].get(y,0)
    out.append([y, round(bt,2), round(bf,2), round(bt-bf,2),
                   round(gt,2), round(gf,2), round(gt-gf,2)])
write("co2_balance.csv", ["year","base_gross","base_captured","base_net",
                          "group1_gross","group1_captured","group1_net"], out)

# 4. carrier flows
def carrier(db):
    a = collections.defaultdict(lambda: collections.defaultdict(float))
    for n, d in rows(db, "unit_flow"):
        p = n.split("__")
        if len(p) < 5: continue
        node = p[2]; base = node.rsplit("_",1)[0] if "_" in node else node
        for k, x in d.items(): a[(base, p[3])][k[:4]] += float(x)
    return a
fb, fg = carrier(BASE), carrier(GRP1)
out = []
for key in sorted(set(fb) | set(fg), key=lambda t: (t[0], t[1])):
    r = [key[0], key[1]]
    tot = 0.0
    for y in YRS:
        bb, gg = fb[key].get(y,0.0), fg[key].get(y,0.0)
        r += [round(bb,2), round(gg,2), round(gg-bb,2)]; tot += abs(bb)+abs(gg)
    if tot > 1.0: out.append(r)
write("carrier_flows.csv", ["carrier","direction"] +
      [f"{y}_{s}" for y in YRS for s in ("base","group1","delta")], out)

# 5. steel detail
out = []
for db, lbl in ((BASE,"base"), (GRP1,"group1")):
    for n, d in rows(db, "unit_flow"):
        if "steel-" not in n or "__to_node__" not in n: continue
        p = n.split("__")
        agg = collections.defaultdict(float)
        for k, x in d.items(): agg[k[:4]] += float(x)
        if sum(agg.values()) <= 0: continue
        out.append([lbl, p[1], p[2]] + [round(agg.get(y,0.0),3) for y in YRS])
out.sort(key=lambda r: (r[2], r[1], r[0]))
write("steel_production.csv", ["run","unit","node"] + list(YRS), out)
