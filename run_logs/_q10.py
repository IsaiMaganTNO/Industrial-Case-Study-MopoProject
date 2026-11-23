import pickle,re,pandas as pd
r=pickle.load(open(r"run_logs\_q_flows.pkl","rb"))
for k,d in r.items():
  U=pd.Series(d["U"]).rename("v").reset_index(); U.columns=["y","c","car","dr","fam","v"]; U=U[(U.y==2050)&U.c.isin(["NL","BE"])]
  ch4=U[U.car=="CH4"]; sup=ch4[ch4.dr=="to_node"].groupby("fam").v.sum(); use=ch4[ch4.dr=="from_node"].groupby("fam").v.sum()
  syn=sup.get("methanation",0)/sup.sum()
  capt={f for f in U[(U.car=="CO2")&(U.dr=="to_node")].fam}
  unab=use[[f for f in use.index if f not in capt]].sum()
  print(f"{k}: CH4 supply {sup.sum()/1e3:.0f} TWh (synthetic {syn:.0%}); unabated CH4 use {unab/1e3:.0f} TWh -> uncounted CO2 ~{0.2*syn*unab/1e6:.1f} Mt; CO2->methanation {U[(U.car=='CO2')&(U.fam=='methanation')].v.sum()/1e3:.1f} Mt")
  C=pd.Series(d["C"]).rename("v").reset_index(); C.columns=["y","cn","node","dr","v"]; C=C[C.y==2050]
  cv=C[C.cn.str.contains("cavern")&(C.dr=="to_node")]
  print("   cavern conn flows TWh:",(cv.groupby(cv.node.str.startswith("salt")).v.sum()/1e3).round(1).to_dict(), "max state:",{a:round(b[0],1) for a,b in d["S"].items() if b[0]>0.5})
