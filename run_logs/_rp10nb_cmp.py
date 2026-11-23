import pickle, pandas as pd
pd.set_option("display.width", 200); pd.set_option("display.max_rows", 200)
R = {"3day": "mr_ccslow_ccu_cap16_dac0", "10day": "rp10nb_mr_ccslow_ccu_cap16_dac0"}
F = {k: pickle.load(open(rf"run_logs\{v}.pkl", "rb")) for k, v in R.items()}
N = {k: pickle.load(open(rf"run_logs\{v}_NLBE.pkl", "rb")) for k, v in R.items()}
X = {k: pd.read_pickle(rf"run_logs\{v}_xbbio.pkl") for k, v in R.items()}
def nlbe(df): return df[df.region.astype(str).str[:2].isin(["NL", "BE"])]
rows = {}
for k in R:
    D, M = F[k], N[k]; s = nlbe(D["supply"].query("year==2050"))
    r = {}
    r["objective (M€)"] = D["obj"].sum()
    r["offshore wind TWh"] = M["supply"].query("year==2050 and category=='wind offshore'").energy.sum() / 1e3
    r["onshore wind TWh"] = s[s.category == "wind onshore"].energy.sum() / 1e3
    r["solar TWh"] = s[s.category.astype(str).str.contains("solar|PV", case=False)].energy.sum() / 1e3
    r["electrolysis H2 TWh"] = s[(s.carrier == "hydrogen") & (s.category == "electrolysis")].energy.sum() / 1e3
    h = s[s.carrier == "heat"].groupby("category").energy.sum() / 1e3
    for c, v in h.items():
        if v > 1: r[f"heat: {c} TWh"] = v
    cap = nlbe(D["co2net"].query("year==2050 and role=='captured'")).co2.sum() / 1e3
    r["CO2 captured NL+BE Mt"] = cap
    cp = D["co2pipe"].query("year==2050").assign(o=lambda x: x.origin.str[:2], d=lambda x: x.dest.str[:2])
    cp = cp[cp.o != cp.d].groupby(["o", "d"]).co2.sum() / 1e3
    r["CO2 NL+BE->UK Mt"] = sum(cp.get((c, "UK"), 0) for c in ("NL", "BE"))
    st = D["co2store"].query("year==2050"); st = st.groupby(st.region.str[:2]).co2.sum() / 1e3
    for c, v in st.items(): r[f"CO2 stored {c} Mt"] = v
    xb = X[k]["xb"].query("year==2050").groupby(["car", "o", "d"]).v.sum() / 1e3
    for car in ["elec", "H2", "CH4"]:
        s2 = xb.get(car, pd.Series(dtype=float))
        ex = sum(v for (o, d), v in s2.items() if o in ("NL", "BE") and d not in ("NL", "BE"))
        im = sum(v for (o, d), v in s2.items() if d in ("NL", "BE") and o not in ("NL", "BE"))
        r[f"{car} net export NL+BE TWh"] = ex - im
    rows[k] = r
T = pd.DataFrame(rows).fillna(0); T["diff"] = T["10day"] - T["3day"]; print(T.round(1))
print("\nPROD columns:", list(N["3day"]["prod"].columns))
P = {k: N[k]["prod"].query("year==2050").groupby(["sector", "tech"]).iloc[:, -1].sum() if False else None for k in R}
