import pickle, pandas as pd
R = {"IC1": "nb_ccslow_ccu_cap16_dac0", "CTRY": "nb_ctry_ccslow_ccu_cap16_dac0"}
S = {}
for k, v in R.items():
    p = pickle.load(open(rf"run_logs\{v}_NLBE.pkl", "rb"))["prod"].query("year==2050")
    s = p.groupby(["sector", "tech"]).output.sum(); S[k] = s / s.groupby(level=0).transform("sum") * 100
t = pd.DataFrame(S).fillna(0); t["d"] = (t.CTRY - t.IC1).abs()
m = t.groupby(level=0).d.sum() / 2
print(m.sort_values(ascending=False).round(1).head(10).to_string())
for sec in m[m > 1].index: print(sec); print(t.loc[sec].round(1)[lambda x: (x.IC1 > .5) | (x.CTRY > .5)].to_string())
