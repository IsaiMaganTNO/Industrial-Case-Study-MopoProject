import sys,os,glob; sys.path.insert(0,"tools"); import postprocess as P
from spinedb_api import DatabaseMapping
db=glob.glob(r"final_runs_pessimistic_ccs\1_IC1_NLBE_17zones\output\*.sqlite")[0]
mdl=glob.glob(r"final_runs_pessimistic_ccs\1_IC1_NLBE_17zones\input\*.sqlite")
w=P.load_weights(mdl[0]) if mdl else None
print("weights", w is not None)
tot={}
with DatabaseMapping("sqlite:///"+os.path.abspath(db)) as d:
    ents={e["id"]:e for e in d.get_entity_items()}
    for v in d.get_parameter_value_items():
        if v["entity_class_name"]!="report__unit__node__direction__stochastic_scenario" or v["parameter_definition_name"]!="unit_flow": continue
        bn=ents[v["entity_id"]]["entity_byname"]
        if not (bn[1].startswith("(H2)MeOH") or bn[1].startswith("(MeOH)O")): continue
        for y,x in P.unpack_flow(v,w):
            k=(bn[1][:12],bn[2].rsplit("_",1)[0],bn[3],y); tot[k]=tot.get(k,0)+x
for k in sorted(tot):
    if k[3]==2050: print(k, round(tot[k]/1e3,2))
