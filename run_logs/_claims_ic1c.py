import pickle
D=pickle.load(open(r"run_logs\nb_ccslow_ccu_cap16_dac0_NLBE.pkl","rb"))
f=D["fleet"]; f=f[f.year==2050]
print(f.groupby(["category","tech"]).units.sum().round(2).to_string())
