import pickle,numpy as np,re
from spinedb_api import from_database,DatabaseMapping
def get(p,par,alt,pat):
  out={}
  with DatabaseMapping("sqlite:///"+p.replace("\\","/")) as m:
    for v in m.get_parameter_value_items(parameter_definition_name=par):
      e="__".join(v["entity_byname"])
      if v["alternative_name"]==alt and re.search(pat,e):
        x=from_database(v["value"],v["type"]); out[e]=[round(float(y),4) for y in getattr(x,"values",[x])]
  return out
A=r"runs\3day_nn_fix\input\Final_SpineOpt_Model.tiny.3day.nn_fix.sqlite";B=r"checkpoints\Final_SpineOpt_Model.tiny.3day.mr_fix.sqlite"
for par,alt,pat in [("storage_investment_count_initial_cumulative","medium_bio",r"^biomass-stock_"),("storage_investment_count_max_cumulative","Base",r"^atmosphere$"),("storage_investment_count_fix_cumulative","high_CO2",r"^CO2-storage-"),("availability_factor","Base",r"^LNG-terminal_"),("investment_count_max_cumulative","Base",r"^DAC_")]:
  a=get(A,par,alt,pat);b=get(B,par,alt,pat)
  sa=sum(v[0] for v in a.values()); sb_nb=sum(v[0] for k,v in b.items() if re.search(r"(BE|NL)C\d|NSNL|NSBE",k)); sb=sum(v[0] for v in b.values())
  print(par,alt,"| nn_fix n",len(a),"sum",round(sa,3),"| mr_fix n",len(b),"NL+BE sum",round(sb_nb,3),"all",round(sb,3))
  if len(b)<8: print("   A",a,"\n   B",b)
