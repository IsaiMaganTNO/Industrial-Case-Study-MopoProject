import sqlite3, pickle, subprocess, sys, pandas as pd
pd.set_option("display.width", 220); pd.set_option("display.max_rows", 400)
o = open(r"run_logs\_ctryco2_all.out", "w", encoding="utf8")
def P(*a): print(*a, file=o); o.flush()
PY = sys.executable
R = {"MR3": ("mr_ccslow_ccu_cap16_dac0", None, None),
     "A": ("ctryco2_mr_ccslow_ccu_cap16_dac0", r"runs\ctryco2_mr", "ctryco2_mr_ccslow_ccu_cap16_dac0"),
     "B": ("ctryco2B_mr_ccslow_ccu_cap16_dac0", r"runs\ctryco2B_mr", "ctryco2B_mr_ccslow_ccu_cap16_dac0")}
# 1. DB diff A vs B
ia = rf"{R['A'][1]}\Final_SpineOpt_Model.tiny.3day.{R['A'][2]}.sqlite"; ib = rf"{R['B'][1]}\Final_SpineOpt_Model.tiny.3day.{R['B'][2]}.sqlite"
def cnt(db):
    c = sqlite3.connect(db)
    e = dict(c.execute("select ec.name, count(*) from entity e join entity_class ec on ec.id=e.class_id group by ec.name"))
    p = dict(c.execute("select pd.name, count(*) from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id group by pd.name"))
    ents = set(r[0] for r in c.execute("select name from entity"))
    return e, p, ents
ea, pa, sa = cnt(ia); eb, pb, sb = cnt(ib)
P("== DB DIFF (B - A) entities by class"); P({k: eb.get(k,0)-ea.get(k,0) for k in set(ea)|set(eb) if eb.get(k,0)!=ea.get(k,0)})
P("params by def"); P({k: pb.get(k,0)-pa.get(k,0) for k in set(pa)|set(pb) if pb.get(k,0)!=pa.get(k,0)})
P("entities only in A:", len(sa-sb), " only in B:", len(sb-sa))
ca, cb = sqlite3.connect(ia), sqlite3.connect(ib)
q = "select e.name, pd.name, a.name, pv.value from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id join alternative a on a.id=pv.alternative_id"
va = {r[:3]: r[3] for r in ca.execute(q)}; vb = {r[:3]: r[3] for r in cb.execute(q)}
P("common params with different value:", sum(1 for k in va if k in vb and va[k] != vb[k]), " removed:", len(set(va)-set(vb)))
# 2. NLBE + xbbio caches
for k, (n, rd, nm) in R.items():
    if rd is None: continue
    r1 = subprocess.run([PY, r"tools\filter_pkl_countries.py", rf"run_logs\{n}.pkl", rf"run_logs\{n}_NLBE.pkl", "NL,BE"], capture_output=True, text=True)
    r2 = subprocess.run([PY, r"tools\extract_xb_bio.py", k, rf"{rd}\Final_SpineOpt_Model.tiny.3day.{nm}.sqlite", rf"{rd}\output\Investment_Results.{nm}.sqlite", rf"run_logs\{n}_xbbio.pkl"], capture_output=True, text=True)
    P(k, "filter rc", r1.returncode, r1.stderr[-300:], "| xb rc", r2.returncode, r2.stdout.strip(), r2.stderr[-300:])
F = {k: pickle.load(open(rf"run_logs\{v[0]}.pkl", "rb")) for k, v in R.items()}
N = {k: pickle.load(open(rf"run_logs\{v[0]}_NLBE.pkl", "rb")) for k, v in R.items()}
X = {k: pd.read_pickle(rf"run_logs\{v[0]}_xbbio.pkl") for k, v in R.items()}
def nlbe(df): return df[df.region.astype(str).str[:2].isin(["NL", "BE"])]
# 3. KPI table
for Y in (2041, 2050):
    rows = {}
    for k in R:
        D, M = F[k], N[k]; yy = Y if Y in set(D["supply"].year) else 2040
        s = nlbe(D["supply"].query("year==@yy")); r = {}
        r["objective"] = D["obj"].sum(); r["obj excl penalty"] = D["obj"].drop("penalties", errors="ignore").sum()
        r["offshore wind TWh"] = M["supply"].query("year==@yy and category=='wind offshore'").energy.sum()/1e3
        r["solar TWh"] = s[s.category.astype(str).str.contains("solar|PV", case=False)].energy.sum()/1e3
        r["electrolysis H2 TWh"] = s[(s.carrier=="hydrogen")&(s.category=="electrolysis")].energy.sum()/1e3
        for c, v in (s[s.carrier=="heat"].groupby("category").energy.sum()/1e3).items():
            if v > 1: r[f"heat: {c}"] = v
        cn = D["co2net"].query("year==@yy"); cn = cn.assign(c=cn.region.astype(str).str[:2])
        for c, v in (cn[cn.role=="captured"].groupby("c").co2.sum()/1e3).items(): r[f"CO2 captured {c}"] = v
        st = D["co2store"].query("year==@yy"); 
        for c, v in (st.groupby(st.region.str[:2]).co2.sum()/1e3).items(): r[f"CO2 stored {c}"] = v
        em = D["emis"].query("year==@yy")
        for c, v in (em.groupby(em.region.str[:2]).co2.sum()/1e3).items(): r[f"net emis {c}"] = v
        cp = D["co2pipe"].query("year==@yy").assign(o=lambda x: x.origin.str[:2], d=lambda x: x.dest.str[:2])
        for (a, b), v in (cp[cp.o!=cp.d].groupby(["o","d"]).co2.sum()/1e3).items():
            if v > .5: r[f"CO2 {a}->{b}"] = v
        xb = X[k]["xb"].query("year==@yy").groupby(["car","o","d"]).v.sum()/1e3
        for car in ["elec","H2","CH4"]:
            s2 = xb.get(car, pd.Series(dtype=float))
            r[f"{car} net export NL+BE TWh"] = sum(v for (a,b),v in s2.items() if a in ("NL","BE") and b not in ("NL","BE")) - sum(v for (a,b),v in s2.items() if b in ("NL","BE") and a not in ("NL","BE"))
        rows[k] = r
    T = pd.DataFrame(rows).fillna(0); P(f"\n== KPI year {Y}"); P(T.round(1).to_string())
# 4. CCU vs storage: CO2 'used / injected' per country, injection vs other
P("\n== CO2 use 2050 by country: injection vs CCU (Mt)")
for k in R:
    cn = F[k]["co2net"].query("year==2050 and role=='used / injected'")
    inj = cn.tech.astype(str).str.contains("inject|storage|CCS_", case=False)
    t = cn.assign(c=cn.region.astype(str).str[:2], kind=inj.map({True:"inject",False:"CCU/other"})).groupby(["c","kind"]).co2.sum().div(1e3).unstack(fill_value=0)
    P(k); P(t.round(2).to_string())
    oth = cn[~inj]; P("  top CCU techs:", (oth.groupby("tech").co2.sum()/1e3).sort_values(ascending=False).head(8).round(2).to_dict())
# 5. industry routes NL+BE share
out = {}
for k in R:
    p = N[k]["prod"]; p = p[p.region.astype(str).str[:2].isin(["NL","BE"])]
    out[k] = p.groupby(["year","sector","tech"]).output.sum()/1e3
T = pd.DataFrame(out).fillna(0); T = T[(T.abs()>0.05).any(axis=1)]
Sh = (T / T.groupby(level=[0,1]).transform("sum") * 100).round(1)
Sh = Sh[((Sh["A"]-Sh["MR3"]).abs()>=5)|((Sh["B"]-Sh["MR3"]).abs()>=5)]
P("\n== Industry route shares NL+BE (%), rows changing >=5pp vs MR3"); P(Sh.to_string())
P("DONE")
