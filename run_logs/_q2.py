import sys, re, collections, pickle; sys.path.insert(0,"tools"); import postprocess as PP
from spinedb_api import DatabaseMapping
R={"IC1":"nb_ccslow","CTRY":"nb_ctry_ccslow","MR":"mr_ccslow_dac0"}
res={}
for k,n in R.items():
  inp=rf"runs\3day_{n}\input\Final_SpineOpt_Model.tiny.3day.{n}.sqlite"; w=PP.load_weights(inp)
  A=collections.defaultdict(float)
  with DatabaseMapping("sqlite:///"+rf"runs\3day_{n}\output\Investment_Results.3day_{n}.sqlite") as db:
    for x in db.get_parameter_value_items(entity_class_name="report__unit__node__direction__stochastic_scenario", parameter_definition_name="unit_flow"):
      u,node,dr=x["entity_byname"][1:4]
      if not (node=="atmosphere" or node.startswith("CO2_") or node.startswith("CO2-") or node.startswith("CH4_") or node.startswith("MeOH_") or node.startswith("HC_") or node.startswith("H2_")): continue
      fam=re.sub(r"_(BE|NL|DE|DK|NO|UK)\w*$","",u); car=node.split("_")[0] if node!="atmosphere" else "atm"
      reg=re.search(r"_((BE|NL|DE|DK|NO|UK))\w*$",u); c=reg.group(1) if reg else "?"
      for y,v in PP.unpack_flow(x,w):
        if int(y)==2050: A[(c,car,dr,fam)]+=v
  res[k]=A
pickle.dump(res,open(r"run_logs\_carbon_audit.pkl","wb")); print("ok")
