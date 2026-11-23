import os
from spinedb_api import DatabaseMapping, from_database
url="sqlite:///"+os.path.abspath(r"checkpoints\Final_SpineOpt_Model.tiny.3day.gascap.vre15.sqlite")
tot={}
n=0
with DatabaseMapping(url) as db:
    for v in db.get_parameter_value_items(parameter_definition_name="investment_count_total_max_cumulative"):
        nm=v["entity_byname"][0]
        if not (nm.startswith("wind-on_") or nm.startswith("solar-PV_")): continue
        val=float(from_database(v["value"],v["type"]))
        tech,reg=nm.rsplit("_",1)
        tot[(tech,reg[:2])]=tot.get((tech,reg[:2]),0.0)+val
        n+=1
print("rows visible to Spine reader:",n)
for k in sorted(tot): print(f"   {k[0]:9s} {k[1]} = {tot[k]:7.2f} GW")
exp={("wind-on","BE"):3.60,("wind-on","NL"):7.20,("solar-PV","BE"):12.7652,("solar-PV","NL"):33.50}
ok=all(abs(tot[k]-v)<1e-2 for k,v in exp.items()) and n==34
print("\nVERIFY:","PASS" if ok else "*** FAIL ***")
# also confirm gas patch survived
with DatabaseMapping(url) as db:
    af={v["entity_byname"][0]:float(from_database(v["value"],v["type"]))
        for v in db.get_parameter_value_items(parameter_definition_name="availability_factor")
        if v["entity_byname"][0].startswith(("LNG-terminal","gas-extraction"))}
print("gas patch still present:",len(af),"rows; LNG=",set(v for k,v in af.items() if k.startswith("LNG")),
      "extraction=",set(v for k,v in af.items() if k.startswith("gas-ex")))
