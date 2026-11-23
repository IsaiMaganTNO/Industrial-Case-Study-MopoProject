r"""Curated, shareable figures for ONE run (no comparisons).
Usage: python tools/plot_run_summary.py <cache.pkl> <outdir> [--title "..."]
Cache = pickle of postprocess.load(); NL+BE IC1 regions; offshore nodes (region NaN) included.
"""
import argparse, os, pickle, re
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white", "font.family": "DejaVu Sans",
    "font.size": 10.5, "axes.titlesize": 12.5, "axes.titleweight": "bold", "axes.titlepad": 10,
    "axes.edgecolor": "#9aa3ad", "axes.linewidth": .8, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "axes.grid.axis": "y", "grid.color": "#e3e7ec", "grid.linewidth": .8, "axes.axisbelow": True,
    "legend.frameon": False, "legend.fontsize": 9.5, "savefig.dpi": 200, "savefig.bbox": "tight",
})
YEARS = [2030, 2040, 2050]
NB = r"^(BE|NL)C\d"

ELEC = [  # (label, regex on tech, colour)
    ("Nuclear (existing)", r"^nuclear.*existing", "#7b3294"),
    ("Nuclear (new)", r"^nuclear", "#c2a5cf"),
    ("Wind offshore", r"^wind-off", "#1f5f8b"),
    ("Wind onshore", r"^wind-on", "#5fa8d3"),
    ("Solar PV", r"^solar", "#f2b134"),
    ("Gas (CCGT/OCGT)", r"^(CCGT|OCGT|GT|gas)(?!-H2)", "#8c8c8c"),
    ("Hydrogen turbines", r"-H2", "#2a9d8f"),
    ("Bioenergy", r"^bio", "#6a994e"),
    ("Battery discharge", r"^battery", "#e76f51"),
]
SECTOR_ORDER = ["steel (primary)", "steel (secondary)", "cement", "olefins", "ammonia", "chlorine",
                "glass (float)", "glass (container)", "glass (fibre)", "aluminium", "paper", "pulp"]

def group(tech, rules):
    for lab, rx, _ in rules:
        if re.search(rx, tech, re.I): return lab
    return "Other"

def save(fig, out, name):
    fig.savefig(os.path.join(out, name + ".png")); plt.close(fig); print("  ", name)

def stacked(ax, df, colors, unit, total=True):
    bottom = np.zeros(len(df)); x = np.arange(len(df))
    for c in df.columns:
        v = df[c].values
        ax.bar(x, v, .62, bottom=bottom, label=c, color=colors.get(c, "#bbbbbb"), edgecolor="white", linewidth=.6)
        bottom += v
    if total:
        for i, t in enumerate(bottom):
            ax.text(i, t * 1.01, f"{t:,.0f}", ha="center", va="bottom", fontsize=9.5, fontweight="bold", color="#333")
    ax.set_xticks(x, [str(y) for y in df.index]); ax.set_ylabel(unit)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.set_ylim(0, max(bottom.max() * 1.12, 1))

def fig_electricity(d, out, title):
    s = d["supply"]; s = s[(s.carrier == "electricity") & (s.energy > 0)]
    s = s[s.region.isna() | s.region.astype(str).str.match(NB)]
    s = s.assign(g=s.tech.map(lambda t: group(t, ELEC)))
    p = s.groupby(["year", "g"]).energy.sum().unstack().reindex(YEARS).fillna(0) / 1e3
    order = [l for l, _, _ in ELEC if l in p] + [c for c in p if c not in [l for l, _, _ in ELEC]]
    p = p[order]; p = p.loc[:, p.max() > .5]
    col = {l: c for l, _, c in ELEC}
    fig, ax = plt.subplots(figsize=(9, 5.6))
    stacked(ax, p, col, "Electricity generation (TWh/yr)")
    ax.set_title(f"Electricity generation by technology - {title}")
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1)); save(fig, out, "01_electricity_generation")
    sh = (p.T / p.sum(axis=1)).T * 100
    return p, sh

def fig_capacity(d, out, title):
    f = d["fleet"]; f = f[f.region.isna() | f.region.astype(str).str.match(NB)]
    f = f[f.tech.str.match(r"^(nuclear|wind|solar|CCGT|OCGT|bioST|battery)", case=False) | f.tech.str.contains("-H2")]
    f = f[~f.tech.str.contains("terminal|storage-node", case=False)]
    f = f.assign(g=f.tech.map(lambda t: group(t, ELEC)))
    p = f.groupby(["year", "g"]).units.sum().unstack().reindex(YEARS).fillna(0)
    p = p.rename(columns={"Battery discharge": "Battery"}); p = p.loc[:, p.max() > .1]
    col = {l: c for l, _, c in ELEC}; col["Battery"] = col["Battery discharge"]
    order = [l if l != "Battery discharge" else "Battery" for l, _, _ in ELEC]
    p = p[[c for c in order if c in p] + [c for c in p if c not in order]]
    fig, ax = plt.subplots(figsize=(9, 5.6)); stacked(ax, p, col, "Installed capacity (GW)")
    ax.set_title(f"Installed power capacity - {title}")
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1)); save(fig, out, "02_power_capacity")

def fig_fuels(d, out, title):
    s = d["supply"]; s = s[(s.energy > 0) & (s.region.isna() | s.region.astype(str).str.match(NB))]
    lab = {"LNG-terminal": "Imported LNG (fossil)", "methanation": "Methanation (synthetic)",
           "LH2-terminal": "Imported liquid H2", "PEM": "Electrolysis (PEM)"}
    col = {"Imported LNG (fossil)": "#6c757d", "Methanation (synthetic)": "#2a9d8f",
           "Imported liquid H2": "#a8dadc", "Electrolysis (PEM)": "#1d3557", "Other": "#cccccc"}
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.2))
    for ax, car, nm in zip(axes, ["methane", "hydrogen"], ["Methane supply", "Hydrogen supply"]):
        x = s[s.carrier == car].assign(g=lambda z: z.tech.map(lambda t: lab.get(t, "Other")))
        p = x.groupby(["year", "g"]).energy.sum().unstack().reindex(YEARS).fillna(0) / 1e3
        p = p.loc[:, p.max() > .5]; stacked(ax, p, col, "TWh/yr"); ax.set_title(nm)
        ax.legend(loc="upper right")
    fig.suptitle(f"Gas and hydrogen supply - {title}", fontweight="bold", fontsize=13.5, y=1.02)
    save(fig, out, "03_methane_hydrogen_supply")

def fig_heat(d, out, title):
    s = d["supply"]; s = s[(s.carrier == "heat") & (s.energy > 0) & (s.region.astype(str).str.match(NB))]
    ren = {"unabated fossil": "Fossil boilers / CHP", "electrification (heat pumps)": "Heat pumps / e-boilers",
           "bioenergy": "Bioenergy", "boilers (other fuels)": "Other-fuel boilers", "other": "Other"}
    col = {"Fossil boilers / CHP": "#8c8c8c", "Heat pumps / e-boilers": "#e63946", "Bioenergy": "#6a994e",
           "Other-fuel boilers": "#bc6c25", "Other": "#cccccc"}
    p = s.assign(g=s.category.map(lambda c: ren.get(c, "Other"))).groupby(["year", "g"]).energy.sum().unstack().reindex(YEARS).fillna(0) / 1e3
    p = p[[c for c in col if c in p]]
    fig, ax = plt.subplots(figsize=(9, 5.4)); stacked(ax, p, col, "Heat supply (TWh/yr)")
    ax.set_title(f"Heat supply by technology - {title}"); ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1))
    save(fig, out, "04_heat_supply")

ROUTE_LABEL = {
    "BF-BOF": "Blast furnace (coal)", "MOE": "Molten-oxide electrolysis", "(NG)DRI-EAF-MEA": "Gas DRI-EAF + CCS",
    "Scraps_EAF": "Scrap EAF", "EU-mix-2018": "Reference kiln", "LC3-(Afm)Oxy-MEA": "Oxy-fuel + CCS",
    "LC3-(Afm)Oxy-CaL": "Oxy-fuel + CaL", "(LN)O": "Steam cracker (unabated)", "(LN)O-MEA": "Steam cracker + CCS",
    "(NG)NH3": "Gas SMR (unabated)", "(NG)NH3-MVR-DEA": "Gas SMR + CCS (DEA)", "(NG)NH3-MVR-MEA-DEA": "Gas SMR + CCS (MEA/DEA)",
    "(BM)NH3": "Biomass gasification", "(H2)NH3": "Electrolytic H2", "Diaphragm": "Diaphragm electrolysis",
}
def route_label(t):
    if t in ROUTE_LABEL: return ROUTE_LABEL[t]
    if t.startswith("(NG)_g"): return "Gas-fired furnace"
    if t.startswith("(EL)-CC"): return "Electric furnace"
    if t.startswith("(H2)-CC"): return "Hydrogen furnace"
    if t.endswith("-alternative"): return "Low-carbon route"
    if t.endswith("-reference"): return "Reference route"
    return t

def route_color(lab):
    l = lab.lower()
    if "ccs" in l or "cal" in l: return "#457b9d"
    if "unabated" in l or "coal" in l or "reference" in l or "gas-fired" in l: return "#9e9e9e"
    if "electr" in l or "molten" in l: return "#e9c46a"
    if "hydrogen" in l or "h2" in l: return "#2a9d8f"
    if "bio" in l: return "#6a994e"
    if "scrap" in l: return "#b5838d"
    return "#90be6d"

def fig_industry_routes(d, out, title):
    p = d["prod"]; p = p[p.region.astype(str).str.match(NB)]
    p = p.assign(r=p.tech.map(route_label))
    secs = [s for s in SECTOR_ORDER if s in set(p.sector)]
    n = len(secs); ncol = 4; nrow = int(np.ceil(n / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(4.4 * ncol, 4.6 * nrow), sharey=True)
    for ax, sec in zip(axes.flat, secs):
        q = p[p.sector == sec].groupby(["year", "r"]).output.sum().unstack().reindex(YEARS).fillna(0)
        q = q.div(q.sum(axis=1), axis=0) * 100; q = q.loc[:, q.max() > .5]
        bottom = np.zeros(3)
        cols = {}
        for c in q.columns:
            col = route_color(c)
            # distinguish two routes sharing a colour
            while col in cols.values(): col = matplotlib.colors.to_hex(np.clip(np.array(matplotlib.colors.to_rgb(col)) * .75, 0, 1))
            cols[c] = col
            ax.bar(range(3), q[c], .65, bottom=bottom, color=col, edgecolor="white", linewidth=.6, label=c)
            for i, v in enumerate(q[c]):
                if v >= 12: ax.text(i, bottom[i] + v / 2, f"{v:.0f}%", ha="center", va="center", fontsize=8, color="white", fontweight="bold")
            bottom += q[c].values
        ax.set_title(sec.capitalize(), fontsize=11); ax.set_xticks(range(3), YEARS); ax.set_ylim(0, 100)
        ax.legend(fontsize=7.5, loc="upper center", bbox_to_anchor=(.5, -.12), ncol=1)
        ax.grid(False)
    for ax in list(axes.flat)[n:]: ax.axis("off")
    for ax in axes[:, 0]: ax.set_ylabel("Share of output (%)")
    fig.suptitle(f"Industrial production routes by sector (share of output) - {title}", fontweight="bold", fontsize=14, y=1.0)
    fig.tight_layout(h_pad=3.5); save(fig, out, "05_industry_routes")

def fig_industry_emissions(d, out, title):
    p = d["prod"]; e = d["emis"]; c = d["co2net"]
    p = p[p.region.astype(str).str.match(NB)]; e = e[e.region.astype(str).str.match(NB)]
    t2s = p.drop_duplicates("tech").set_index("tech").sector
    em = e.assign(s=e.tech.map(t2s)).dropna(subset=["s"]).groupby(["year", "s"]).co2.sum().unstack().reindex(YEARS).fillna(0) / 1e3
    cc = c[(c.role == "captured") & c.region.astype(str).str.match(NB)]
    cap = cc.groupby(["year", "source"]).co2.sum().unstack().reindex(YEARS).fillna(0) / 1e3
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.6))
    secs = [s for s in SECTOR_ORDER if s in em]; em = em[secs]; em = em.loc[:, em.max() > .05]
    cmap = plt.get_cmap("tab20"); col = {s: cmap(i) for i, s in enumerate(em.columns)}
    stacked(axes[0], em, col, "Direct CO2 emissions (Mt/yr)")
    axes[0].set_title("Residual direct emissions, heavy industry"); axes[0].legend(loc="upper right", fontsize=8.5)
    cap = cap.loc[:, cap.max() > .05]
    ccol = {k: v for k, v in zip(cap.columns, ["#264653", "#2a9d8f", "#e9c46a", "#f4a261", "#e76f51", "#8ab17d", "#6d597a"])}
    stacked(axes[1], cap, ccol, "CO2 captured (Mt/yr)"); axes[1].set_title("CO2 captured by source")
    axes[1].legend(loc="upper left", fontsize=8.5)
    fig.suptitle(f"Industrial CO2: residual emissions and capture - {title}", fontweight="bold", fontsize=13.5, y=1.02)
    save(fig, out, "06_industry_emissions_capture")

def fig_co2_balance(d, out, title):
    e = d["emis"]; e = e[e.region.isna() | e.region.astype(str).str.match(NB)]
    def g(row):
        t, c = row.tech, row.category
        if t.startswith("CO2-injection"): return "Geological storage"
        if t.startswith("LNG-terminal"): return "Fossil gas use (all sectors)"
        if str(c).startswith("industry") or t in ("(NG)PEA", "BF-BOF") or re.match(r"^\(", t): return "Industry (process & fuel)"
        if "hydrogen" in str(c) or t.startswith("REF-SMR"): return "Hydrogen production"
        return "Other"
    e = e.assign(g=e.apply(g, axis=1))
    p = e.groupby(["year", "g"]).co2.sum().unstack().reindex(YEARS).fillna(0) / 1e3
    col = {"Fossil gas use (all sectors)": "#6c757d", "Industry (process & fuel)": "#bc6c25",
           "Hydrogen production": "#2a9d8f", "Other": "#cfd4da", "Geological storage": "#1d3557"}
    fig, ax = plt.subplots(figsize=(9.5, 5.6)); x = np.arange(3)
    pos = np.zeros(3); neg = np.zeros(3)
    for k in col:
        if k not in p: continue
        v = p[k].values; vp = np.clip(v, 0, None); vn = np.clip(v, None, 0)
        ax.bar(x, vp, .6, bottom=pos, color=col[k], label=k, edgecolor="white"); pos += vp
        if vn.any(): ax.bar(x, vn, .6, bottom=neg, color=col[k], edgecolor="white", label=None if vp.any() else None); neg += vn
    net = p.sum(axis=1).values
    ax.plot(x, net, "D", color="#d62828", ms=9, label="Net emissions", zorder=5)
    for i, v in enumerate(net): ax.annotate(f"net {v:,.1f}", (i, v), xytext=(18, 6), textcoords="offset points", fontsize=9.5, color="#d62828", fontweight="bold")
    ax.axhline(0, color="#333", lw=.9); ax.set_xticks(x, YEARS); ax.set_ylabel("Mt CO2/yr")
    ax.set_title(f"CO2 balance (gross emissions vs storage) - {title}"); ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1))
    save(fig, out, "07_co2_balance")

def fig_co2_storage(d, out, title):
    s = d["co2store"].groupby(["year", "reservoir"]).co2.sum().unstack().reindex(YEARS).fillna(0) / 1e3
    s.columns = [c.replace("CO2-storage-", "") for c in s.columns]
    caps = {"NSNL012": 21.0, "NSNL031": 6.2}
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    stacked(ax, s, {"NSNL012": "#1d3557", "NSNL031": "#457b9d"}, "CO2 injected (Mt/yr)")
    ax.axhline(sum(caps.values()), ls="--", color="#d62828", lw=1.2)
    ax.text(-.4, sum(caps.values()) * 1.02, f"Combined site limit {sum(caps.values()):.1f} Mt/yr (high_CO2)", color="#d62828", fontsize=9)
    ax.set_title(f"CO2 geological storage use - {title}"); ax.legend(loc="upper left")
    save(fig, out, "08_co2_storage")

def fig_costs(d, out, title):
    o = d["obj"].drop(labels=[k for k in d["obj"].index if abs(d["obj"][k]) < 1], errors="ignore").sort_values()
    lab = {k: k.replace("_", " ").replace("costs", "").strip().capitalize() for k in o.index}
    fig, ax = plt.subplots(figsize=(9, 4.6))
    ax.barh([lab[k] for k in o.index], o.values / 1e3, color="#457b9d"); ax.grid(axis="x"); ax.grid(axis="y", visible=False)
    for i, v in enumerate(o.values / 1e3): ax.text(v, i, f"  {v:,.0f}", va="center", fontsize=9.5)
    ax.set_xlabel("Objective contribution (model cost units / 1000)")
    ax.set_title(f"System cost breakdown (total {o.sum():,.0f}) - {title}")
    ax.set_xlim(0, o.max() / 1e3 * 1.18); save(fig, out, "09_cost_breakdown")

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("pkl"); ap.add_argument("out"); ap.add_argument("--title", default="")
    ap.add_argument("--regions", default=None, help="regex on region (default NL+BE IC1 zones)")
    ap.add_argument("--no-offshore", action="store_true", help="drop region-less rows (offshore wind)")
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    global NB
    if a.regions: NB = a.regions
    d = pickle.load(open(a.pkl, "rb"))
    if a.no_offshore:
        d = {k: (v[v.region.notna()] if hasattr(v, "columns") and "region" in v.columns else v) for k, v in d.items()}
    fig_electricity(d, a.out, a.title); fig_capacity(d, a.out, a.title); fig_fuels(d, a.out, a.title)
    fig_heat(d, a.out, a.title); fig_industry_routes(d, a.out, a.title); fig_industry_emissions(d, a.out, a.title)
    fig_co2_balance(d, a.out, a.title); fig_co2_storage(d, a.out, a.title); fig_costs(d, a.out, a.title)

if __name__ == "__main__":
    main()

