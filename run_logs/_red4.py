import pickle,re
from spinedb_api import DatabaseMapping,from_database
A,B=pickle.load(open(r"run_logs\_red_ents.pkl","rb"))
print([e for e in B if e[0] in("user_constraint","unit__user_constraint")][:10])
print([e for e in B if e[0]=="investment_group"])
for p in [r"runs\3day_nn_fix\input\Final_SpineOpt_Model.tiny.3day.nn_fix.sqlite",r"checkpoints\Final_SpineOpt_Model.tiny.3day.mr_fix.sqlite"]:
  with DatabaseMapping("sqlite:///"+p.replace("\\","/")) as m:
    w={}
    for v in m.get_parameter_value_items(entity_class_name="temporal_block"):
      x=from_database(v["value"],v["type"]); w[(v["entity_byname"][0],v["parameter_definition_name"],v["alternative_name"])]=str(getattr(x,"values",x))[:80]
    print(p.split("\\")[-1],len(w)); pickle.dump(w,open(r"run_logs\_tb_"+("nn" if "nn_fix" in p else "mr")+".pkl","wb"))
a=pickle.load(open(r"run_logs\_tb_nn.pkl","rb"));b=pickle.load(open(r"run_logs\_tb_mr.pkl","rb"))
print("temporal_block params differ:",[(k,a.get(k),b.get(k)) for k in set(a)|set(b) if a.get(k)!=b.get(k)][:10])
