import pickle
L="refinery (SMR+CC, internal H2)"
for n in ["nb_ccslow_ccu_cap16_dac0","nb_ctry_ccslow_ccu_cap16_dac0"]:
    for suf in ["","_NLBE"]:
        p=rf"run_logs\{n}{suf}.pkl"; d=pickle.load(open(p,"rb"))
        d["co2net"]["source"]=d["co2net"]["source"].replace("hydrogen (SMR+CC)",L); pickle.dump(d,open(p,"wb")); print(p,(d["co2net"].source==L).sum())
