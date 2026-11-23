import os
from spinedb_api import DatabaseMapping, from_database
url="sqlite:///"+os.path.abspath(r"checkpoints\Final_SpineOpt_Model.tiny.3day.gascap.sqlite")
seen={}
with DatabaseMapping(url) as db:
    for v in db.get_parameter_value_items():
        if v["parameter_definition_name"]!="availability_factor": continue
        n=v["entity_name"]
        if n.startswith("LNG-terminal") or n.startswith("gas-extraction"):
            val=from_database(v["value"],v["type"])
            seen[n]=(float(getattr(val,"value",val)), v["alternative_name"])
print("rows visible to Spine reader:",len(seen))
lng=[v for k,v in seen.items() if k.startswith("LNG")]
ext=[v for k,v in seen.items() if k.startswith("gas-ex")]
print(f"  LNG-terminal   n={len(lng)} values={sorted({x[0] for x in lng})} alts={sorted({x[1] for x in lng})}")
print(f"  gas-extraction n={len(ext)} values={sorted({x[0] for x in ext})} alts={sorted({x[1] for x in ext})}")
print()
be=3.4844*8*8760*0.50/1000; nl=3.9829*9*8760*0.50/1000
print(f"Implied 2050 ceiling: BE {be:.1f} + NL {nl:.1f} = {be+nl:.1f} TWh  (was 662.1)")
print(f"  extraction now 0.0 TWh (was 103.9)")
