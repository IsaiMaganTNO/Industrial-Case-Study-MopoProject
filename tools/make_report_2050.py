r"""2050-focused report figures, NL+BE focus, all runs. Reuses make_deck_final3 helpers.
Outputs final_runs_pessimistic_ccs\report_2050\*.png/.csv  (suffix _all = 2030/40/50, _2050 = 2050 only)."""
import os, sys, re, pickle
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, "tools"); import make_deck_final3 as F
OUT = r"results_2050_analysis\figures"; DAT = r"results_2050_analysis\data"; os.makedirs(OUT, exist_ok=True); os.makedirs(DAT, exist_ok=True)
RUN = {"IC1": "nb_ccslow_ccu_cap16_dac0", "CTRY": "nb_ctry_ccslow_ccu_cap16_dac0", "MR": "mr_ccslow_ccu_cap16_dac0",
       "NATCAP": "ctryco2B_mr_ccslow_ccu_cap16_dac0", "RP10": "rp10nb_mr_ccslow_ccu_cap16_dac0", "CCSOPT": "mr_ccsopt_ccu_dac0", "FRLU": "frlu_mr_ccslow_ccu_cap16_dac0"}
SH = {"IC1": "NL+BE 17 zones", "CTRY": "NL+BE 1 node/country", "MR": "With neighbours", "NATCAP": "National CO2 caps", "RP10": "10 repr. days", "CCSOPT": "Optimistic CCS", "FRLU": "With FR + LU"}
COL = {"IC1": "#9aa3ad", "CTRY": "#1d3557", "MR": "#e76f51", "NATCAP": "#f4a261", "RP10": "#2a9d8f", "CCSOPT": "#457b9d", "FRLU": "#8d5a97"}
F.D = {k: pickle.load(open(rf"run_logs\{v}_NLBE.pkl", "rb")) for k, v in RUN.items()}
F.F = {k: pickle.load(open(rf"run_logs\{v}.pkl", "rb")) for k, v in RUN.items()}
F.X = {k: pd.read_pickle(rf"run_logs\{v}_xbbio.pkl") for k, v in RUN.items()}
F.SH, F.COL = SH, COL
D, CN, style = F.D, F.CN, F.style
GROUPS = {"A": ["IC1", "CTRY", "MR"], "B": ["MR", "NATCAP", "RP10", "CCSOPT", "FRLU"]}
# refinery add-on (same convention as run_logs\_decarb_refinery.py)
REN = {"S1": "NATCAP", "S2": "RP10", "S3": "CCSOPT", "S4": "FRLU"}
hc = {REN.get(k, k): v for k, v in pickle.load(open(r"run_logs\_hc_supply_all.pkl", "rb")).items()}
for k in RUN:
    rows = [dict(tech=t, region=c + "_ref", year=y, sector="refinery", output=v * 1e3, cc=t.endswith("MEA"), fuel="natural gas")
            for (t, c, y), v in hc[k].items() if c in CN and v > 0]
    D[k]["prod"] = pd.concat([D[k]["prod"][D[k]["prod"].sector != "refinery"], pd.DataFrame(rows)], ignore_index=True)
SECS = F.SECS + ["refinery"]
def sv(fig, name): p = os.path.join(OUT, name + ".png"); fig.savefig(p, dpi=400, bbox_inches="tight"); fig.savefig(p[:-4] + ".svg", bbox_inches="tight"); plt.close(fig); print("saved", p); return p
# ---------- 1 industry routes (share by route type)
def f_decarb(K, yrs, name):
    fig, axes = plt.subplots(1, len(K), figsize=(3.6 * len(K) + 1.5, 2.2 + .32 * len(SECS) * len(yrs)), sharey=True); rows = []
    for ax, k in zip(axes, K):
        p = D[k]["prod"]; p = p.assign(cat=p.apply(F.dcat, axis=1)); y = 0; ticks = []
        for sec in SECS:
            for yr in yrs:
                q = p[(p.sector == sec) & (p.year == yr)]; t = q.output.sum(); sh = q.groupby("cat").output.sum() / t * 100 if t > 0 else pd.Series(dtype=float); left = 0
                for l, c in F.DCAT:
                    v = sh.get(l, 0); ax.barh(y, v, .85, left=left, color=c, edgecolor="white", lw=.3); left += v
                    rows.append(dict(run=k, sector=sec, year=yr, route_type=l, share_pct=v, output_kt=t * v / 100))
                if t <= 0: ax.text(1, y, "no production in NL+BE", va="center", fontsize=6.5, color="#888")
                ticks.append((y, f"{sec}  {yr}" if (yr == yrs[0] and len(yrs) > 1) else (sec if len(yrs) == 1 else str(yr)))); y -= 1
            y -= .6 if len(yrs) > 1 else .15
        ax.set_yticks([t[0] for t in ticks], [t[1] for t in ticks], fontsize=7.5); ax.set_xlim(0, 100); ax.set_xlabel("% of NL+BE production")
        ax.set_title(SH[k], fontsize=11, fontweight="bold"); [ax.spines[s].set_visible(False) for s in ("top", "right")]
    fig.legend([plt.Rectangle((0, 0), 1, 1, color=c) for _, c in F.DCAT], [l for l, _ in F.DCAT], loc="lower center", ncol=6, frameon=False, fontsize=9)
    fig.tight_layout(rect=(0, .05 if len(yrs) > 1 else .09, 1, 1)); pd.DataFrame(rows).to_csv(os.path.join(DAT, name + ".csv"), index=False); return sv(fig, name)
# ---------- 2 electricity mix NL / BE
def f_elecmix(K, yrs, name):
    fig, axes = plt.subplots(1, 2, figsize=(max(9, 1.0 * len(K) * len(yrs) + 3), 5.2), sharey=True); rows = []; gap = len(yrs) + .6
    for ax, c in zip(axes, CN):
        xs, lab = [], []
        for j, k in enumerate(K):
            for i, y in enumerate(yrs):
                x = j * gap + i; xs.append(x); lab.append(str(y)[2:] if len(yrs) > 1 else SH[k].replace(" ", "\n", 1))
                s = F.sel(k, "supply", y); s = s[(s.carrier == "electricity") & (s.energy > 0) & (s.cn == c)]; b = 0
                for n, q, col in F.ELC:
                    v = s[q(s)].energy.sum() / 1e3; ax.bar(x, v, .85, bottom=b, color=col, label=n if (j, i, c) == (0, 0, "NL") else None, edgecolor="white", lw=.4); b += v
                    rows.append(dict(run=k, country=c, year=y, source=n, twh=v))
                ax.text(x, b + 3, f"{b:.0f}", ha="center", fontsize=7.5)
        ax.set_xticks(xs, lab, fontsize=8); ax.set_title(c, fontsize=13, fontweight="bold"); style(ax)
        if len(yrs) > 1:
            for j, k in enumerate(K): ax.annotate(SH[k], (j * gap + (len(yrs) - 1) / 2, 0), xytext=(0, -26), textcoords="offset points", ha="center", fontsize=8.5, fontweight="bold", annotation_clip=False)
    axes[0].set_ylabel("Electricity generation (TWh)"); fig.legend(loc="lower center", ncol=7, frameon=False, bbox_to_anchor=(.5, -.09))
    fig.tight_layout(); pd.DataFrame(rows).to_csv(os.path.join(DAT, name + ".csv"), index=False); return sv(fig, name)
# ---------- 3 energy panel (NL dark / BE light), one bar per run (and year)
def bars(ax, K, yrs, fn, title):
    gap = len(yrs) + .5; mx = 0; rows = []
    for j, k in enumerate(K):
        for i, y in enumerate(yrs):
            v = fn(k, y); x = j * gap + i; b = 0
            for c, a in (("NL", 1), ("BE", .45)): ax.bar(x, v[c], .8, bottom=b, color=COL[k], alpha=a, edgecolor="white"); b += v[c]
            ax.text(x, b, f"{b:.0f}", ha="center", va="bottom", fontsize=7.5); mx = max(mx, b); rows += [dict(panel=title, run=k, year=y, country=c, value=v[c]) for c in CN]
    if len(yrs) > 1: ax.set_xticks([j * gap + i for j in range(len(K)) for i in range(len(yrs))], [str(y)[2:] for _ in K for y in yrs], fontsize=7)
    else: ax.set_xticks(range(0, len(K) * int(gap), int(gap)) if gap == int(gap) else [j * gap for j in range(len(K))], [SH[k].replace(" ", "\n", 1) for k in K], fontsize=7.5)
    if len(yrs) > 1:
        for j, k in enumerate(K): ax.annotate(SH[k], (j * gap + 1, 0), xytext=(0, -20), textcoords="offset points", ha="center", fontsize=7, annotation_clip=False)
    ax.set_title(title, fontsize=10.5, fontweight="bold"); style(ax); ax.set_ylim(0, max(mx, 1e-9) * 1.18); return rows
def f_energy(K, yrs, name):
    items = [("Offshore wind (TWh)", lambda s: s.category == "wind offshore"), ("Nuclear (TWh)", lambda s: s.tech.str.startswith("nuclear")),
             ("Solar + onshore wind (TWh)", lambda s: s.category.isin(["solar PV", "wind onshore"])),
             ("H2 from electrolysis (TWh)", lambda s: (s.carrier == "hydrogen") & (s.category == "electrolysis")),
             ("H2 imported as LH2 (TWh)", lambda s: s.tech == "LH2-terminal"), ("H2 turbines (TWh el.)", lambda s: s.tech.str.startswith("CCGT-H2"))]
    fig, axes = plt.subplots(2, 3, figsize=(5.2 * 3 * (1.4 if len(yrs) > 1 else 1), 9)); rows = []
    for ax, (t, q) in zip(axes.flat, items): rows += bars(ax, K, yrs, lambda k, y, q=q: F.sup(k, q, y), t)
    fig.text(.5, -.01, "Dark = NL, light = BE", ha="center", fontsize=9); fig.tight_layout(); pd.DataFrame(rows).to_csv(os.path.join(DAT, name + ".csv"), index=False); return sv(fig, name)
# ---------- 4 H2 and electricity balance NL+BE
U = pd.read_pickle(r"run_logs\_use_elec_h2_all.pkl"); DM = pd.read_pickle(r"run_logs\_elec_dem_xb_all.pkl")
U["run"] = U.run.replace(REN); DM["run"] = DM.run.replace(REN)
def ucat(t):
    if re.match(r"^(PEM|SOEC|AEC)", t): return "Electrolysis"
    if re.search(r"heatpump|electric-heating|electric-boiler", t): return "Building heat (HP, e-heating)"
    if re.search(r"storage|battery", t): return "Storage charging"
    if re.match(r"^(CCGT|OCGT)-H2", t): return "Power generation (H2 turbines)"
    if re.match(r"^REF", t): return "Refineries"
    return "Industry"
U["cat"] = U.tech.map(ucat)
H2S = [("Electrolysis", lambda s: s.category == "electrolysis", "#2a9d8f"), ("LH2 import terminal", lambda s: s.tech == "LH2-terminal", "#457b9d"),
       ("SMR (gas)", lambda s: s.tech.str.contains("SMR|ATR", regex=True), "#6c757d")]
def xbnet(k, car, y):
    x = F.X[k]["xb"]; x = x[(x.year == y) & (x.car == car)]; return (x[~x.o.isin(CN) & x.d.isin(CN)].v.sum() - x[x.o.isin(CN) & ~x.d.isin(CN)].v.sum()) / 1e3
def f_balance(K, yrs, name):
    rows = []
    for k in K:
        for y in yrs:
            s = F.sel(k, "supply", y); s = s[(s.carrier == "hydrogen") & (s.energy > 0)]; tot_ = s.energy.sum() / 1e3; acc = 0
            for n, q, _ in H2S: v = s[q(s)].energy.sum() / 1e3; acc += v; rows.append(dict(run=k, year=y, carrier="H2", side="supply", item=n, twh=v))
            rows.append(dict(run=k, year=y, carrier="H2", side="supply", item="Other H2 supply", twh=tot_ - acc))
            ni = xbnet(k, "H2", y); rows.append(dict(run=k, year=y, carrier="H2", side="supply" if ni > 0 else "use", item="Net pipeline import" if ni > 0 else "Net pipeline export", twh=abs(ni)))
            u = U[(U.run == k) & (U.year == y)]
            for car in ("H2", "elec"):
                for c, v in u[u.carrier == car].groupby("cat").twh.sum().items(): rows.append(dict(run=k, year=y, carrier=car, side="use", item=c, twh=v))
            dm = DM[(DM.run == k) & (DM.year == y)]
            rows.append(dict(run=k, year=y, carrier="elec", side="use", item="Fixed demand (buildings, transport, other)", twh=dm[dm.tech.str.startswith("demand")].twh.sum()))
            ne = -dm[dm.tech == "net import"].twh.sum()
            rows.append(dict(run=k, year=y, carrier="elec", side="use" if ne > 0 else "supply", item="Net export" if ne > 0 else "Net import", twh=abs(ne)))
    R = pd.DataFrame(rows); R.to_csv(os.path.join(DAT, name + ".csv"), index=False)
    fig, axes = plt.subplots(1, 3, figsize=(7 + 1.2 * len(K) * len(yrs), 5.6), gridspec_kw=dict(width_ratios=[1, 1, 1.3]))
    def stack(ax, sub, title):
        items = list(dict.fromkeys(sub.item)); cm = plt.get_cmap("tab20"); gap = len(yrs) + .5; xs = []; lab = []
        for j, k in enumerate(K):
            for i, y in enumerate(yrs):
                x = j * gap + i; xs.append(x); lab.append(str(y)[2:] if len(yrs) > 1 else SH[k].replace(" ", "\n", 1)); b = 0
                for n, it in enumerate(items):
                    v = sub[(sub.run == k) & (sub.year == y) & (sub.item == it)].twh.sum()
                    ax.bar(x, v, .8, bottom=b, color=cm(n % 20), label=it if (j, i) == (0, 0) else None, edgecolor="white", lw=.3); b += v
                ax.text(x, b, f"{b:.0f}", ha="center", va="bottom", fontsize=7.5)
        ax.set_xticks(xs, lab, fontsize=7.5); ax.set_title(title, fontsize=11, fontweight="bold"); style(ax); ax.legend(frameon=False, fontsize=7.5, loc="upper center", bbox_to_anchor=(.5, -.13), ncol=1)
        if len(yrs) > 1:
            for j, k in enumerate(K): ax.annotate(SH[k], (j * gap + 1, 0), xytext=(0, -22), textcoords="offset points", ha="center", fontsize=7, annotation_clip=False)
    stack(axes[0], R[(R.carrier == "H2") & (R.side == "supply")], "Hydrogen supply NL+BE (TWh)")
    stack(axes[1], R[(R.carrier == "H2") & (R.side == "use")], "Hydrogen use NL+BE (TWh)")
    stack(axes[2], R[(R.carrier == "elec") & (R.side == "use")], "Electricity use NL+BE (TWh)")
    axes[0].set_ylabel("TWh/yr"); fig.tight_layout(); return sv(fig, name)
# ---------- 5 CO2 capture by source and destination (NL+BE)
def co2d(k, y):
    st = D[k]["co2store"].query("year==@y").co2.sum() / 1e3
    c = D[k]["co2net"].query("year==@y and role=='used / injected'"); u = c[~c.tech.str.startswith("CO2-injection")].co2.sum() / 1e3
    p = F.F[k]["co2pipe"]; p = p[p.year == y]; nb = lambda s: s.str[:2].isin(CN)
    ex = (p[nb(p.origin) & ~nb(p.dest)].co2.sum() - p[~nb(p.origin) & nb(p.dest)].co2.sum()) / 1e3 if len(p) else 0
    return dict(stored_NL=st, CCU_methanol=u, net_export=ex, net_emissions=D[k]["emis"].query("year==@y").co2.sum() / 1e3)
def f_co2(K, yrs, name):
    rows = []
    for k in K:
        for y in yrs:
            c = F.sel(k, "co2net", y); c = c[c.role == "captured"]
            for s, v in c.groupby("source").co2.sum().items(): rows.append(dict(run=k, year=y, kind="captured", item=s, mt=v / 1e3))
            for n, v in co2d(k, y).items(): rows.append(dict(run=k, year=y, kind="destination" if n != "net_emissions" else "emissions", item=n, mt=v))
    R = pd.DataFrame(rows); R.to_csv(os.path.join(DAT, name + ".csv"), index=False)
    srcs = list(R[R.kind == "captured"].groupby("item").mt.sum().sort_values(ascending=False).index); cm = plt.get_cmap("tab20")
    DST = [("stored_NL", "Stored in NL", "#2a9d8f"), ("CCU_methanol", "Used in methanol (CCU)", F.ACC), ("net_export", "Net export (storage abroad)", "#457b9d")]
    fig, axes = plt.subplots(1, 2, figsize=(6 + 1.5 * len(K) * len(yrs), 5.8)); gap = len(yrs) + .5
    for ax, kind in zip(axes, ("captured", "destination")):
        xs = []; lab = []
        for j, k in enumerate(K):
            for i, y in enumerate(yrs):
                x = j * gap + i; xs.append(x); lab.append(str(y)[2:] if len(yrs) > 1 else SH[k].replace(" ", "\n", 1)); b = 0; r = R[(R.run == k) & (R.year == y)]
                lst = [(s, s, cm(n % 20)) for n, s in enumerate(srcs)] if kind == "captured" else DST
                for key, l, col in lst:
                    v = r[r.item == key].mt.sum(); ax.bar(x, v, .8, bottom=b, color=col, label=l if (j, i) == (0, 0) else None, edgecolor="white", lw=.3); b += v
                ax.text(x, b, f"{b:.0f}", ha="center", va="bottom", fontsize=7.5)
                if kind == "destination" and k == "NATCAP":
                    em = r[r.kind == "emissions"].mt.sum(); ax.plot([x - .4, x + .4], [em, em], color="k", lw=2, label="NL+BE net emissions (national caps only)" if i == 0 else None)
        ax.set_xticks(xs, lab, fontsize=7.5); style(ax); ax.set_ylabel("Mt CO2/yr")
        ax.set_title("CO2 captured in NL+BE, by source" if kind == "captured" else "Where the captured CO2 goes", fontsize=11, fontweight="bold")
        ax.legend(frameon=False, fontsize=7.5, loc="upper center", bbox_to_anchor=(.5, -.13), ncol=2)
        if len(yrs) > 1:
            for j, k in enumerate(K): ax.annotate(SH[k], (j * gap + 1, 0), xytext=(0, -22), textcoords="offset points", ha="center", fontsize=7, annotation_clip=False)
    fig.tight_layout(); return sv(fig, name)
# ---------- 6 KPI table 2050
def kpi():
    rows = []
    for k in RUN:
        d = co2d(k, 2050); t = lambda q: F.tot(F.sup(k, q))
        rows.append(dict(run=k, label=SH[k], objective_M=F.F[k]["obj"].sum() / 1e6, NLBE_net_emis_Mt=d["net_emissions"],
            captured_Mt=D[k]["co2net"].query("year==2050 and role=='captured'").co2.sum() / 1e3, stored_NL_Mt=d["stored_NL"], CCU_Mt=d["CCU_methanol"], CO2_net_export_Mt=d["net_export"],
            offshore_wind_TWh=t(lambda s: s.category == "wind offshore"), nuclear_TWh=t(lambda s: s.tech.str.startswith("nuclear")),
            electrolysis_H2_TWh=t(lambda s: (s.carrier == "hydrogen") & (s.category == "electrolysis")), LH2_import_TWh=t(lambda s: s.tech == "LH2-terminal"),
            elec_net_import_TWh=DM[(DM.run == k) & (DM.year == 2050) & (DM.tech == "net import")].twh.sum(),
            refinery_output_NLBE=sum(v for (tt, c, y), v in hc[k].items() if c in CN and y == 2050)))
    T = pd.DataFrame(rows).round(2); T.to_csv(os.path.join(DAT, "kpi_2050.csv"), index=False); print(T.to_string()); return T
if __name__ == "__main__":
    for g, K in GROUPS.items():
        for tag, yrs in (("all", [2030, 2040, 2050]), ("2050", [2050])):
            f_decarb(K, yrs, f"1_industry_routes_{g}_{tag}")
            f_elecmix(K, yrs, f"2_elecmix_{g}_{tag}")
            f_energy(K, yrs, f"3_energy_{g}_{tag}")
            f_balance(K, yrs, f"4_h2_elec_balance_{g}_{tag}")
            f_co2(K, yrs, f"5_co2_capture_dest_{g}_{tag}")
    kpi()






