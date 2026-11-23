import pickle,pandas as pd; pd.set_option("display.width",250); pd.set_option("display.max_rows",400)
r=pickle.load(open(r"run_logs\_q_flows.pkl","rb"))
for k,d in r.items():
  df=pd.Series(d["U"]).rename("v").reset_index(); df.columns=["y","c","car","dr","fam","v"]
  df=df[(df.y==2050)&df.c.isin(["NL","BE"])]
  print("=====",k)
  for car in ["CH4","H2","MeOH","HC","bio"]:
    x=(df[df.car==car].groupby(["dr","fam"]).v.sum()/1e3).round(1); x=x[x.abs()>0.3]
    print("--",car,"(TWh)"); print(x.to_string())
