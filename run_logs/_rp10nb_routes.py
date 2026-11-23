import pickle, pandas as pd
pd.set_option("display.width", 220); pd.set_option("display.max_rows", 300)
R = {"3day": "mr_ccslow_ccu_cap16_dac0", "10day": "rp10nb_mr_ccslow_ccu_cap16_dac0"}
out = {}
for k, v in R.items():
    p = pickle.load(open(rf"run_logs\{v}_NLBE.pkl", "rb"))["prod"]
    p = p[p.region.astype(str).str[:2].isin(["NL", "BE"])]
    out[k] = p.groupby(["year", "sector", "tech"]).output.sum() / 1e3
T = pd.DataFrame(out).fillna(0); T = T[(T.abs() > 0.05).any(axis=1)]
S = T.groupby(level=[0, 1]).transform("sum"); Sh = (T / S * 100).round(1)
Sh["d"] = Sh["10day"] - Sh["3day"]
print(Sh[Sh.d.abs() >= 1].to_string())
print("\nsector totals equal?", (S.groupby(level=[0,1]).first().round(1)).to_string())
hc = pickle.load(open(r"run_logs\_hc_supply.pkl", "rb")); print("\nhc keys", type(hc), list(hc)[:10] if hasattr(hc, "__iter__") else "")
