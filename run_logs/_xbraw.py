import os,sys
sys.path.insert(0,"tools"); import postprocess as PP
from spinedb_api import DatabaseMapping
for n in ["nb_ccslow_ccu_cap16_dac0","nb_ctry_ccslow_ccu_cap16_dac0"]:
    inp=rf"runs\3day_{n}\input\Final_SpineOpt_Model.tiny.3day.{n}.sqlite"; out=rf"runs\3day_{n}\output\Investment_Results.3day_{n}.sqlite"
    w=PP.load_weights(inp); print("=====",n)
    with DatabaseMapping("sqlite:///"+os.path.abspath(out)) as db:
        for v in db.get_parameter_value_items(entity_class_name="report__connection__node__direction__stochastic_scenario", parameter_definition_name="connection_flow"):
            conn,node,d=v["entity_byname"][1:4]
            if "_CH4_FR" in conn or conn.startswith("FR_CH4_") or ("_CH4_DE" in conn and conn[:2]=="NL"):
                s=sum(x for y,x in PP.unpack_flow(v,w) if int(y)==2050)
                print(f"{conn:20s} {node:12s} {d:10s} {s/1e3:8.1f}")
