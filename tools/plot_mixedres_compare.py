"""Comparison plots: mixed-resolution run vs vre15 (NL+BE only) + spatial maps.
Inputs: run_logs/mixedres.pkl, run_logs/vre15.pkl, geodata/IC1_NWEU.geojson.
Output: reports_v2_mixedres/.  Units: energy GWh -> TWh, co2 kt -> Mt."""
import pickle, os, re
import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import geopandas as gpd

OUT = "reports_v2_mixedres"; os.makedirs(OUT, exist_ok=True)
M = pickle.load(open(r"run_logs\mixedres.pkl", "rb"))
V = pickle.load(open(r"run_logs\vre15.pkl", "rb"))

# --- plot-specific supply labels (postprocess.classify is industry-oriented: any "+CC" tech is
#     "industry: CCS-equipped", and nuclear/hydro/storage/LNG land in "other"). Relabel by tech+carrier.
def supply_label(tech, carrier):
    l = str(tech).lower()
    if "ccgt+cc" in l:                         return "gas power + CCS (CCGT+CC)"
    if "ccgt-h2" in l:                         return "hydrogen turbine (CCGT-H2)"
    if "ccgt" in l or "ocgt" in l:             return "gas power, unabated"
    if "nuclear" in l:                         return "nuclear"
    if "hydro" in l or l.startswith("ror") or "ph-discharge" in l: return "hydro (incl. pumped)"
    if "battery" in l:                         return "battery discharge"
    if "-dr" in l:                             return "EV/transport flexibility (discharge)"
    if "scpc" in l:                            return "coal power"
    if "oil-eng" in l:                         return "oil engines"
    if "waste" in l:                           return "waste incineration"
    if l.startswith("biost"):                  return "biomass power"
    if "solar" in l:                           return "solar PV"
    if "wind-off" in l:                        return "wind offshore"
    if "wind-on" in l:                         return "wind onshore"
    if "lng-terminal" in l:                    return "LNG import"
    if "gas-extraction" in l:                  return "domestic gas extraction"
    if "bio-diges-up+cc" in l:                 return "biomethane + CCS"
    if "bio-diges" in l:                       return "biomethane"
    if "methanation" in l:                     return "synthetic methane"
    if "lh2-terminal" in l:                    return "liquid H2 import"
    if "smr+cc" in l:                          return "blue H2 (SMR+CCS)"
    if "smr" in l:                             return "grey H2 (SMR)"
    if any(k in l for k in ("pem", "aec", "soec")): return "electrolysis"
    if "heatpump" in l:                        return "heat pumps"
    if "electric-heating" in l:                return "electric resistance heating"
    if "gas-boiler" in l:                      return "gas boilers"
    if "bio-boiler" in l:                      return "biomass boilers"
    if "oil-boiler" in l:                      return "oil boilers"
    if "coal-boiler" in l:                     return "coal boilers"
    return "other: " + re.sub(r"_.*$", "", str(tech))
for _d in (M, V):
    _s = _d["supply"]
    _s["category"] = [supply_label(t, c) for t, c in zip(_s.tech, _s.carrier)]
    _s["region"] = _s["region"].astype(object).where(_s["region"].notna(), "offshore")
G = gpd.read_file(r"geodata\IC1_NWEU.geojson").set_index("id")
YRS = [2030, 2040, 2050]
NB = r"^(BE|NL)C\d"

def ctry(r):
    r = str(r)
    if r in ("nan","None",""): return "offshore"
    return r[:2] if re.match(NB, r) else r
def nb(df): return df[df.region.astype(str).str.match(NB)]
def save(fig, name):
    fig.tight_layout(); fig.savefig(os.path.join(OUT, name), dpi=150); plt.close(fig); print("wrote", name)

def mix_frame(d, car):
    s = nb(d["supply"]); s = s[(s.carrier == car) & (s.energy > 0)]
    return s.groupby(["year", "category"]).energy.sum().unstack().fillna(0) / 1e3
for car in ["electricity", "methane", "hydrogen", "heat"]:
    a, b = mix_frame(V, car), mix_frame(M, car)
    cats = sorted(set(a.columns) | set(b.columns))
    a, b = a.reindex(columns=cats, fill_value=0), b.reindex(columns=cats, fill_value=0)
    fig, ax = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
    for x, df, t in [(ax[0], a, "vre15 (NL+BE only)"), (ax[1], b, "mixed-res")]:
        df.plot.bar(stacked=True, ax=x, legend=False, colormap="tab20"); x.set_title(t); x.set_ylabel("TWh/yr")
    ax[1].legend(bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=8)
    fig.suptitle(f"NL+BE gross {car} supply (incl. storage discharge)"); save(fig, f"01_NLBE_{car}_mix.png")

def tech(d, car, y=2050):
    s = nb(d["supply"]); s = s[(s.carrier == car) & (s.year == y)]
    return s.groupby("tech").energy.sum() / 1e3
for car in ["electricity", "methane"]:
    df = pd.concat([tech(V, car), tech(M, car)], axis=1, keys=["vre15", "mixed"]).fillna(0)
    df = df[(df.abs() > 1).any(axis=1)].sort_values("mixed")
    fig, ax = plt.subplots(figsize=(9, max(4, .3 * len(df))))
    df.plot.barh(ax=ax); ax.set_xlabel("TWh"); ax.set_title(f"NL+BE {car} by technology, 2050")
    save(fig, f"02_NLBE_{car}_tech2050.png")

a = nb(V["inv"]).groupby("tech").units.sum(); b = nb(M["inv"]).groupby("tech").units.sum()
idx = a.index.union(b.index)
d = b.reindex(idx, fill_value=0) - a.reindex(idx, fill_value=0)
d = d[d.abs() > .5].sort_values()
fig, ax = plt.subplots(figsize=(8, max(4, .3 * len(d))))
d.plot.barh(ax=ax, color=np.where(d > 0, "tab:green", "tab:red"))
ax.set_xlabel("unit count (mixed - vre15), summed over vintages\n(units differ by tech: GW for power, plant units for industry)"); ax.set_title("NL+BE investment difference")
save(fig, "03_NLBE_investment_delta.png")

def cap(d):
    c = nb(d["co2net"]); c = c[c.role == "captured"]
    return c.groupby(["year", "source"]).co2.sum().unstack().fillna(0) / 1e3
a, b = cap(V), cap(M); cols = sorted(set(a.columns) | set(b.columns))
fig, ax = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
for x, df, t in [(ax[0], a.reindex(columns=cols, fill_value=0), "vre15"),
                 (ax[1], b.reindex(columns=cols, fill_value=0), "mixed-res")]:
    df.plot.bar(stacked=True, ax=x, legend=False, colormap="tab10"); x.set_title(t); x.set_ylabel("Mt CO2")
ax[1].legend(bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=8)
fig.suptitle("NL+BE CO2 captured by source"); save(fig, "04_NLBE_co2_captured.png")

nbG = G[G.index.str.match(NB)]
def map_pair(sa, sb, title, fname, cmap="viridis", unit="TWh"):
    vmax = max(sa.max() if len(sa) else 0, sb.max() if len(sb) else 0, 1e-6)
    fig, ax = plt.subplots(1, 3, figsize=(16, 6))
    for x, s, t in [(ax[0], sa, "vre15"), (ax[1], sb, "mixed-res")]:
        g = nbG.join(s.rename("v")).fillna({"v": 0})
        g.plot(column="v", ax=x, cmap=cmap, vmin=0, vmax=vmax, legend=True, edgecolor="k", lw=.3,
               legend_kwds={"label": unit, "shrink": .6}); x.set_title(t); x.axis("off")
    dd = sb.reindex(nbG.index, fill_value=0) - sa.reindex(nbG.index, fill_value=0)
    lim = max(dd.abs().max(), 1e-6)
    nbG.join(dd.rename("v")).plot(column="v", ax=ax[2], cmap="RdBu_r", vmin=-lim, vmax=lim, legend=True,
                                  edgecolor="k", lw=.3, legend_kwds={"label": unit, "shrink": .6})
    ax[2].set_title("mixed - vre15"); ax[2].axis("off"); fig.suptitle(title); save(fig, fname)
def reg_sup(d, car, y):
    s = nb(d["supply"]); s = s[(s.carrier == car) & (s.year == y) & (s.energy > 0)]
    return s.groupby("region").energy.sum() / 1e3
def reg_emis(d, y):
    e = nb(d["emis"]); return e[e.year == y].groupby("region").co2.sum() / 1e3
def reg_capt(d, y):
    c = nb(d["co2net"]); c = c[(c.year == y) & (c.role == "captured")]
    return c.groupby("region").co2.sum() / 1e3
map_pair(reg_sup(V, "electricity", 2050), reg_sup(M, "electricity", 2050),
         "NL+BE onshore electricity generation 2050 (TWh; offshore wind not region-assigned)", "05_map_NLBE_elec2050.png")
map_pair(reg_emis(V, 2050), reg_emis(M, 2050), "NL+BE gross direct CO2 2050 (Mt; incl. gas CO2 booked at LNG terminals)",
         "05_map_NLBE_emis2050.png", "Reds", "Mt")
map_pair(reg_capt(V, 2050), reg_capt(M, 2050), "NL+BE CO2 captured 2050 (Mt)",
         "05_map_NLBE_capt2050.png", "Greens", "Mt")

def full_map(series, title, fname, cmap, unit, flows=None):
    g = G.join(series.rename("v")).fillna({"v": 0})
    fig, ax = plt.subplots(figsize=(9, 10))
    g.plot(column="v", ax=ax, cmap=cmap, legend=True, edgecolor="k", lw=.3,
           legend_kwds={"label": unit, "shrink": .5})
    if flows is not None and len(flows):
        c = G.geometry.representative_point(); mx = flows.v.max()
        for _, r in flows.iterrows():
            if r.o in c.index and r.d in c.index:
                p, q = c[r.o], c[r.d]
                ax.annotate("", xy=(q.x, q.y), xytext=(p.x, p.y),
                            arrowprops=dict(arrowstyle="-|>", lw=.5 + 5 * r.v / mx, color="purple", alpha=.7))
                ax.text((p.x + q.x) / 2, (p.y + q.y) / 2, f"{r.v:.0f}", fontsize=7, color="purple")
    ax.set_xlim(-9, 32); ax.set_ylim(48, 72); ax.set_title(title); ax.axis("off"); save(fig, fname)
for y in YRS:
    full_map(M["emis"][M["emis"].year == y].groupby("region").co2.sum() / 1e3,
             f"Gross direct CO2 {y} (Mt) - fossil gas CO2 booked where gas is EXTRACTED/IMPORTED\n(NO high because exported gas is counted in NO)", f"06_map_emis_{y}.png", "Reds", "Mt")
    st = M["co2store"][M["co2store"].year == y].groupby("region").co2.sum() / 1e3
    p = M["co2pipe"][M["co2pipe"].year == y].groupby(["origin", "dest"]).co2.sum().div(1e3).reset_index()
    p.columns = ["o", "d", "v"]; p = p[p.v > 1]
    full_map(st, f"CO2 injected to storage {y} (Mt) + CO2 pipeline flows (Mt)", f"06_map_co2storage_{y}.png",
             "YlGn", "Mt", flows=p)
    el = M["supply"]; el = el[(el.carrier == "electricity") & (el.year == y) & (el.energy > 0)]
    full_map(el.groupby("region").energy.sum() / 1e3, f"Onshore electricity generation {y} (TWh; offshore wind excluded)",
             f"06_map_elec_{y}.png", "viridis", "TWh")
    cp = M["co2net"]; cp = cp[(cp.year == y) & (cp.role == "captured")]
    full_map(cp.groupby("region").co2.sum() / 1e3, f"CO2 captured {y} (Mt)", f"06_map_captured_{y}.png", "Greens", "Mt")

s = M["supply"].copy(); s["c"] = s.region.map(ctry)
for car in ["electricity", "methane"]:
    t = s[(s.carrier == car) & (s.energy > 0) & (s.year == 2050)]
    df = t.groupby(["c", "category"]).energy.sum().unstack().fillna(0) / 1e3
    fig, ax = plt.subplots(figsize=(10, 5)); df.plot.bar(stacked=True, ax=ax, colormap="tab20")
    ax.set_ylabel("TWh/yr"); ax.set_title(f"Mixed-res gross {car} supply by country, 2050 (offshore = wind farms not assigned to a country)")
    ax.legend(bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=8); save(fig, f"07_country_{car}_2050.png")
c = M["co2net"].copy(); c["c"] = c.region.map(ctry)
df = c[(c.role == "captured") & (c.year == 2050)].groupby(["c", "source"]).co2.sum().unstack().fillna(0) / 1e3
fig, ax = plt.subplots(figsize=(10, 5)); df.plot.bar(stacked=True, ax=ax, colormap="tab10")
ax.set_ylabel("Mt"); ax.set_title("Mixed-res CO2 captured by country and source, 2050")
ax.legend(bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=8); save(fig, "07_country_co2captured_2050.png")

obj = pd.concat([V["obj"], M["obj"]], axis=1, keys=["vre15", "mixed"]) / 1e3
obj = obj[(obj > 0).any(axis=1)]
fig, ax = plt.subplots(figsize=(8, 5)); obj.T.plot.bar(stacked=True, ax=ax, colormap="tab10")
ax.set_ylabel("objective value (model cost units, x1000)"); ax.set_title("Objective breakdown (note: mixed run covers 6 countries, vre15 only NL+BE)"); save(fig, "08_objective.png")
