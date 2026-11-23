import pickle,re,pandas as pd; pd.set_option("display.width",250); pd.set_option("display.max_rows",400)
r=pickle.load(open(r"run_logs\_q_flows.pkl","rb"))
for k,d in r.items():
  df=pd.Series(d["U"]).rename("v").reset_index(); df.columns=["y","c","car","dr","fam","v"]
  df=df[(df.y==2050)&df.c.isin(["NL","BE"])]
  print("=====",k)
  # heat node consumers / producers
  h=(df[df.car=="heat"].groupby(["dr","fam"]).v.sum()/1e3).round(1); print("-- heat"); print(h[h.abs()>0.5].to_string())
  b=(df[df.car=="bio"].groupby(["dr","fam","c"]).v.sum()/1e3).round(1); print("-- bio"); print(b[b.abs()>0.3].to_string())
  # pulp/paper/glass inputs
  pp=(df[df.fam.str.contains("pulp|paper|^\(EL\)-CC|^\(H2\)-CC|^\(NG\)-CC|MOE|DRI", regex=True) & (df.dr=="from_node")].groupby(["fam","c","car"]).v.sum()/1e3).round(2); print("-- pulp/paper/glass/steel inputs"); print(pp[pp.abs()>0.01].to_string())
  C=pd.Series(d["C"]).rename("v").reset_index(); C.columns=["y","cn","node","dr","v"]
  C=C[(C.y==2050)&(C.dr=="to_node")]
  cc=C[C.cn.str.contains("elec",case=False)]
  ext=cc[~cc.cn.str.match(r"^(NL|BE)\w*_elec_(NL|BE)")]
  print("-- elec connections not NL/BE<->NL/BE:", ext.cn.unique()[:20])
  print("-- storage node_state ranges:", dict(list(d["S"].items())[:10]))
