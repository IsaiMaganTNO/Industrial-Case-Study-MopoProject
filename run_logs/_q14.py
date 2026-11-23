import pickle,re,pandas as pd
r=pickle.load(open(r"run_logs\_q_flows.pkl","rb"))
for k in ["IC1","MR"]:
  C=pd.Series(r[k]["C"]).rename("v").reset_index(); C.columns=["y","cn","node","dr","v"]; C=C[(C.y==2050)&(C.dr=="to_node")]
  t=C[C.cn.str.match(r"^(HC|CH4|H2|elec|MeOH)_(NL|BE)\w*__[a-z\-]+_")]
  t=t[t.node==t.cn.str.split("__").str[-1]]  # flow back? keep only into transport node
  t=C[C.cn.str.match(r"^(HC|CH4|H2|elec|MeOH)_(NL|BE)\w*__[a-z\-]+_") & ~C.node.str.match(r"^(HC|CH4|H2|elec|MeOH)_")]
  g=t.assign(car=t.cn.str.split("_").str[0], mode=t.cn.str.split("__").str[1].str.replace(r"_\w+$","",regex=True)).groupby(["car","mode"]).v.sum()/1e3
  print(k,"transport consumption TWh by carrier:",g.groupby(level=0).sum().round(1).to_dict())
  print("  top:",g.sort_values(ascending=False).head(8).round(1).to_dict())
