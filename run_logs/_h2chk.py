import sys; sys.argv=["x","none"]; sys.path.insert(0,"tools")
import make_slides_ctry as M, pandas as pd, re
for k,d in M.BAL.items():
  x=d[(d.car=="H2")&(d.year==2050)&(d.kind=="unit")].copy(); x["g"]=x.obj.str.replace(r"_(BE|NL)C\d+$","",regex=True)
  print(k,"sup",(x[x.dir=="to_node"].groupby("g").v.sum()/1e3).round(1).to_dict())
  u=(x[x.dir=="from_node"].groupby("g").v.sum()/1e3); print(k,"use top",u[u>0.5].round(1).to_dict())
