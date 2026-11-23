import sqlite3, json, statistics, collections
c=sqlite3.connect(r"reports_3day_group1\INPUT_Final_SpineOpt_Model.tiny.3day.group1.sqlite")
alts={r[0]:r[1] for r in c.execute("SELECT id,name FROM alternative")}
q="""SELECT e.name, pv.alternative_id, pv.value FROM parameter_value pv
     JOIN entity e ON e.id=pv.entity_id
     JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
     WHERE pd.name='availability_factor'"""
res=collections.defaultdict(list)
for n,a,v in c.execute(q):
    v=v.decode() if isinstance(v,bytes) else v
    tech=n.rsplit("_",1)[0]
    try:
        d=json.loads(v)
        data=d.get("data",d)
        if isinstance(data,dict): vals=[float(x) for x in data.values()]
        elif isinstance(data,list): vals=[float(x[1]) if isinstance(x,list) else float(x) for x in data]
        else: vals=[float(data)]
    except Exception:
        try: vals=[float(v)]
        except Exception: continue
    res[(tech,alts.get(a,a))].append((n,len(vals),statistics.mean(vals)))
for k in sorted(res):
    if any(x in k[0] for x in ("wind","solar","bioST")):
        n,ln,mu=res[k][0]
        print(f"{k[0][:34]:34s} {k[1][:10]:10s} entities={len(res[k]):3d} n={ln:6d} meanCF={mu:.4f}")
