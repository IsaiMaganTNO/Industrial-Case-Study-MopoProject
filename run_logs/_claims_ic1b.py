import pickle,pandas as pd
D=pickle.load(open(r"run_logs\nb_ccslow_ccu_cap16_dac0_NLBE.pkl","rb"))
f=D["fleet"]; f=f[f.year==2050]
print(f[f.tech.str.contains("boil|H2-|PEM|MeOH|bio|methanation|nuclear|CCGT",regex=True)].groupby("tech").units.sum().round(2).to_string())
print(D["inv"].columns.tolist())
