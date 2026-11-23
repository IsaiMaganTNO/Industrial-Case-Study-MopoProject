import pickle, pandas as pd
x = pickle.load(open(r"run_logs\mr_ccslow_ccu_cap16_dac0_xbbio.pkl","rb"))["xb"].query("year==2050")
g = x.groupby(["car","o","d"]).v.sum().reset_index(); g = g[g.v.abs()>1]
print(g.round(0).to_string())
d = pickle.load(open(r"run_logs\mr_ccslow_ccu_cap16_dac0.pkl","rb"))
cp = d["co2pipe"].query("year==2050"); cp["oc"]=cp.origin.str[:2]; cp["dc"]=cp.dest.str[:2]
print(cp[cp.oc!=cp.dc].groupby(["oc","dc"]).co2.sum().round(0))
e = d["emis"].query("year==2050"); print(e.groupby(e.region.str[:2]).co2.sum().round(0))
print(d["co2store"].query("year==2050").groupby("region").co2.sum().round(0))
