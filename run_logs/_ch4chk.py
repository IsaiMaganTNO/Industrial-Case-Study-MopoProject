import pickle, pandas as pd
pd.set_option("display.width",250)
for n in ["mr_ccslow_dac0_NLBE","nb_ccslow_ccu_cap16_dac0_NLBE"]:
    d=pickle.load(open(rf"run_logs\{n}.pkl","rb")); s=d["supply"].query("carrier=='methane' and year==2050")
    print("==",n,"gross supply by tech TWh"); print((s.groupby("tech").energy.sum()/1e3).round(1).to_string())
x=pickle.load(open(r"run_logs\mr_ccslow_dac0_xbbio.pkl","rb")); print(x.keys())
for k,v in x.items(): print(k, getattr(v,"columns",type(v))); print(v.head(3) if hasattr(v,"head") else "")
