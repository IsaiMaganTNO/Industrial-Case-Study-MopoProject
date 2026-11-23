import sys, re, collections, pickle; sys.path.insert(0,"tools"); import postprocess as PP
from spinedb_api import DatabaseMapping
R={"IC1":"nb_ccslow","CTRY":"nb_ctry_ccslow","MR":"mr_ccslow_dac0"}
CARS=("CH4","H2","MeOH","HC","bio","heat","elec","CO2","atmosphere","global-H2","fossil-CH4","crude","NH3")
res={}
for k,n in R.items():
  inp=rf"runs\3day_{n}\input\Final_SpineOpt_Model.tiny.3day.{n}.sqlite"; w=PP.load_weights(inp)
  U=collections.defaultdict(float); C=collections.defaultdict(float); S=collections.defaultdict(float)
  with DatabaseMapping("sqlite:///"+rf"runs\3day_{n}\output\Investment_Results.3day_{n}.sqlite") as db:
    for x in db.get_parameter_value_items(entity_class_name="report__unit__node__direction__stochastic_scenario", parameter_definition_name="unit_flow"):
      u,node,dr=x["entity_byname"][1:4]
      car=re.sub(r"_(BE|NL|DE|DK|NO|UK)\w*$","",node)
      fam=re.sub(r"_(BE|NL|DE|DK|NO|UK)\w*$","",u)
      m=re.search(r"_((BE|NL|DE|DK|NO|UK))\w*$",u); c=m.group(1) if m else "?"
      for y,v in PP.unpack_flow(x,w): U[(int(y),c,car,dr,fam)]+=v
    for x in db.get_parameter_value_items(entity_class_name="report__connection__node__direction__stochastic_scenario", parameter_definition_name="connection_flow"):
      cn,node,dr=x["entity_byname"][1:4]
      for y,v in PP.unpack_flow(x,w): C[(int(y),cn,node,dr)]+=v
    for x in db.get_parameter_value_items(parameter_definition_name="node_state"):
      nd=x["entity_byname"][1] if len(x["entity_byname"])>1 else x["entity_byname"][0]
      if "cavern" in nd.lower() or "salt" in nd.lower():
        vals=[float(a) for a in x["parsed_value"].values]; S[nd]=(max(vals),min(vals))
  res[k]=dict(U=U,C=C,S=S)
pickle.dump(res,open(r"run_logs\_q_flows.pkl","wb")); print({k:len(v["U"]) for k,v in res.items()})
