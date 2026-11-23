from spinedb_api import DatabaseMapping
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.gascap.vre15.sqlite"
tgt=[f"nuclear-3_{c}{i}" for c,n in [("BEC",8),("NLC",9)] for i in range(1,n+1)]
with DatabaseMapping("sqlite:///"+db) as m:
    seen={}
    for pv in m.get_parameter_value_items(entity_class_name="unit"):
        n=pv["entity_byname"][0]
        if n in tgt:
            seen.setdefault(pv["parameter_definition_name"],{})[n]=(pv["parsed_value"],pv["alternative_name"])
    for p,d in sorted(seen.items()):
        vals={k:v[0] for k,v in d.items()}
        uniq=set(str(v) for v in vals.values())
        print(f"{p:42} n={len(vals):2} distinct={len(uniq)}")
        if len(uniq)>1:
            for k in sorted(vals): print("      ",k,vals[k],d[k][1])
