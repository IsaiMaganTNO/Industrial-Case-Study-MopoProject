import pickle, pandas as pd
R={"MR":"mr_ccslow_ccu_cap16_dac0","FRLUv4":"frlu_mr_ccslow_ccu_cap16_dac0"}
D={k:pickle.load(open(rf"run_logs\{v}_NLBE.pkl","rb")) for k,v in R.items()}
F={k:pickle.load(open(rf"run_logs\{v}.pkl","rb")) for k,v in R.items()}
pd.set_option("display.width",200)
for k in R:
  st=D[k]["co2store"]; print(k,"NL storage by year (Mt):",(st.groupby("year").co2.sum()/1e3).round(2).to_dict())
  f=F[k]["fleet"]; f=f[f.tech.str.startswith("nuclear")]; print("  nuclear GW 2050 by country:",f[f.year==2050].groupby(f.region.astype(str).str[:2]).units.sum().round(2).to_dict())
  e=F[k]["emis"]; print("  emissions 2050 by country (Mt):",(e[e.year==2050].groupby(e.region.astype(str).str[:2]).co2.sum()/1e3).round(1).to_dict())
  s=F[k]["supply"]; print("  LNG landed 2050 all (TWh):",round(s[(s.year==2050)&(s.tech=="LNG-terminal")].energy.sum()/1e3,1))
y=2050
p=pd.concat({k:D[k]["prod"][D[k]["prod"].year==y].groupby(["sector","cc"]).output.sum() for k in R},axis=1).fillna(0).round(0); print(p[p.MR!=p.FRLUv4])
