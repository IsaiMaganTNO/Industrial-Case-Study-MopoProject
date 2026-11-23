import re
from spinedb_api import DatabaseMapping,from_database
def get(p):
  o={}
  with DatabaseMapping("sqlite:///"+p.replace("\\","/")) as m:
    for v in m.get_parameter_value_items(parameter_definition_name="storage_investment_count_initial_cumulative",alternative_name="medium_bio"):
      e=v["entity_byname"][0]
      if re.search(r"(BE|NL)C\d",e): o[e]=float(from_database(v["value"],v["type"]))
  return o
A=get(r"runs\3day_nn_fix\input\Final_SpineOpt_Model.tiny.3day.nn_fix.sqlite");B=get(r"checkpoints\Final_SpineOpt_Model.tiny.3day.mr_fix.sqlite")
for k in sorted(A): print(f"{k:22s} {A[k]:9.3f} {B.get(k,0):9.3f}  x{B.get(k,0)/A[k]:.2f}  TWh/yr nn={A[k]*365:.0f} mr={B.get(k,0)*365:.0f}")
print("BE",sum(v for k,v in A.items() if "BE" in k)*365, sum(v for k,v in B.items() if "BE" in k)*365)
print("NL",sum(v for k,v in A.items() if "NL" in k)*365, sum(v for k,v in B.items() if "NL" in k)*365)
