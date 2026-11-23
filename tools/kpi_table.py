import pickle, pandas as pd
R = {"NL+BE (IC1), isolation": "nb_ccslow_ccu_cap16_dac0", "NL+BE (NUTS-0), isolation": "nb_ctry_ccslow_ccu_cap16_dac0", "NL+BE (IC1), interconnected": "mr_ccslow_ccu_cap16_dac0"}
CN = ["NL", "BE"]; rows = {}
for col, v in R.items():
    D = pickle.load(open(rf"run_logs\{v}_NLBE.pkl", "rb")); F = pickle.load(open(rf"run_logs\{v}.pkl", "rb")); X = pd.read_pickle(rf"run_logs\{v}_xbbio.pkl")
    s = D["supply"]; s = s[(s.year == 2050) & (s.energy > 0)]
    E = lambda car, pat: s[(s.carrier == car) & s.tech.str.contains(pat, regex=True)].energy.sum() / 1e3
    x = X["xb"].query("year==2050 and car=='CH4'"); imp = x[~x.o.isin(CN) & x.d.isin(CN)].v.sum() / 1e3; exp_ = x[x.o.isin(CN) & ~x.d.isin(CN)].v.sum() / 1e3
    c = D["co2net"].query("year==2050"); cap = c[c.role == "captured"].co2.sum() / 1e3
    ccu = c[(c.role == "used / injected") & ~c.tech.str.startswith("CO2-injection")].co2.sum() / 1e3
    st = D["co2store"].query("year==2050"); ccsnl = st[st.region.astype(str).str[:2] == "NL"].co2.sum() / 1e3
    p = F["co2pipe"].query("year==2050"); nb = lambda z: z.str[:2].isin(CN)
    co2x = (p[nb(p.origin) & ~nb(p.dest)].co2.sum() - p[~nb(p.origin) & nb(p.dest)].co2.sum()) / 1e3
    net = D["emis"].query("year==2050").co2.sum() / 1e3
    def sh(sec, techs):
        q = D["prod"].query("year==2050 and sector==@sec"); return q[q.tech.isin(techs)].output.sum() / q.output.sum() * 100
    o = D["obj"]; tot = (o.sum() if hasattr(o, "sum") else sum(o.values())) / 1e3
    el = {k: E("electricity", p_) for k, p_ in [("Nuclear", "^nuclear"), ("Wind offshore", "^wind-off"), ("Wind onshore", "^wind-on"), ("Solar PV", "^solar"),
          ("Battery discharge", "^battery"), ("Biomass", "^bio"), ("Hydrogen turbines", "^CCGT-H2"), ("Hydro", "^RoR")]}
    r = {("Total system costs", "Meuro", "-"): tot}
    for k, v_ in el.items(): r[("Electricity", "TWh", k)] = v_
    r[("Electricity", "TWh", "Total production")] = sum(el.values())
    r[("Hydrogen", "TWh", "SMR (NG)")] = E("hydrogen", "SMR")
    r[("Hydrogen", "TWh", "Electrolysers")] = E("hydrogen", "^PEM|^Diaphragm|^AEC|^SOEC")
    r[("Hydrogen", "TWh", "Import (liquid)")] = E("hydrogen", "^LH2")
    r[("CH4", "TWh", "Methanation")] = E("methane", "^methanation")
    r[("CH4", "TWh", "Bio-methane")] = E("methane", "^bio")
    r[("CH4", "TWh", "LNG landed")] = E("methane", "^LNG")
    r[("CH4", "TWh", "Net pipeline import")] = imp - exp_
    r[("CH4", "TWh", "Gas used in NL+BE")] = E("methane", ".") + imp - exp_
    for k, p_ in [("Heat pumps", "heatpump(?!-cool)"), ("Gas boilers", "^gas-boiler"), ("Biomass boilers", "^bio-boiler"), ("Electric heating", "^electric-heating"), ("Hydrogen boilers", "^H2-boiler")]:
        r[("Building heat", "TWh", k)] = E("heat", p_)
    r[("CO2 captured", "Mton", "Total captured")] = cap
    r[("CO2 captured", "Mton", "CCU (methanol)")] = ccu
    r[("CO2 captured", "Mton", "CCS NL site")] = ccsnl
    r[("CO2 captured", "Mton", "CO2 exported")] = co2x
    r[("Steel route", "% of output", "MOE")] = sh("steel (primary)", ["MOE"])
    r[("Steel route", "% of output", "H2 DRI-EAF")] = sh("steel (primary)", ["(H2)DRI-EAF"])
    r[("Steel route", "% of output", "NG DRI-EAF+CCS")] = sh("steel (primary)", ["(NG)DRI-EAF-MEA"])
    r[("Ammonia route", "% of output", "Green hydrogen")] = sh("ammonia", ["(H2)NH3"])
    r[("Ammonia route", "% of output", "Biomass gasification")] = sh("ammonia", ["(BM)NH3"])
    r[("Ammonia route", "% of output", "Gas SMR + CCS")] = sh("ammonia", ["(NG)NH3-MVR-MEA-DEA"])
    r[("Emissions", "Mton", "Net emissions")] = net
    r[("Emissions", "Mton", "Gross emissions (net + captured)")] = net + cap
    rows[col] = r
t = pd.DataFrame(rows); t.index.names = ["Group", "Unit", "Item"]
t.loc[("Total system costs", "Meuro", "-"), "NL+BE (IC1), interconnected"] = float("nan")
out = r"final_runs_pessimistic_ccs\KPI_table_2050.xlsx"; t.round(1).to_excel(out); t.round(1).to_csv(out.replace(".xlsx", ".csv"))
pd.set_option("display.width", 250); print(t.round(1).to_string()); print(out)
