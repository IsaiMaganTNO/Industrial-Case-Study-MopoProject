import sqlite3, json, collections, os

def rep_weights(model_db):
    """day-of-year -> weight (days represented), read from the model, not assumed."""
    c = sqlite3.connect(model_db)
    q = """SELECT e.name, pd.name, pv.value FROM parameter_value pv
           JOIN entity e ON e.id=pv.entity_id
           JOIN entity_class ec ON ec.id=e.class_id
           JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
           WHERE ec.name='temporal_block' AND e.name LIKE 'representative_period%'
             AND pd.name IN ('weight','block_start')"""
    tmp = collections.defaultdict(dict)
    for n, p, v in c.execute(q):
        s = v.decode(errors="replace") if isinstance(v, bytes) else str(v)
        tmp[n][p] = s
    c.close()
    w = {}
    for n, d in tmp.items():
        if "weight" not in d or "block_start" not in d:
            continue
        try:
            wt = float(d["weight"])
        except Exception:
            wt = float(json.loads(d["weight"])["data"])
        bs = d["block_start"]
        ts = json.loads(bs)["data"] if bs.strip().startswith("{") else bs
        w[ts[5:10]] = wt           # 'MM-DD' -> weight
    return w

def caps(model_db, alt="medium_bio"):
    c = sqlite3.connect(model_db)
    q = """SELECT e.name, pv.value FROM parameter_value pv
           JOIN entity e ON e.id=pv.entity_id
           JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
           JOIN alternative a ON a.id=pv.alternative_id
           WHERE pd.name='storage_investment_count_max_cumulative'
             AND e.name LIKE 'biomass-stock%' AND a.name=?"""
    out = {}
    for n, v in c.execute(q, (alt,)):
        s = v.decode(errors="replace") if isinstance(v, bytes) else str(v)
        try:
            out[n.replace("biomass-stock_", "")] = float(s)
        except Exception:
            pass
    c.close()
    return out

def annual_use(result_db, w):
    """region -> year -> biomass withdrawn per YEAR (weighted to a full year)."""
    c = sqlite3.connect(result_db)
    q = """SELECT e.name, pv.value FROM parameter_value pv
           JOIN entity e ON e.id=pv.entity_id
           JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
           WHERE pd.name='connection_flow' AND e.name LIKE '%biomass-stock%to_node%'"""
    use = collections.defaultdict(lambda: collections.defaultdict(float))
    for n, v in c.execute(q):
        reg = n.split("__")[1].replace("biomass-stock_", "")
        s = v.decode(errors="replace") if isinstance(v, bytes) else str(v)
        d = json.loads(s[s.index("{"):])["data"]
        for ts, val in d.items():
            wt = w.get(ts[5:10])
            if wt is None:
                continue
            use[reg][int(ts[:4])] += float(val) * wt
    c.close()
    return use

RUNS = [
    ("summer BASE",  "checkpoints/Final_SpineOpt_Model.tiny.summer.sqlite",
                     "checkpoints/Investment_Results.summer_gurobi.sqlite"),
    ("3rep",         "checkpoints/Final_SpineOpt_Model.tiny.3rep.sqlite",
                     "checkpoints/Investment_Results.3rep_gurobi.sqlite"),
    ("summer BIOFIX","checkpoints/Final_SpineOpt_Model.tiny.biofix.summer.sqlite",
                     "checkpoints/Investment_Results.biofix_summer.sqlite"),
]
AUTHORED = caps("checkpoints/Final_SpineOpt_Model.tiny.summer.sqlite")
TOTCAP = sum(AUTHORED.values())
print("AUTHORED annual cap (medium_bio, 50%% of technical potential), system total = {:,.1f}\n".format(TOTCAP))
print("{:<16} {:>6} {:>16} {:>14} {:>10}".format("run","year","biomass used/yr","annual cap","x cap"))
for tag, mdb, rdb in RUNS:
    if not os.path.exists(rdb):
        print("{:<16} (missing)".format(tag)); continue
    w = rep_weights(mdb)
    use = annual_use(rdb, w)
    yrs = sorted({y for r in use.values() for y in r})
    for y in yrs:
        tot = sum(use[r].get(y, 0.0) for r in use)
        print("{:<16} {:>6} {:>16,.1f} {:>14,.1f} {:>9.1f}x".format(
            tag, y, tot, TOTCAP, tot/TOTCAP if TOTCAP else 0))
    print("   weights used:", {k: round(v,2) for k,v in sorted(w.items())})
