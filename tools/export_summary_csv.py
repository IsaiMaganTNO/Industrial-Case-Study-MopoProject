r"""Export summary CSVs (per country and year) for a set of runs.
Usage: python tools/export_summary_csv.py OUTDIR name1[:label1] name2[:label2] ...
Reads run_logs/<name>.pkl and run_logs/<name>_xbbio.pkl. Units: TWh, GW, Mt CO2, output units (industry).
Writes per run and a combined long table with a 'run' column.
"""
import os, re, sys, pickle
import pandas as pd
sys.path.insert(0, "tools"); import plot_run_summary as S
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
runs = [a.split(":", 1) if ":" in a else (a, a) for a in sys.argv[2:]]
SITE = re.compile(r"(?:NS|BS|AT|AS)([A-Z]{2})")
def country(region, name=""):
    r = "" if pd.isna(region) else str(region)
    if r: return r[:2]
    m = SITE.search(str(name)); return m.group(1) if m else "offshore/other"
def add_c(df, namecol="tech"):
    return df.assign(country=[country(r, n) for r, n in zip(df.region, df[namecol])])
T = {}
for name, label in runs:
    d = pickle.load(open(rf"run_logs\{name}.pkl", "rb")); xb = pd.read_pickle(rf"run_logs\{name}_xbbio.pkl")["xb"]
    t = {}
    o = d["obj"].rename("value").reset_index().rename(columns={"index": "cost_component"}); o.loc[len(o)] = ["TOTAL", o.value.sum()]; t["objective"] = o
    s = add_c(d["supply"][d["supply"].energy > 0])
    t["energy_supply_by_category_TWh"] = (s.groupby(["country", "year", "carrier", "category"]).energy.sum() / 1e3).rename("TWh").reset_index()
    t["energy_supply_by_tech_TWh"] = (s.groupby(["country", "year", "carrier", "tech"]).energy.sum() / 1e3).rename("TWh").reset_index()
    t["electricity_mix_TWh"] = t["energy_supply_by_category_TWh"].query("carrier=='electricity'").pivot_table(index=["country", "year"], columns="category", values="TWh", fill_value=0).reset_index()
    t["heat_mix_TWh"] = t["energy_supply_by_category_TWh"].query("carrier=='heat'").pivot_table(index=["country", "year"], columns="category", values="TWh", fill_value=0).reset_index()
    t["hydrogen_supply_TWh"] = t["energy_supply_by_category_TWh"].query("carrier=='hydrogen'").pivot_table(index=["country", "year"], columns="category", values="TWh", fill_value=0).reset_index()
    f = add_c(d["fleet"]); f["tech_group"] = f.tech.str.replace(r"_(NS|BS|AT|AS)\w+$", "", regex=True)
    t["capacity_GW"] = f.groupby(["country", "year", "category", "tech_group"]).units.sum().rename("GW_or_units").reset_index()
    i = add_c(d["inv"]); i["tech_group"] = i.tech.str.replace(r"_(NS|BS|AT|AS)\w+$", "", regex=True)
    t["new_investment_GW"] = i.groupby(["country", "year", "category", "tech_group"]).units.sum().rename("GW_or_units").reset_index()
    e = add_c(d["emis"])
    t["co2_emissions_by_category_Mt"] = (e.groupby(["country", "year", "category"]).co2.sum() / 1e3).rename("Mt").reset_index()
    c = add_c(d["co2net"])
    t["co2_captured_by_source_Mt"] = (c[c.role == "captured"].groupby(["country", "year", "source"]).co2.sum() / 1e3).rename("Mt").reset_index()
    st = d["co2store"].assign(country=[country(None, r) for r in d["co2store"].reservoir])
    t["co2_stored_by_site_Mt"] = (st.groupby(["country", "reservoir", "year"]).co2.sum() / 1e3).rename("Mt").reset_index()
    p = add_c(d["prod"]); p["route"] = p.tech.map(S.route_label)
    q = p.groupby(["country", "year", "sector", "route", "cc"]).output.sum().rename("output").reset_index()
    q["share_pct"] = 100 * q.output / q.groupby(["country", "year", "sector"]).output.transform("sum"); t["industry_routes"] = q
    x = xb.groupby(["car", "o", "d", "year"]).v.sum().reset_index().rename(columns={"car": "carrier", "o": "from_country", "d": "to_country", "v": "flow"})
    x["unit"] = x.carrier.map({"CO2": "kt", "elec": "GWh", "H2": "GWh", "CH4": "GWh"}); t["cross_border_flows"] = x
    # headline per country/year
    yrs = sorted(e.year.unique()); rows = []
    for (cc, y), _ in s.groupby(["country", "year"]):
        g = lambda df, col, **kw: df[(df.country == cc) & (df.year == y)].pipe(lambda z: z.query(" and ".join(f"{k}=={v!r}" for k, v in kw.items())) if kw else z)[col].sum()
        rows.append(dict(country=cc, year=y,
            net_co2_Mt=g(e, "co2") / 1e3, co2_captured_Mt=g(c[c.role == "captured"], "co2") / 1e3, co2_stored_Mt=g(st, "co2") / 1e3,
            elec_TWh=g(s, "energy", carrier="electricity") / 1e3, elec_wind_offshore_TWh=g(s, "energy", carrier="electricity", category="wind offshore") / 1e3,
            elec_wind_onshore_TWh=g(s, "energy", carrier="electricity", category="wind onshore") / 1e3, elec_solar_TWh=g(s, "energy", carrier="electricity", category="solar PV") / 1e3,
            h2_TWh=g(s, "energy", carrier="hydrogen") / 1e3, h2_electrolysis_TWh=g(s, "energy", carrier="hydrogen", category="electrolysis") / 1e3,
            methane_TWh=g(s, "energy", carrier="methane") / 1e3, heat_TWh=g(s, "energy", carrier="heat") / 1e3,
            heat_heatpumps_TWh=g(s, "energy", carrier="heat", category="electrification (heat pumps)") / 1e3, heat_bio_TWh=g(s, "energy", carrier="heat", category="bioenergy") / 1e3,
            heat_fossil_TWh=g(s, "energy", carrier="heat", category="unabated fossil") / 1e3,
            nuclear_GW=f[(f.country == cc) & (f.year == y) & f.tech.str.startswith("nuclear")].units.sum(),
            pem_GW=f[(f.country == cc) & (f.year == y) & f.tech.str.startswith("PEM")].units.sum()))
    t["headline_by_country"] = pd.DataFrame(rows)
    rd = os.path.join(out, name); os.makedirs(rd, exist_ok=True)
    for k, v in t.items():
        v.to_csv(os.path.join(rd, k + ".csv"), index=False, float_format="%.4f")
        T.setdefault(k, []).append(v.assign(run=label))
    print(name, len(t), "tables")
cd = os.path.join(out, "_combined"); os.makedirs(cd, exist_ok=True)
for k, v in T.items(): pd.concat(v).to_csv(os.path.join(cd, k + ".csv"), index=False, float_format="%.4f")
print("combined", len(T))
