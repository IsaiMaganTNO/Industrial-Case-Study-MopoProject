import sqlite3, json
import statistics as st
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
for u in ["solar-PV-no-tracking_NLC3","wind-on-SP277-HH100_NLC3"]:
    print("="*70); print(u)
    for a,v in c.execute("""select al.name,pv.value from parameter_value pv
      join parameter_definition pd on pd.id=pv.parameter_definition_id
      join entity e on e.id=pv.entity_id
      join alternative al on al.id=pv.alternative_id
      where e.name=? and pd.name='availability_factor'""",(u,)):
        d=json.loads(bytes(v).decode())
        vals=d["data"] if isinstance(d.get("data"),list) else list(d.get("data",{}).values())
        vals=[float(x) for x in vals]
        print(f"   alt={a:14s} n={len(vals):5d} mean={st.mean(vals):.4f} max={max(vals):.3f} min={min(vals):.3f}")
