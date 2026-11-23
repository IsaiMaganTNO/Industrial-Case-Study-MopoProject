import sqlite3, json, collections, statistics
c=sqlite3.connect(r"reports_3day_group1\INPUT_Final_SpineOpt_Model.tiny.3day.group1.sqlite")
q="""SELECT e.name, pv.value FROM parameter_value pv
     JOIN entity e ON e.id=pv.entity_id
     JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
     WHERE pd.name='unit_availability_factor' AND pv.alternative_id=1"""
rows=list(c.execute(q))
print("unit_availability_factor rows:",len(rows))
for n,v in rows:
    base=n.rsplit("_",1)[0]
    if not any(k in n for k in ("wind-on-SP277-HH100_NLC6","wind-off-FB-SP370-HH155_NSNL011","solar-PV-no-tracking_NLC6","bioST_NLC6")): continue
    v=v.decode() if isinstance(v,bytes) else v
    try:
        d=json.loads(v)["data"]
        vals=[float(x) for x in d.values()]
        print(f"{n:36s} n={len(vals):5d} mean={statistics.mean(vals):.4f} min={min(vals):.3f} max={max(vals):.3f}")
    except Exception as e:
        print(f"{n:36s} scalar {v[:40]}")
