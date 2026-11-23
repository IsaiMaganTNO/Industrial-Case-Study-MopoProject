import pickle
d = pickle.load(open(r"run_logs\mr_ccslow_ccu_cap16_dac0.pkl","rb"))
cp = d["co2pipe"].query("year==2050 and co2>1")
print(cp[cp.connection.str.contains("DE|DK|NO|UK")][["connection","origin","dest","co2"]].round(0).to_string())
print("all CO2 connections touching DK/NO/DE/UK:", sorted({c for c in d["co2pipe"].connection if any(x in c for x in ("DK","NO"))}))
e = d["emis"].query("year==2050 and region=='DK'"); print(e.groupby(["category","cc"]).co2.sum().round(0).to_string())
n = d["co2net"].query("year==2050 and region=='DK'"); print(n.groupby(["role","source"]).co2.sum().round(0).to_string())
print(d["co2store"].query("year==2050 and region in ['DK','NO','UK']").groupby(["region","reservoir"]).co2.sum().round(0))
