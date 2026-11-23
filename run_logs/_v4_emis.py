import pickle, pandas as pd
R={"MR":"mr_ccslow_ccu_cap16_dac0","V4":"frlu_mr_ccslow_ccu_cap16_dac0"}
D={k:pickle.load(open(rf"run_logs\{v}_NLBE.pkl","rb")) for k,v in R.items()}
e=pd.concat({k:D[k]["emis"].query("year==2050").assign(c=lambda z:z.region.astype(str).str[:2]).groupby(["c","category"]).co2.sum()/1e3 for k in R},axis=1).fillna(0).round(1)
e["d"]=e.V4-e.MR; print(e[e.d.abs()>0.5].sort_values("d"))
c=pd.concat({k:D[k]["co2net"].query("year==2050 and role=='captured'").groupby("source").co2.sum()/1e3 for k in R},axis=1).fillna(0).round(1); print(c)
for k in R:
  s=D[k]["supply"].query("year==2050 and carrier=='heat' and energy>0"); print(k,"bio heat",round(s[s.tech.str.startswith("bio")].energy.sum()/1e3,1),"HP",round(s[s.tech.str.contains("heatpump")].energy.sum()/1e3,1))
