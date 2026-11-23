import pickle
D=pickle.load(open(r"run_logs\nb_ccslow_ccu_cap16_dac0_NLBE.pkl","rb"))
p=D["prod"];print(p.groupby(["fuel","cc"]).output.sum().round(0).to_string())
print(p.groupby(["year","sector"]).output.sum().unstack(0).round(1).to_string())
