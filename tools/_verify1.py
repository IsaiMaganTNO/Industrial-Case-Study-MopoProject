import sqlite3, json, collections
r = sqlite3.connect("checkpoints/Investment_Results.3rep_gurobi.sqlite")
q="""SELECT e.name, pv.value FROM parameter_value pv JOIN entity e ON e.id=pv.entity_id
     JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
     WHERE pd.name='connection_flow' AND e.name LIKE '%biomass-stock_BEC1%to_node%'"""
W={'01-12':108.49,'02-18':154.0,'08-19':102.51}
for n,v in r.execute(q):
    s=v.decode(errors="replace") if isinstance(v,bytes) else str(v)
    d=json.loads(s[s.index("{"):])["data"]
    byday=collections.defaultdict(float)
    for k,x in d.items(): byday[k[:10]]+=float(x)
    print("BEC1 withdrawal per representative day:")
    for k in sorted(byday):
        if byday[k]>0: print("   {}  {:>10,.3f}  x weight {:>6}".format(k, byday[k], W.get(k[5:10],'-')))
    y2030=sum(byday[k]*W.get(k[5:10],0) for k in byday if k[:4]=='2030')
    print("\n   2030 weighted annual = {:,.1f}".format(y2030))
    print("   cap (annual)         = 1,088.07")
    print("   ratio                = {:.1f}x".format(y2030/1088.0673))
    break
r.close()
