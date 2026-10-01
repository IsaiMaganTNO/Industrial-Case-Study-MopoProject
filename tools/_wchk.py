import sqlite3, json, collections
# Is postprocess summing raw hourly values without weights?
r = sqlite3.connect("checkpoints/Investment_Results.3rep_gurobi.sqlite")
q="""SELECT e.name, pv.value FROM parameter_value pv JOIN entity e ON e.id=pv.entity_id
     JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
     WHERE pd.name='unit_flow' AND e.name LIKE '%bioST%' AND e.name LIKE '%to_node%' LIMIT 3"""
for n,v in r.execute(q):
    s=v.decode(errors="replace") if isinstance(v,bytes) else str(v)
    d=json.loads(s[s.index("{"):])["data"]
    raw=sum(float(x) for x in d.values())
    byday=collections.defaultdict(float)
    for k,x in d.items(): byday[k[:10]]+=float(x)
    print("==", n[:78])
    print("   entries={}  RAW sum (no weights) = {:,.3f}".format(len(d), raw))
    print("   per-day:", {k:round(v,2) for k,v in sorted(byday.items())[:4]})
    break
r.close()
