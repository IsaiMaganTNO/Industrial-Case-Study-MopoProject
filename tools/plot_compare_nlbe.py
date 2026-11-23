r"""Comparison plots NL+BE: 3day_nb_v2 (NL+BE alone) vs 3day_mr_fix (mixed resolution, shared CO2 budget).
Usage: python tools/plot_compare_nlbe.py <outdir>
Inputs: run_logs/{nb_v2,mr_fix}_NLBE.pkl (tools/filter_pkl_countries.py),
        run_logs/{nb_v2,mr_fix}_xbbio.pkl (tools/extract_xb_bio.py), run input/output DBs (costs).
"""
import os, re, sys, pickle
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, "tools")
import plot_run_summary as S
import postprocess as PP
import report_v2 as R2
YEARS = S.YEARS
A_NAME = os.environ.get("CMP_NAME_A", "nb_v2"); B_NAME = os.environ.get("CMP_NAME_B", "mr_fix")
RUNS = {os.environ.get("CMP_LABEL_A", "nb_v2 (NL+BE only)"): A_NAME, os.environ.get("CMP_LABEL_B", "mr_fix (6-country, shared budget)"): B_NAME}
LAB = list(RUNS)
COL2 = {LAB[0]: "#9aa3ad", LAB[1]: "#1d3557"}
_db = lambda n: (rf"runs\3day_{n}\input\Final_SpineOpt_Model.tiny.3day.{n}.sqlite", rf"runs\3day_{n}\output\Investment_Results.3day_{n}.sqlite")
DB = {n: _db(n) for n in (A_NAME, B_NAME)}
D = {k: pickle.load(open(rf"run_logs\{v}_NLBE.pkl", "rb")) for k, v in RUNS.items()}
X = {k: pd.read_pickle(rf"run_logs\{v}_xbbio.pkl") for k, v in RUNS.items()}
NLBE = {"NL", "BE"}
def save(fig, out, name): fig.savefig(os.path.join(out, name + ".png")); plt.close(fig); print("  ", name)
def suptitle(fig, t): fig.suptitle(t, fontweight="bold", fontsize=14, y=1.02)

def paired_stacks(ax_pair, frames, colors, unit):
    ymax = max(f.sum(axis=1).max() for f in frames.values()) * 1.12
    for ax, (k, f) in zip(ax_pair, frames.items()):
        S.stacked(ax, f, colors, unit); ax.set_ylim(0, ymax); ax.set_title(k)

# 1 electricity mix
def c01(out):
    fr = {}
    for k, d in D.items():
        s = d["supply"]; s = s[(s.carrier == "electricity") & (s.energy > 0)]
        fr[k] = s.assign(g=s.tech.map(lambda t: S.group(t, S.ELEC))).groupby(["year", "g"]).energy.sum().unstack().reindex(YEARS).fillna(0) / 1e3
    cols = [l for l, _, _ in S.ELEC if any(l in f and f[l].max() > .5 for f in fr.values())] + ["Other"]
    fr = {k: f.reindex(columns=cols).fillna(0) for k, f in fr.items()}
    col = {l: c for l, _, c in S.ELEC}; col["Other"] = "#cccccc"
    fig, ax = plt.subplots(1, 2, figsize=(14, 5.6), sharey=True); paired_stacks(ax, fr, col, "Electricity generation (TWh/yr)")
    ax[1].legend(loc="upper left", bbox_to_anchor=(1.01, 1)); suptitle(fig, "NL+BE electricity generation mix"); save(fig, out, "C01_electricity_mix")

# 2 capacity deltas
CAPG = [("Wind offshore", r"^wind-off"), ("Wind onshore", r"^wind-on"), ("Solar PV", r"^solar"), ("Nuclear", r"^nuclear"),
        ("Gas power (CCGT/OCGT)", r"^(CCGT|OCGT)"), ("Battery", r"^battery"), ("Electrolysers (PEM)", r"^PEM"),
        ("SMR (H2 from gas)", r"^REF-SMR"), ("Gas boilers", r"^gas-boiler"), ("Heat pumps", r"heatpump|heat-pump")]
def cap_table(d):
    f = d["fleet"]; return pd.DataFrame({l: f[f.tech.astype(str).str.contains(rx, case=False)].groupby("year").units.sum() for l, rx in CAPG}).reindex(YEARS).fillna(0)
def c02(out):
    a, b = cap_table(D[LAB[0]]), cap_table(D[LAB[1]])
    fig, axes = plt.subplots(1, 2, figsize=(15, 6), gridspec_kw={"width_ratios": [1.25, 1]})
    y = np.arange(len(CAPG)); h = .38; ax = axes[0]
    ax.barh(y + h / 2, a.loc[2050], h, color=COL2[LAB[0]], label=LAB[0]); ax.barh(y - h / 2, b.loc[2050], h, color=COL2[LAB[1]], label=LAB[1])
    for i in range(len(CAPG)):
        ax.text(a.loc[2050].iloc[i], i + h / 2, f" {a.loc[2050].iloc[i]:.1f}", va="center", fontsize=8.5)
        ax.text(b.loc[2050].iloc[i], i - h / 2, f" {b.loc[2050].iloc[i]:.1f}", va="center", fontsize=8.5)
    ax.set_yticks(y, [l for l, _ in CAPG]); ax.invert_yaxis(); ax.grid(axis="x"); ax.grid(axis="y", visible=False)
    ax.set_xlabel("GW"); ax.set_title("Installed capacity 2050"); ax.legend(loc="lower right")
    dd = (b - a); ax = axes[1]; w = .26
    for j, yr in enumerate(YEARS):
        ax.barh(y + (j - 1) * w, dd.loc[yr], w, label=str(yr), color=["#a8dadc", "#457b9d", "#1d3557"][j])
    ax.axvline(0, color="#333", lw=.8); ax.set_yticks(y, ["" for _ in CAPG]); ax.invert_yaxis(); ax.grid(axis="x"); ax.grid(axis="y", visible=False)
    ax.set_xlabel(f"GW ({B_NAME} minus {A_NAME})"); ax.set_title(f"Difference {B_NAME} - {A_NAME}"); ax.legend(loc="lower right")
    suptitle(fig, f"NL+BE installed capacity: {A_NAME} vs {B_NAME}"); fig.tight_layout(); save(fig, out, "C02_capacity_delta")

# 3 industry routes paired
def c03(out):
    P = {k: d["prod"].assign(r=lambda z: z.tech.map(S.route_label)) for k, d in D.items()}
    secs = [s for s in S.SECTOR_ORDER if any(s in set(p.sector) for p in P.values())]
    allr = sorted(set().union(*[set(p.r) for p in P.values()]))
    # distinct qualitative colours (colleague: shaded variants were too similar)
    PAL = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
           "#393b79", "#e7ba52", "#637939", "#ad494a", "#7b4173", "#3182bd", "#fd8d3c", "#74c476", "#9e9ac8", "#000000"]
    col = {r: PAL[i % len(PAL)] for i, r in enumerate(allr)}
    ncol = 4; nrow = int(np.ceil(len(secs) / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(4.8 * ncol, 4.3 * nrow), sharey=True)
    xs = [0, 1, 2, 3.6, 4.6, 5.6]; used = set()
    for ax, sec in zip(axes.flat, secs):
        bars = []
        for k in LAB:
            q = P[k][P[k].sector == sec].groupby(["year", "r"]).output.sum().unstack().reindex(YEARS).fillna(0)
            bars.append(q.div(q.sum(axis=1).replace(0, np.nan), axis=0).fillna(0) * 100)
        for xi, (bi, yr) in zip(xs, [(0, y) for y in YEARS] + [(1, y) for y in YEARS]):
            bot = 0
            for r, v in bars[bi].loc[yr].items():
                if v < .5: continue
                ax.bar(xi, v, .85, bottom=bot, color=col[r], edgecolor="white", lw=.5); used.add(r)
                if v >= 15: ax.text(xi, bot + v / 2, f"{v:.0f}", ha="center", va="center", fontsize=7.5, color="white", fontweight="bold")
                bot += v
        ax.set_xticks(xs, ["30", "40", "50"] * 2, fontsize=8); ax.set_ylim(0, 112); ax.grid(False)
        ax.text(1, 104, A_NAME, ha="center", fontsize=9, color="#555"); ax.text(4.6, 104, B_NAME, ha="center", fontsize=9, color="#1d3557", fontweight="bold")
        ax.set_title(sec.capitalize(), fontsize=11)
    for ax in list(axes.flat)[len(secs):]: ax.axis("off")
    for ax in axes[:, 0]: ax.set_ylabel("Share of output (%)")
    h = [plt.Rectangle((0, 0), 1, 1, color=col[r]) for r in sorted(used)]
    fig.legend(h, sorted(used), loc="lower center", ncol=4, bbox_to_anchor=(.5, -.06), fontsize=9)
    suptitle(fig, f"NL+BE industrial routes per sector (left: {A_NAME}, right: {B_NAME}; years 2030/40/50)"); fig.tight_layout(); save(fig, out, "C03_industry_routes")

# 4 CO2 balance waterfall 2050 (+2040)
def co2_items(k):
    d = D[k]; e = d["emis"]; xb = X[k]["xb"]
    gross = e[e.co2 > 0].co2.sum
    inj = e[e.tech.str.startswith("CO2-injection")]
    rows = {}
    for yr in YEARS:
        ey = e[e.year == yr]
        lng = ey[ey.tech.str.startswith("LNG-terminal")].co2.sum() / 1e3
        oth = ey[(ey.co2 > 0) & ~ey.tech.str.startswith("LNG-terminal")].co2.sum() / 1e3
        negs = ey[(ey.co2 < 0) & ~ey.tech.str.startswith("CO2-injection")].co2.sum() / 1e3
        st = ey[ey.tech.str.startswith("CO2-injection")].co2.sum() / 1e3
        c = xb[(xb.car == "CO2") & (xb.year == yr)]
        ex = c[c.o.isin(NLBE) & ~c.d.isin(NLBE)].v.sum() / 1e3; im = c[~c.o.isin(NLBE) & c.d.isin(NLBE)].v.sum() / 1e3
        cap = d["co2net"]; cap = cap[(cap.role == "captured") & (cap.year == yr)].co2.sum() / 1e3
        rows[yr] = dict(lng=lng, oth=oth, negs=negs, stored=st, exp=ex, imp=im, captured=cap, net=ey.co2.sum() / 1e3)
    return pd.DataFrame(rows).T
def c04(out):
    fig, axes = plt.subplots(1, 2, figsize=(15, 6), sharey=True)
    for ax, k in zip(axes, LAB):
        t = co2_items(k).loc[2050]
        steps = [("Fossil gas\n(imported LNG)", t.lng), ("Other gross\nemissions", t.oth), ("Other negative\n(bio-CCS etc.)", t.negs),
                 ("Stored in NL\nsites", t.stored)]
        cum = 0; xl = []
        for i, (l, v) in enumerate(steps):
            ax.bar(i, v, .6, bottom=cum if v >= 0 else cum + v, color="#6c757d" if v >= 0 else "#2a9d8f", edgecolor="white")
            ax.text(i, max(cum, cum + v) + 2, f"{v:+.1f}", ha="center", fontsize=9.5, fontweight="bold"); cum += v; xl.append(l)
        ax.bar(len(steps), cum, .6, color="#d62828"); ax.text(len(steps), max(cum, 0) + 2, f"{cum:.1f}", ha="center", fontsize=10, fontweight="bold", color="#d62828"); xl.append("Net NL+BE\nemissions")
        ax.bar(len(steps) + 1.3, t.captured, .6, color="#457b9d"); ax.text(len(steps) + 1.3, t.captured + 2, f"{t.captured:.1f}", ha="center", fontsize=9.5)
        ax.bar(len(steps) + 2.3, t.exp, .6, color="#e9c46a"); ax.text(len(steps) + 2.3, t.exp + 2, f"{t.exp:.1f}", ha="center", fontsize=9.5)
        xl += ["memo: CO2\ncaptured", "memo: CO2\nexported"]
        ax.set_xticks(list(range(len(steps) + 1)) + [len(steps) + 1.3, len(steps) + 2.3], xl, fontsize=8.5)
        ax.axhline(0, color="#333", lw=.8); ax.set_title(k); ax.set_ylabel("Mt CO2 / yr (2050)")
    suptitle(fig, "NL+BE CO2 balance in 2050"); fig.tight_layout(); save(fig, out, "C04_co2_balance_2050")
    rows = []
    for k in LAB:
        t = co2_items(k)
        for yr in YEARS: rows.append(dict(run=k, year=yr, **t.loc[yr].round(2).to_dict()))
    pd.DataFrame(rows).to_csv(os.path.join(out, "C04_co2_balance.csv"), index=False)

# 5 gas supply and transit
def gas_tab(k):
    s = D[k]["supply"]; s = s[(s.carrier == "methane") & (s.energy > 0)]; xb = X[k]["xb"]; xb = xb[xb.car == "CH4"]
    r = {}
    for yr in YEARS:
        sy = s[s.year == yr]
        lng = sy[sy.tech.str.startswith("LNG") | sy.tech.str.startswith("gas-extr")].energy.sum() / 1e3
        bio = sy[sy.tech.str.startswith("bio")].energy.sum() / 1e3
        syn = sy[sy.tech.str.startswith("methanation")].energy.sum() / 1e3
        x = xb[xb.year == yr]
        im = x[~x.o.isin(NLBE) & x.d.isin(NLBE)].v.sum() / 1e3; ex = x[x.o.isin(NLBE) & ~x.d.isin(NLBE)].v.sum() / 1e3
        r[yr] = dict(lng=lng, bio=bio, syn=syn, local=bio + syn, imp=im, exp=ex, use=lng + bio + syn + im - ex)
    return pd.DataFrame(r).T
def c05(out):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.8), sharey=True)
    ymax = max(gas_tab(k)[["lng", "local", "imp"]].sum(axis=1).max() for k in LAB) * 1.15
    for ax, k in zip(axes, LAB):
        t = gas_tab(k); x = np.arange(3); w = .36
        b = np.zeros(3)
        for c, l, cl in [("lng", "Fossil: LNG import (terminals)", "#6c757d"), ("bio", "Renewable: biomethane", "#6a994e"), ("syn", "Synthetic: methanation", "#2a9d8f"), ("imp", "Pipeline import from neighbours (mostly transit)", "#adb5bd")]:
            ax.bar(x - w / 2, t[c], w, bottom=b, color=cl, label=l, edgecolor="white"); b += t[c].values
        ax.bar(x + w / 2, t.exp, w, color="#e9c46a", label="Pipeline export to neighbours")
        ax.plot(x, t.use, "D", color="#d62828", ms=8, label="Net NL+BE consumption")
        for i in range(3):
            ax.text(x[i] - w / 2, b[i] + 8, f"{b[i]:.0f}", ha="center", fontsize=9); ax.text(x[i] + w / 2, t.exp.iloc[i] + 8, f"{t.exp.iloc[i]:.0f}", ha="center", fontsize=9)
            ax.annotate(f"{t.use.iloc[i]:.0f}", (x[i], t.use.iloc[i]), xytext=(12, -12), textcoords="offset points", color="#d62828", fontsize=9, fontweight="bold")
        ax.set_xticks(x, YEARS); ax.set_ylim(0, ymax); ax.set_ylabel("TWh/yr"); ax.set_title(k)
    axes[1].legend(loc="upper left", bbox_to_anchor=(1.01, 1)); suptitle(fig, "NL+BE methane: supply, imports, exports (transit) and net use"); save(fig, out, "C05_gas_supply_transit")

# 6 H2 supply
def c06(out):
    lab = {"LH2-terminal": "Imported liquid H2", "PEM": "Electrolysis (PEM)", "REF-SMR": "SMR (gas)", "REF-SMR-CC": "SMR + CCS"}
    fr = {}
    for k in LAB:
        s = D[k]["supply"]; s = s[(s.carrier == "hydrogen") & (s.energy > 0)]
        g = s.tech.map(lambda t: "SMR + CCS" if re.match(r"REF-SMR.*CC", t) else ("SMR (gas)" if t.startswith("REF-SMR") else lab.get(t, "Other")))
        f = s.assign(g=g).groupby(["year", "g"]).energy.sum().unstack().reindex(YEARS).fillna(0) / 1e3
        xb = X[k]["xb"]; xb = xb[xb.car == "H2"]
        f["Net pipeline import"] = [max(0, (xb[(xb.year == y) & ~xb.o.isin(NLBE) & xb.d.isin(NLBE)].v.sum() - xb[(xb.year == y) & xb.o.isin(NLBE) & ~xb.d.isin(NLBE)].v.sum()) / 1e3) for y in YEARS]
        fr[k] = f
    cols = sorted(set().union(*[set(f.columns[f.max() > .5]) for f in fr.values()]))
    fr = {k: f.reindex(columns=cols).fillna(0) for k, f in fr.items()}
    col = {"Imported liquid H2": "#a8dadc", "Electrolysis (PEM)": "#1d3557", "SMR (gas)": "#8c8c8c", "SMR + CCS": "#457b9d", "Net pipeline import": "#e9c46a", "Other": "#cccccc"}
    fig, ax = plt.subplots(1, 2, figsize=(14, 5.6), sharey=True); paired_stacks(ax, fr, col, "Hydrogen supply (TWh/yr)")
    ax[1].legend(loc="upper left", bbox_to_anchor=(1.01, 1)); suptitle(fig, "NL+BE hydrogen supply"); save(fig, out, "C06_hydrogen_supply")

# 7 cross-border flow maps 2050
def c07(out):
    import geopandas as gpd
    gdf = gpd.read_file(r"geodata\IC1_NWEU.geojson"); gdf["c"] = gdf.id.str[:2]
    cty = gdf.dissolve("c"); cen = {c: (g.representative_point().x, g.representative_point().y) for c, g in cty.geometry.items()}
    cen.update({"FR": (2.5, 49.3), "LU": (6.1, 49.7), "SE": (13.5, 57.5), "PL": (15.5, 52.5), "CZ": (14.5, 50.0), "AT": (13.0, 48.6),
                "CH": (8.2, 47.4), "FI": (21, 60.5), "IE": (-7.5, 53.2)})
    cars = [("CO2", "Mt CO2", "#d62828"), ("CH4", "TWh methane", "#6c757d"), ("elec", "TWh electricity", "#f2b134"), ("H2", "TWh hydrogen", "#2a9d8f")]
    for k in LAB:
        xb = X[k]["xb"]; xb = xb[xb.year == 2050]
        fig, axes = plt.subplots(1, 4, figsize=(22, 6.5))
        for ax, (car, unit, cl) in zip(axes, cars):
            gdf.plot(ax=ax, color="#eef1f4", edgecolor="#c5ccd3", lw=.4)
            gdf[gdf.c.isin(NLBE)].plot(ax=ax, color="#dde6ef", edgecolor="#9aa3ad", lw=.4)
            f = xb[xb.car == car].groupby(["o", "d"]).v.sum() / 1e3
            net = {}
            for (o, d), v in f.items():
                key = tuple(sorted((o, d))); s = 1 if (o, d) == key else -1; net[key] = net.get(key, 0) + s * v
            mx = max([abs(v) for v in net.values()] + [1])
            for (a, b), v in net.items():
                if abs(v) < .5 or a not in cen or b not in cen: continue
                o, d = (a, b) if v > 0 else (b, a)
                ax.annotate("", xy=cen[d], xytext=cen[o], arrowprops=dict(arrowstyle="-|>", color=cl, lw=1 + 7 * abs(v) / mx, alpha=.8, mutation_scale=14, shrinkA=6, shrinkB=6))
                mxp, myp = (cen[o][0] + cen[d][0]) / 2, (cen[o][1] + cen[d][1]) / 2
                ax.text(mxp, myp, f"{abs(v):.0f}", fontsize=8, ha="center", va="center", bbox=dict(boxstyle="round,pad=.15", fc="white", ec="none", alpha=.85))
            for c, (x, y) in cen.items(): ax.text(x, y - .45, c, fontsize=7.5, ha="center", color="#555")
            ax.set_xlim(-9, 24); ax.set_ylim(46.5, 64); ax.set_axis_off(); ax.set_title(f"Net {car} flows, 2050 ({unit})")
        suptitle(fig, f"Cross-border net flows 2050 - {k}"); fig.tight_layout(); save(fig, out, f"C07_flow_map_2050_{RUNS[k]}")

# 8 cost breakdown NL+BE assets
def cost_nlbe(k):
    m, r = DB[RUNS[k]]; c = R2.load_costs(m, r)
    def ctry(n):
        mm = re.search(r"_(?:NS|AS|AT|BS)?((?:BE|NL)C?\d*|DE|DK|NO|UK)$", n.replace("_realization", ""))
        return mm.group(1)[:2] if mm else None
    c["c"] = c["name"].map(ctry); return c[c.c.isin(NLBE)]
CG = [("Offshore wind", r"^wind-off"), ("Onshore wind", r"^wind-on"), ("Solar", r"^solar"), ("Nuclear", r"^nuclear"), ("Gas power", r"^(CCGT|OCGT)"),
      ("Hydrogen (PEM/SMR)", r"^(PEM|REF-SMR)"), ("Heat (boilers/HP)", r"boiler|heatpump|heat-pump"), ("Industry routes (incl. with CCS)", r"^\(|EAF|BOF|MOE|production|Diaphragm|CEM|LC3"),
      ("CO2 transport / injection", r"^CO2-"), ("Gas/LNG/H2 terminals", r"terminal")]
def c08(out):
    rows = []
    for k in LAB:
        c = cost_nlbe(k); c["g"] = c.tech.map(lambda t: next((l for l, rx in CG if re.search(rx, t)), "Other"))
        t = c.groupby(["g", "kind"]).cost.sum().unstack().fillna(0) / 1e3; t["run"] = k; rows.append(t)
    t = pd.concat(rows).reset_index()
    groups = [l for l, _ in CG] + ["Other"]
    fig, ax = plt.subplots(figsize=(13, 6.5)); y = np.arange(len(groups)); h = .38
    for j, k in enumerate(LAB):
        tt = t[t.run == k].set_index("g").reindex(groups).fillna(0)
        left = np.zeros(len(groups))
        for kind, al in [("investment", 1), ("fixed O&M", .5)]:
            v = tt.get(kind, pd.Series(0, index=groups)).values
            ax.barh(y + (h / 2 if j == 0 else -h / 2), v, h, left=left, color=COL2[k], alpha=al, label=f"{k} - {kind}"); left += v
        for i, v in enumerate(left): ax.text(v, y[i] + (h / 2 if j == 0 else -h / 2), f" {v:,.0f}", va="center", fontsize=8)
    ax.set_yticks(y, groups); ax.invert_yaxis(); ax.grid(axis="x"); ax.grid(axis="y", visible=False)
    ax.set_xlabel("Cost, summed over milestones (model cost units / 1000)"); ax.legend(loc="lower right", fontsize=8.5)
    ax.set_title(f"NL+BE asset costs (investment solid, fixed O&M light) - {A_NAME} vs {B_NAME}")
    t.to_csv(os.path.join(out, "C08_costs_nlbe.csv"), index=False); save(fig, out, "C08_cost_breakdown_nlbe")

# 9 emissions under two accountings
def c09(out):
    rows = []
    for k in LAB:
        b = co2_items(k); g = gas_tab(k)
        ef = (b.lng / g.lng.replace(0, np.nan)).fillna(.2)  # Mt per TWh, as booked on the terminals
        fossil_use = (g.use - g.local).clip(lower=0)  # pipeline imports assumed fossil
        at_use = b.net - b.lng + ef * fossil_use
        for yr in YEARS: rows.append(dict(run=k, year=yr, at_import=b.net.loc[yr], at_use=at_use.loc[yr], ef=ef.loc[yr]))
    t = pd.DataFrame(rows); t.to_csv(os.path.join(out, "C09_emission_accounting.csv"), index=False)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.6), sharey=True); x = np.arange(3); w = .36
    for ax, k in zip(axes, LAB):
        tt = t[t.run == k].set_index("year")
        ax.bar(x - w / 2, tt.at_import, w, color="#6c757d", label="Booked at import (model)")
        ax.bar(x + w / 2, tt.at_use, w, color="#457b9d", label="Re-attributed to NL+BE gas use")
        for i, yr in enumerate(YEARS):
            ax.text(i - w / 2, max(tt.at_import[yr], 0) + 3, f"{tt.at_import[yr]:.0f}", ha="center", fontsize=9)
            ax.text(i + w / 2, max(tt.at_use[yr], 0) + 3, f"{tt.at_use[yr]:.0f}", ha="center", fontsize=9)
        ax.axhline(0, color="#333", lw=.8); ax.set_xticks(x, YEARS); ax.set_title(k); ax.set_ylabel("Net NL+BE CO2 (Mt/yr)")
    axes[0].legend(loc="upper right")
    fig.text(.5, -.04, "Re-attribution: remove LNG-terminal emissions, add (net NL+BE fossil gas use = LNG + pipeline imports - exports) x emission factor booked on the terminals. Approximation; storage/capture unchanged.",
             ha="center", fontsize=8.5, color="#555")
    suptitle(fig, "NL+BE net CO2: emissions at import (as modelled) vs at gas use"); save(fig, out, "C09_emission_accounting")

# 10 nuclear and biomass
def c10(out):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.6)); x = np.arange(3); w = .2
    ax = axes[0]
    for j, k in enumerate(LAB):
        f = D[k]["fleet"]; f = f[f.tech.str.startswith("nuclear")]
        f = f.assign(c=f.region.astype(str).str[:2])
        for i, c in enumerate(["BE", "NL"]):
            v = f[f.c == c].groupby("year").units.sum().reindex(YEARS).fillna(0)
            ax.bar(x + (2 * j + i - 1.5) * w, v, w, color=COL2[k], alpha=1 if c == "BE" else .55, label=f"{c} - {k}")
            for xi, vv in zip(x + (2 * j + i - 1.5) * w, v): ax.text(xi, vv + .1, f"{vv:.1f}", ha="center", fontsize=8)
    ax.set_xticks(x, YEARS); ax.set_ylabel("GW"); ax.set_title("Nuclear capacity"); ax.legend(fontsize=8.5)
    ax = axes[1]
    for j, k in enumerate(LAB):
        b = X[k]["bio"]
        for i, c in enumerate(["BE", "NL"]):
            v = b[b.c == c].groupby("year").v.sum().reindex(YEARS).fillna(0) / 1e3
            ax.bar(x + (2 * j + i - 1.5) * w, v, w, color="#6a994e" if j else "#b7c9a8", alpha=1 if c == "BE" else .6, label=f"{c} - {k}")
            for xi, vv in zip(x + (2 * j + i - 1.5) * w, v): ax.text(xi, vv + 1, f"{vv:.0f}", ha="center", fontsize=8)
    ax.set_xticks(x, YEARS); ax.set_ylabel("TWh/yr"); ax.set_title("Biomass consumption (flow out of bio nodes)"); ax.legend(fontsize=8.5)
    suptitle(fig, f"NL+BE nuclear and biomass: {A_NAME} vs {B_NAME}"); fig.tight_layout(); save(fig, out, "C10_nuclear_biomass")

if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    for f in [c01, c02, c03, c04, c05, c06, c07, c08, c09, c10]:
        try: f(out)
        except Exception as e:
            import traceback; print("FAIL", f.__name__); traceback.print_exc()


