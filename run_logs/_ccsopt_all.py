import sys, pickle, subprocess, pandas as pd
sys.path.insert(0, "tools"); import postprocess as PP
pd.set_option("display.width", 220); pd.set_option("display.max_rows", 400)
o = open(r"run_logs\_ccsopt_all.out", "w", encoding="utf8")
def P(*a): print(*a, file=o); o.flush()
R = r"runs\3day_mr_ccsopt_ccu_dac0"; name = "mr_ccsopt_ccu_dac0"
inp = rf"{R}\Final_SpineOpt_Model.tiny.3day.{name}.sqlite"; out = rf"{R}\output\Investment_Results.{name}.sqlite"
d = PP.load(out, wmap=PP.load_weights(inp)); pickle.dump(d, open(rf"run_logs\{name}.pkl", "wb"))
P("obj components:", d["obj"].round(0).to_dict()); P("penalties:", d["obj"].get("penalties", 0.0))
PY = sys.executable
r1 = subprocess.run([PY, r"tools\filter_pkl_countries.py", rf"run_logs\{name}.pkl", rf"run_logs\{name}_NLBE.pkl", "NL,BE"], capture_output=True, text=True)
r2 = subprocess.run([PY, r"tools\extract_xb_bio.py", "OPT", inp, out, rf"run_logs\{name}_xbbio.pkl"], capture_output=True, text=True)
P("filter rc", r1.returncode, r1.stderr[-300:], "| xb rc", r2.returncode, r2.stdout.strip(), r2.stderr[-300:])
RUNS = {"PESS (baseline)": "mr_ccslow_ccu_cap16_dac0", "OPT": name}
F = {k: pickle.load(open(rf"run_logs\{v}.pkl", "rb")) for k, v in RUNS.items()}
N = {k: pickle.load(open(rf"run_logs\{v}_NLBE.pkl", "rb")) for k, v in RUNS.items()}
X = {k: pd.read_pickle(rf"run_logs\{v}_xbbio.pkl") for k, v in RUNS.items()}
nlbe = lambda df: df[df.region.astype(str).str[:2].isin(["NL", "BE"])]
for Y in (2030, 2040, 2050):
    rows = {}
    for k in RUNS:
        D, M = F[k], N[k]; yy = Y if Y in set(D["supply"].year) else Y + 1
        s = nlbe(D["supply"].query("year==@yy")); r = {}
        r["objective"] = D["obj"].sum()
        r["offshore wind NL+BE TWh"] = M["supply"].query("year==@yy and category=='wind offshore'").energy.sum() / 1e3
        r["electrolysis H2 NL+BE TWh"] = s[(s.carrier == "hydrogen") & (s.category == "electrolysis")].energy.sum() / 1e3
        for c, v in (s[s.carrier == "heat"].groupby("category").energy.sum() / 1e3).items():
            if v > 1: r[f"heat NL+BE: {c}"] = v
        cn = D["co2net"].query("year==@yy"); cn = cn.assign(c=cn.region.astype(str).str[:2])
        for c, v in (cn[cn.role == "captured"].groupby("c").co2.sum() / 1e3).items(): r[f"CO2 captured {c}"] = v
        st = D["co2store"].query("year==@yy")
        for c, v in (st.groupby(st.region.str[:2]).co2.sum() / 1e3).items(): r[f"CO2 stored {c}"] = v
        em = D["emis"].query("year==@yy")
        for c, v in (em.groupby(em.region.str[:2]).co2.sum() / 1e3).items(): r[f"net emis {c}"] = v
        cp = D["co2pipe"].query("year==@yy").assign(o=lambda x: x.origin.str[:2], d=lambda x: x.dest.str[:2])
        for (a, b), v in (cp[cp.o != cp.d].groupby(["o", "d"]).co2.sum() / 1e3).items():
            if v > .5: r[f"CO2 {a}->{b}"] = v
        xb = X[k]["xb"].query("year==@yy").groupby(["car", "o", "d"]).v.sum() / 1e3
        for car in ["elec", "H2", "CH4"]:
            s2 = xb.get(car, pd.Series(dtype=float))
            r[f"{car} net export NL+BE TWh"] = sum(v for (a, b), v in s2.items() if a in ("NL", "BE") and b not in ("NL", "BE")) - sum(v for (a, b), v in s2.items() if b in ("NL", "BE") and a not in ("NL", "BE"))
        rows[k] = r
    T = pd.DataFrame(rows).fillna(0); T["diff"] = T["OPT"] - T["PESS (baseline)"]
    P(f"\n== KPI {Y}"); P(T.round(1).to_string())
P("\n== CO2 use 2050 by country: injection vs CCU (Mt)")
for k in RUNS:
    cn = F[k]["co2net"].query("year==2050 and role=='used / injected'")
    inj = cn.tech.astype(str).str.contains("inject|storage|CCS_", case=False)
    P(k, cn.assign(c=cn.region.astype(str).str[:2], kind=inj.map({True: "inject", False: "CCU"})).groupby(["c", "kind"]).co2.sum().div(1e3).round(2).to_dict())
out_ = {}
for k in RUNS:
    p = nlbe(N[k]["prod"]); out_[k] = p.groupby(["year", "sector", "tech"]).output.sum() / 1e3
T = pd.DataFrame(out_).fillna(0); T = T[(T.abs() > .05).any(axis=1)]
Sh = (T / T.groupby(level=[0, 1]).transform("sum") * 100).round(1)
Sh = Sh[(Sh["OPT"] - Sh["PESS (baseline)"]).abs() >= 5]
P("\n== Industry route shares NL+BE (%), rows changing >=5pp"); P(Sh.to_string())
P("DONE")
