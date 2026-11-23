import pickle, pandas as pd
R={"MR":"mr_ccslow_ccu_cap16_dac0","NATCAP":"ctryco2B_mr_ccslow_ccu_cap16_dac0","RP10":"rp10nb_mr_ccslow_ccu_cap16_dac0","CCSOPT":"mr_ccsopt_ccu_dac0","FRLU":"frlu_mr_ccslow_ccu_cap16_dac0"}
CN=["NL","BE"]
for k,v in R.items():
  D=pickle.load(open(rf"run_logs\{v}_NLBE.pkl","rb")); X=pd.read_pickle(rf"run_logs\{v}_xbbio.pkl")["xb"]
  s=D["supply"].query("year==2050 and carrier=='methane' and energy>0"); s=s.assign(c=s.region.astype(str).str[:2])
  lng={c:round(s[(s.tech=="LNG-terminal")&(s.c==c)].energy.sum()/1e3,1) for c in CN}
  x=X.query("year==2050 and car=='CH4'"); im=x[~x.o.isin(CN)&x.d.isin(CN)].v.sum()/1e3; ex=x[x.o.isin(CN)&~x.d.isin(CN)].v.sum()/1e3
  e=D["emis"].query("year==2050"); lt=e[e.tech=="LNG-terminal"].co2.sum()/1e3
  print(f"{k:7s} LNG landed {lng}  CH4 pipe in {im:6.1f} out {ex:6.1f}  LNG-terminal CO2 {lt:5.1f} Mt  NL+BE net {e.co2.sum()/1e3:5.1f}")
