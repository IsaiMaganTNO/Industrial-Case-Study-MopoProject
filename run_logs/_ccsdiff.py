import pickle, pandas as pd
pd.set_option("display.width",250); pd.set_option("display.max_rows",200)
P=[("nb_v2","nb_ccslow"),("nb_ctry","nb_ctry_ccslow"),("mr_fix","mr_ccslow")]
L=lambda k: pickle.load(open(rf"run_logs\{k}.pkl","rb"))
for a,b in P:
  A,B=L(a),L(b); print(f"\n===== {a} -> {b}  dObj {B['obj'].sum()-A['obj'].sum():+,.0f}")
  o=pd.concat({a:A["obj"],b:B["obj"]},axis=1); o["d"]=o[b]-o[a]; print(o.round(0))
  st=pd.concat({a:A["co2store"].groupby(["region","year"]).co2.sum(),b:B["co2store"].groupby(["region","year"]).co2.sum()},axis=1).fillna(0)/1e3
  print("CO2 stored Mt by region/year\n",st.round(2).unstack())
  e=pd.concat({a:A["emis"].groupby(["category","year"]).co2.sum(),b:B["emis"].groupby(["category","year"]).co2.sum()},axis=1).fillna(0)/1e3
  e["d"]=e[b]-e[a]; print("emis by category Mt (|d|>0.2)\n",e[e.d.abs()>0.2].round(2))
  s=pd.concat({a:A["supply"].groupby(["carrier","category","year"]).energy.sum(),b:B["supply"].groupby(["carrier","category","year"]).energy.sum()},axis=1).fillna(0)
  s["d"]=s[b]-s[a]; s=s[s.year if False else s.index.get_level_values(2)==2050] if True else s
  print("supply 2050 (|d|>2% & >1e3)\n",s[(s.d.abs()>1e3)&(s.d.abs()>0.02*s[[a,b]].max(axis=1))].sort_values("d").round(0))
  i=pd.concat({a:A["fleet"].query("year==2050").groupby("tech").units.sum(),b:B["fleet"].query("year==2050").groupby("tech").units.sum()},axis=1).fillna(0)
  i["d"]=i[b]-i[a]; print("fleet 2050 changed techs\n",i[i.d.abs()>0.05*i[[a,b]].max(axis=1).clip(lower=0.01)].sort_values("d").round(2).to_string())
