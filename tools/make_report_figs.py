r"""Report figures (no figure titles). Main runs (IC1/CTRY/MR) x 2030/40/50 -> A_*; sensitivities x 2050 -> B_*.
NL and BE as side-by-side panels. Reuses make_report_2050 data loading."""
import os, sys, re
import pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, "tools"); import make_report_2050 as R
F, D, CN = R.F, R.D, R.CN
OUT, DAT = R.OUT, R.DAT
R.SH.update({"MR": "Mixed resolution", "IC1": "NL+BE regional clusters", "CTRY": "NL+BE country level"}); SH = R.SH
SETS = {"A": (["IC1", "CTRY", "MR"], [2030, 2040, 2050]), "B": (["MR", "NATCAP", "RP10", "CCSOPT", "FRLU"], [2050])}
ELC = [("Offshore wind", lambda s: s.category == "wind offshore", "#1f5f8b"), ("Onshore wind", lambda s: s.category == "wind onshore", "#5fa8d3"),
       ("Solar PV", lambda s: s.category == "solar PV", "#f2b134"), ("Nuclear", lambda s: s.tech.str.startswith("nuclear"), "#7b3294"),
       ("Gas power", lambda s: s.tech.str.match(r"^(CCGT|OCGT)(?!-H2)") & ~s.tech.str.contains("+CC", regex=False), "#8c8c8c"), ("Gas power + CCS", lambda s: s.tech.str.match(r"^(CCGT|OCGT)(?!-H2)") & s.tech.str.contains("+CC", regex=False), "#c1121f"),
       ("Hydrogen turbines", lambda s: s.tech.str.startswith("CCGT-H2"), "#2a9d8f"), ("Biomass power", lambda s: s.tech.str.startswith("bio") & ~s.tech.str.contains("+CC", regex=False), "#6a994e"), ("Biomass power + CCS", lambda s: s.tech.str.startswith("bio") & s.tech.str.contains("+CC", regex=False), "#386641"),
       ("Coal power", lambda s: s.tech.str.startswith("SCPC"), "#3d2b1f"), ("Oil power", lambda s: s.tech.str.startswith("oil-eng"), "#7f5539"),
       ("Waste incineration", lambda s: s.tech.str.startswith("wasteST"), "#b5838d"), ("Hydro (run-of-river)", lambda s: s.tech.str.startswith("RoR"), "#48cae4"),
       ("Battery discharge", lambda s: s.tech.str.startswith("battery-storage"), "#ff2d95")]
H2S = [("Electrolysis", lambda s: s.category == "electrolysis", "#2a9d8f"), ("LH2 import terminal", lambda s: s.tech == "LH2-terminal", "#457b9d"),
       ("Gas reforming", lambda s: s.tech.str.contains("SMR|ATR", regex=True) & ~s.tech.str.contains("+CC", regex=False), "#6c757d"), ("Gas reforming + CCS", lambda s: s.tech.str.contains("SMR|ATR", regex=True) & s.tech.str.contains("+CC", regex=False), "#c1121f")]
UCOL = {"Fixed demand (buildings, transport, other)": "#adb5bd", "Industry": "#e76f51", "Electrolysis": "#2a9d8f", "Building heat (HP, e-heating)": "#f4a261",
        "Battery charging": "#ff2d95", "Power generation (H2 turbines)": "#90be6d", "Refineries": "#6c757d", "Net export": "#1d3557", "Net import": "#a8dadc",
        "Net pipeline export": "#1d3557", "Net pipeline import": "#a8dadc", "Other H2 supply": "#ced4da"}
def xbnet(k, car, y, c):
    x = F.X[k]["xb"]; x = x[(x.year == y) & (x.car == car)]; return (x[(x.o != c) & (x.d == c)].v.sum() - x[(x.o == c) & (x.d != c)].v.sum()) / 1e3
# ---- item functions: (k, y, c) -> list of (item, value, colour)
def it_elgen(k, y, c):
    s = F.sel(k, "supply", y); s = s[(s.carrier == "electricity") & (s.energy > 0) & (s.cn == c)]
    out = [(n, s[q(s)].energy.sum() / 1e3, col) for n, q, col in ELC]
    rest = s.energy.sum() / 1e3 - sum(v for _, v, _ in out)
    out.append(("Other", max(rest, 0), "#ced4da")); return out
def it_h2gen(k, y, c):
    s = F.sel(k, "supply", y); s = s[(s.carrier == "hydrogen") & (s.energy > 0) & (s.cn == c)]; out = []; acc = 0
    for n, q, col in H2S: v = s[q(s)].energy.sum() / 1e3; acc += v; out.append((n, v, col))
    out.append(("Other H2 supply", s.energy.sum() / 1e3 - acc, UCOL["Other H2 supply"]))
    ni = xbnet(k, "H2", y, c); out.append(("Net pipeline import", max(ni, 0), UCOL["Net pipeline import"])); return out
HATCH = {"Gas power + CCS": "///", "Biomass power + CCS": "///", "Gas reforming + CCS": "///"}
UCATS = ["Industry", "Refineries", "Electrolysis", "Building heat (HP, e-heating)", "Battery charging", "Power generation (H2 turbines)"]
def uses(k, y, c, car):
    u = R.U[(R.U.run == k) & (R.U.year == y) & (R.U.cn == c) & (R.U.carrier == car)]; g = u.groupby("cat").twh.sum().rename({"Storage charging": "Battery charging"})
    return [(n, g.get(n, 0), UCOL[n]) for n in UCATS]
def it_eluse(k, y, c):
    dm = R.DM[(R.DM.run == k) & (R.DM.year == y) & (R.DM.cn == c)]
    out = [("Fixed demand (buildings, transport, other)", dm[dm.tech.str.startswith("demand")].twh.sum(), UCOL["Fixed demand (buildings, transport, other)"])] + uses(k, y, c, "elec")
    ne = -dm[dm.tech == "net import"].twh.sum(); out.append(("Net export", max(ne, 0), UCOL["Net export"])); return out
def it_h2use(k, y, c):
    out = uses(k, y, c, "H2"); ni = xbnet(k, "H2", y, c); out.append(("Net pipeline export", max(-ni, 0), UCOL["Net pipeline export"])); return out
def stackfig(K, yrs, fn, ylabel, name, vertical=False):
    single = len(yrs) == 1; gap = len(yrs) + .6
    w = (1.25 * len(K) + 1.5) * 2 if single else 1.0 * len(K) * len(yrs) * 2 + 2
    fig, axes = plt.subplots(2, 1, figsize=(w / 2 + 1, 9), sharey=True, sharex=True) if vertical else plt.subplots(1, 2, figsize=(w, 5), sharey=True); rows = []; used = {}
    for ax, c in zip(axes, CN):
        xs, lab = [], []
        for j, k in enumerate(K):
            for i, y in enumerate(yrs):
                x = j * gap + i; xs.append(x); lab.append(SH[k].replace(" ", "\n", 1) if single else str(y)); b = 0
                for n, v, col in fn(k, y, c):
                    rows.append(dict(run=k, label=SH[k], country=c, year=y, item=n, twh=v))
                    if v > 0: ax.bar(x, v, .8, bottom=b, color=col, edgecolor="white", lw=.4, hatch=HATCH.get(n)); b += v; used.setdefault(n, col) if v > .05 else None
                ax.text(x, b, f"{b:.0f}", ha="center", va="bottom", fontsize=7.5)
        ax.set_xticks(xs, lab, fontsize=8); F.style(ax)
        ax.text(.02, .98, c, transform=ax.transAxes, fontsize=12, fontweight="bold", va="top")
        if not single:
            for j, k in enumerate(K): ax.annotate(SH[k], (j * gap + (len(yrs) - 1) / 2, 0), xytext=(0, -24), textcoords="offset points", ha="center", fontsize=9, fontweight="bold", annotation_clip=False)
    lo, hi = axes[0].get_ylim(); [a.set_ylim(0, hi * 1.06) for a in axes]
    [a.set_ylabel(ylabel) for a in (axes if vertical else axes[:1])]
    if vertical: axes[0].tick_params(labelbottom=True)
    fig.legend([plt.Rectangle((0, 0), 1, 1, facecolor=c, edgecolor="white", hatch=HATCH.get(n)) for n, c in used.items()], list(used), loc="upper center", ncol=4, frameon=False, fontsize=8.5, bbox_to_anchor=(.5, 0))
    fig.tight_layout()
    if vertical: fig.subplots_adjust(hspace=.35)
    pd.DataFrame(rows).to_csv(os.path.join(DAT, name + ".csv"), index=False); return R.sv(fig, name)
def industry(K, yrs, name):
    p = R.f_decarb(K, yrs, name); return p
def industry_vertical(K, yr, name):
    """One small panel per sector (stacked vertically), one horizontal bar per run."""
    import matplotlib.pyplot as plt, pandas as pd, os
    F = R.F; SECS = R.SECS; rows = []
    fig, axes = plt.subplots(len(SECS), 1, figsize=(16/2.54, (0.24*len(K)+0.5)*len(SECS)/2.54 + 0.9), sharex=True)
    for ax, sec in zip(axes, SECS):
        for j, k in enumerate(K):
            p = R.D[k]["prod"]; p = p.assign(cat=p.apply(F.dcat, axis=1))
            q = p[(p.sector == sec) & (p.year == yr)]; t = q.output.sum()
            sh = q.groupby("cat").output.sum() / t * 100 if t > 0 else pd.Series(dtype=float); left = 0
            for l, c in F.DCAT:
                v = sh.get(l, 0); ax.barh(-j, v, .8, left=left, color=c, edgecolor="white", lw=.3); left += v
                rows.append(dict(run=k, sector=sec, year=yr, route_type=l, share_pct=v, output_kt=t * v / 100))
            if t <= 0: ax.text(1, -j, "no production in NL+BE", va="center", fontsize=6.5, color="#888")
        ax.set_yticks([-j for j in range(len(K))], [R.SH[k] for k in K], fontsize=7)
        ax.set_xlim(0, 100); ax.set_ylim(-len(K) + .45, .55)
        ax.set_title(sec[0].upper() + sec[1:], fontsize=8.5, fontweight="bold", loc="left", pad=2)
        for sp in ("top", "right"): ax.spines[sp].set_visible(False)
        ax.tick_params(axis="x", labelsize=7)
    axes[-1].set_xlabel("% of NL+BE production", fontsize=8)
    fig.legend([plt.Rectangle((0, 0), 1, 1, color=c) for _, c in F.DCAT], [l for l, _ in F.DCAT],
               loc="lower center", ncol=2, frameon=False, fontsize=7.5)
    fig.tight_layout(rect=(0, .045, 1, 1), h_pad=.6)
    pd.DataFrame(rows).to_csv(os.path.join(R.DAT, name + ".csv"), index=False)
    return R.sv(fig, name)

def industry_v2(K, yr, name, ncol=3):
    """Original B5 layout (sectors as rows, one panel per run) wrapped into rows of ncol panels."""
    import matplotlib.pyplot as plt, pandas as pd, os, math
    F = R.F; SECS = R.SECS; rows = []; nr = math.ceil(len(K) / ncol)
    fig, axes = plt.subplots(nr, ncol, figsize=(3.6 * ncol + 1.5, (0.6 + .32 * len(SECS)) * nr + .8), sharey=True, squeeze=False)
    for i, ax in enumerate(axes.flat):
        if i >= len(K): ax.axis("off"); continue
        k = K[i]; p = R.D[k]["prod"]; p = p.assign(cat=p.apply(F.dcat, axis=1)); ticks = []
        for y, sec in enumerate(SECS):
            q = p[(p.sector == sec) & (p.year == yr)]; t = q.output.sum()
            sh = q.groupby("cat").output.sum() / t * 100 if t > 0 else pd.Series(dtype=float); left = 0
            for l, c in F.DCAT:
                v = sh.get(l, 0); ax.barh(-y, v, .85, left=left, color=c, edgecolor="white", lw=.3); left += v
                rows.append(dict(run=k, sector=sec, year=yr, route_type=l, share_pct=v, output_kt=t * v / 100))
            if t <= 0: ax.text(1, -y, "no production in NL+BE", va="center", fontsize=6.5, color="#888")
            ticks.append((-y, sec))
        ax.set_yticks([t[0] for t in ticks], [t[1] for t in ticks], fontsize=7.5); ax.tick_params(axis="y", labelleft=(i % ncol == 0))
        ax.set_xlim(0, 100); ax.set_xlabel("% of NL+BE production", fontsize=8)
        ax.set_title(R.SH[k], fontsize=11, fontweight="bold"); [ax.spines[sp].set_visible(False) for sp in ("top", "right")]
    h = [plt.Rectangle((0, 0), 1, 1, color=c) for _, c in F.DCAT]; L = [l for l, _ in F.DCAT]
    if len(K) < nr * ncol:
        axes.flat[len(K)].legend(h, L, loc="center", frameon=False, fontsize=9)
        fig.tight_layout()
    else:
        fig.legend(h, L, loc="lower center", ncol=3, frameon=False, fontsize=9); fig.tight_layout(rect=(0, .06, 1, 1))
    pd.DataFrame(rows).to_csv(os.path.join(R.DAT, name + ".csv"), index=False)
    return R.sv(fig, name)

if __name__ == "__main__":
    for g, (K, yrs) in SETS.items():
        stackfig(K, yrs, it_elgen, "Electricity generation (TWh/yr)", f"{g}1_electricity_generation")
        stackfig(K, yrs, it_h2gen, "Hydrogen supply (TWh/yr)", f"{g}2_hydrogen_supply")
        stackfig(K, yrs, it_eluse, "Electricity consumption (TWh/yr)", f"{g}3_electricity_consumption")
        stackfig(K, yrs, it_h2use, "Hydrogen consumption (TWh/yr)", f"{g}4_hydrogen_consumption")
        industry(K, yrs, f"{g}5_industry_routes")
    for g, (K, yrs) in SETS.items():
        stackfig(K, yrs, it_elgen, "Electricity generation (TWh/yr)", f"{g}1_electricity_generation_vertical", vertical=True)
        stackfig(K, yrs, it_h2gen, "Hydrogen supply (TWh/yr)", f"{g}2_hydrogen_supply_vertical", vertical=True)
        stackfig(K, yrs, it_eluse, "Electricity consumption (TWh/yr)", f"{g}3_electricity_consumption_vertical", vertical=True)
        stackfig(K, yrs, it_h2use, "Hydrogen consumption (TWh/yr)", f"{g}4_hydrogen_consumption_vertical", vertical=True)
    industry_vertical(SETS["B"][0], 2050, "B5_industry_routes_vertical")
    industry_v2(SETS["B"][0], 2050, "B5_industry_routes_vertical_v2")








