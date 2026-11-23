import sqlite3,json
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
for n in ["LNG-terminal_NLC3__CH4_NLC3","gas-extraction_NLC3__CH4_NLC3","LNG-terminal_NLC3","gas-extraction_NLC3"]:
    for p,v,a in c.execute("select pd.name,pv.value,al.name from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id join entity e on e.id=pv.entity_id join alternative al on al.id=pv.alternative_id where e.name=? and pd.name in (\"vom_cost\",\"capacity_per_unit\")",(n,)):
        s=bytes(v).decode()
        try:
            d=json.loads(s)
            if isinstance(d,dict) and isinstance(d.get("data"),dict):
                s="  ".join(f"{k[:4]}={float(x):.4f}" for k,x in d["data"].items())
        except Exception: pass
        print(f"{n:34s} {p:18s} [{a:10s}] {s[:90]}")
print()
print("=== fossil-CH4 tax_out_unit_flow (gas price proxy) ===")
r=c.execute("select pv.value from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id join entity e on e.id=pv.entity_id where e.name=\"fossil-CH4\" and pd.name=\"tax_out_unit_flow\"").fetchone()
print(bytes(r[0]).decode()[:300])
