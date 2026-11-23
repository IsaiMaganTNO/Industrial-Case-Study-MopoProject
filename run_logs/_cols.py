import pickle
d=pickle.load(open(r"run_logs\nb_ccslow_ccu_cap16_dac0.pkl","rb"))
for k in ["inv","fleet","prod","supply","co2store","co2net","atm"]:
    print(k, list(d[k].columns)); print(d[k].head(3).to_string())
