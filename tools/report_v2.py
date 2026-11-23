r"""Focused report: supply mixes, industry decarbonisation, CO2, costs.

Usage:
  .\.venv\Scripts\python.exe tools\report_v2.py RESULTS.sqlite -m MODEL.sqlite -o OUTDIR
"""
from __future__ import annotations
import argparse, os, re, sys, warnings, collections
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import FuncFormatter
from spinedb_api import DatabaseMapping
from spinedb_api.parameter_value import from_database

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import postprocess as PP

warnings.filterwarnings("ignore")

plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white",
    "axes.edgecolor": "#b0b7c3", "axes.linewidth": .8,
    "axes.grid": True, "grid.color": "#dfe3ea", "grid.linewidth": .7,
    "axes.axisbelow": True, "font.size": 10,
    "axes.titlesize": 12, "axes.titleweight": "bold",
    "legend.frameon": False, "savefig.dpi": 160,
})

PALETTE = ["#2d6a9f", "#e08214", "#4daf4a", "#984ea3", "#d62728", "#17becf",
           "#8c564b", "#7f7f7f", "#bcbd22", "#1b9e77", "#e7298a", "#66a61e",
           "#a6761d", "#386cb0", "#f0027f", "#bf5b17", "#999999", "#66c2a5"]


def colors(n):
    return [PALETTE[i % len(PALETTE)] for i in range(n)]


def thousands(ax):
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{v:,.0f}"))


def grouped_bar(ax, piv, ylabel, legend_title=None, pct=False):
    """One bar per year, series side by side. piv: index=year, columns=series."""
    piv = piv.loc[:, piv.abs().sum().sort_values(ascending=False).index]
    if pct:
        piv = piv.div(piv.sum(axis=1).replace(0, np.nan), axis=0) * 100
    years = list(piv.index)
    cols = list(piv.columns)
    x = np.arange(len(years), dtype=float)
    w = min(0.8 / max(len(cols), 1), 0.22)
    cs = colors(len(cols))
    for k, c in enumerate(cols):
        off = (k - (len(cols) - 1) / 2) * w
        ax.bar(x + off, piv[c].values, w, label=str(c), color=cs[k],
               edgecolor="white", linewidth=.4)
    ax.set_xticks(x); ax.set_xticklabels([str(int(y)) for y in years])
    ax.set_ylabel(ylabel)
    thousands(ax)
    ax.grid(axis="x", visible=False)
    ax.legend(title=legend_title, fontsize=8, ncol=1,
              loc="center left", bbox_to_anchor=(1.01, .5))
    return piv


def stacked_bar(ax, piv, ylabel, legend_title=None, pct=False):
    piv = piv.loc[:, piv.abs().sum().sort_values(ascending=False).index]
    if pct:
        piv = piv.div(piv.sum(axis=1).replace(0, np.nan), axis=0) * 100
    years = [str(int(y)) for y in piv.index]
    cs = colors(len(piv.columns))
    bottom = np.zeros(len(piv))
    for k, c in enumerate(piv.columns):
        v = piv[c].values.astype(float)
        ax.bar(years, v, .55, bottom=bottom, label=str(c), color=cs[k],
               edgecolor="white", linewidth=.5)
        bottom += v
    ax.set_ylabel(ylabel)
    thousands(ax)
    ax.grid(axis="x", visible=False)
    ax.legend(title=legend_title, fontsize=8,
              loc="center left", bbox_to_anchor=(1.01, .5))
    return piv

# ------------------------------------------------------------------ figures
def fig_supply_mix(supply, carrier, title):
    sub = supply[supply["carrier"] == carrier]
    fig, axes = plt.subplots(1, 2, figsize=(15.5, 6.4))
    if sub.empty:
        for a in axes:
            a.text(.5, .5, f"no {carrier} supply in results", ha="center")
            a.set_axis_off()
        fig.suptitle(title, fontsize=14, fontweight="bold")
        return fig, pd.DataFrame()
    piv = sub.pivot_table(index="year", columns="category", values="energy",
                          aggfunc="sum").fillna(0)
    piv = piv.loc[:, piv.sum() > 0]
    grouped_bar(axes[0], piv, "TWh per year")
    axes[0].set_title("Supply by technology")
    stacked_bar(axes[1], piv.copy(), "% of supply", pct=True)
    axes[1].set_title("Share of supply")
    axes[1].set_ylim(0, 100)
    fig.suptitle(title, fontsize=14, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, .94))
    return fig, piv


def fig_industry_sector(prod, sectors, title):
    """Capacity mix of production routes per sector, across years."""
    n = len(sectors)
    ncol = min(3, n)
    nrow = int(np.ceil(n / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(5.6 * ncol, 4.6 * nrow),
                             squeeze=False)
    tables = {}
    for i, sec in enumerate(sectors):
        ax = axes[i // ncol][i % ncol]
        sub = prod[prod["sector"] == sec]
        if sub.empty:
            ax.text(.5, .5, "no output", ha="center"); ax.set_axis_off(); continue
        piv = sub.pivot_table(index="year", columns="route", values="output",
                              aggfunc="sum").fillna(0)
        piv = piv.loc[:, piv.sum() > 0]
        piv = piv.div(piv.sum(axis=1).replace(0, np.nan), axis=0) * 100
        tables[sec] = piv
        years = [str(int(y)) for y in piv.index]
        cs = colors(len(piv.columns))
        bottom = np.zeros(len(piv))
        for k, c in enumerate(piv.columns):
            v = piv[c].values.astype(float)
            ax.bar(years, v, .55, bottom=bottom, label=str(c), color=cs[k],
                   edgecolor="white", linewidth=.5)
            bottom += v
        ax.set_title(sec); ax.set_ylabel("% of sector output")
        ax.set_ylim(0, 100); ax.grid(axis="x", visible=False)
        ax.legend(fontsize=7, loc="upper center", bbox_to_anchor=(.5, -.09),
                  ncol=2)
    for j in range(n, nrow * ncol):
        axes[j // ncol][j % ncol].set_axis_off()
    fig.suptitle(title, fontsize=14, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, .95))
    return fig, tables


def fig_co2_system(emis, co2net, co2store):
    """Whole-model CO2: gross emitted, captured, injected, net."""
    fig, axes = plt.subplots(1, 3, figsize=(16.5, 5.6))
    gross = emis[emis.co2 > 0].groupby("year")["co2"].sum()
    neg = -emis[emis.co2 < 0].groupby("year")["co2"].sum()
    cap = (co2net[co2net.role == "captured"].groupby("year")["co2"].sum()
           if len(co2net) else pd.Series(dtype=float))
    inj = (co2store.groupby("year")["co2"].sum()
           if len(co2store) else pd.Series(dtype=float))
    years = sorted(set(gross.index) | set(cap.index) | set(inj.index))
    t = pd.DataFrame({
        "emitted to atmosphere": gross.reindex(years).fillna(0),
        "removed from atmosphere": neg.reindex(years).fillna(0),
        "captured": cap.reindex(years).fillna(0),
        "injected to storage": inj.reindex(years).fillna(0),
    })
    grouped_bar(axes[0], t, "Mt CO2 per year")
    axes[0].set_title("CO2 balance, NL+BE")

    bysrc = (co2net[co2net.role == "captured"]
             .pivot_table(index="year", columns="source", values="co2",
                          aggfunc="sum").fillna(0) if len(co2net) else pd.DataFrame())
    if not bysrc.empty:
        stacked_bar(axes[1], bysrc, "Mt CO2 captured")
    else:
        axes[1].set_axis_off()
    axes[1].set_title("Captured CO2 by origin")

    bycat = emis[emis.co2 > 0].pivot_table(index="year", columns="category",
                                           values="co2", aggfunc="sum").fillna(0)
    bycat = bycat.loc[:, bycat.sum().sort_values(ascending=False).index[:10]]
    stacked_bar(axes[2], bycat, "Mt CO2 emitted")
    axes[2].set_title("Gross emissions by sector")
    fig.suptitle("CO2 emissions and capture - whole model (NL + BE)",
                 fontsize=14, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, .93))
    return fig, t

def fig_co2_maps(gdf, emis, co2net, co2store, co2pipe, years):
    """Geographic CO2: emitted (top row) and captured (bottom row) per region."""
    fig, axes = plt.subplots(2, len(years), figsize=(4.6 * len(years), 10.4),
                             squeeze=False)
    em = (emis[emis.co2 > 0].pivot_table(index="region", columns="year",
                                         values="co2", aggfunc="sum")
          .reindex(gdf.index).fillna(0))
    cp = (co2net[co2net.role == "captured"]
          .pivot_table(index="region", columns="year", values="co2",
                       aggfunc="sum").reindex(gdf.index).fillna(0)
          if len(co2net) else pd.DataFrame(index=gdf.index))
    for row, (piv, cmap, lab) in enumerate(
            ((em, "OrRd", "CO2 emitted"), (cp, "GnBu", "CO2 captured"))):
        vmax = float(np.nanmax(piv.values)) if piv.size else 1.0
        vmax = vmax if vmax > 0 else 1.0
        for j, y in enumerate(years):
            ax = axes[row][j]
            g = gdf.copy()
            g["v"] = piv[y] if y in getattr(piv, "columns", []) else 0.0
            g.plot(column="v", ax=ax, cmap=cmap, vmin=0, vmax=vmax,
                   edgecolor="white", linewidth=.7)
            for rid, r in g.iterrows():
                c = r.geometry.representative_point()
                ax.annotate(f"{rid}\n{r['v']:,.0f}", (c.x, c.y), ha="center",
                            fontsize=6)
            ax.set_axis_off()
            ax.set_title(f"{lab} - {int(y)}", fontsize=11)
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(0, vmax))
        fig.colorbar(sm, ax=axes[row].tolist(), fraction=.03, pad=.02)
    fig.suptitle("CO2 emitted and captured by region", fontsize=14,
                 fontweight="bold")
    return fig


def fig_co2_flows(gdf, co2net, co2pipe, co2store, years):
    """Where captured CO2 goes: pipeline arrows + injection sites."""
    fig, axes = plt.subplots(1, len(years), figsize=(5.2 * len(years), 6.2),
                             squeeze=False)
    cap = (co2net[co2net.role == "captured"]
           .pivot_table(index="region", columns="year", values="co2",
                        aggfunc="sum").reindex(gdf.index).fillna(0)
           if len(co2net) else pd.DataFrame(index=gdf.index))
    vmax = float(np.nanmax(cap.values)) if cap.size else 1.0
    vmax = vmax if vmax > 0 else 1.0
    cent = {r: g.representative_point() for r, g in gdf.geometry.items()}
    for j, y in enumerate(years):
        ax = axes[0][j]
        g = gdf.copy()
        g["v"] = cap[y] if y in getattr(cap, "columns", []) else 0.0
        g.plot(column="v", ax=ax, cmap="GnBu", vmin=0, vmax=vmax,
               edgecolor="white", linewidth=.7)
        inj = (set(co2store[co2store.year == y]["region"].dropna())
               if len(co2store) else set())
        for rid, r in g.iterrows():
            c = cent[rid]
            ax.annotate(f"{rid}\n{r['v']:,.0f}", (c.x, c.y), ha="center",
                        fontsize=6)
            if rid in inj:
                ax.plot(c.x, c.y, "o", ms=15, mfc="none", mec="#8e44ad", mew=2.2)
        if len(co2pipe):
            pp = co2pipe[co2pipe.year == y]
            mx = pp["co2"].max() if len(pp) else 0
            for _, r in pp.iterrows():
                o, d = r["origin"], r["dest"]
                if not o or not d or o not in cent or d not in cent:
                    continue
                a, b = cent[o], cent[d]
                ax.annotate("", xy=(b.x, b.y), xytext=(a.x, a.y),
                            arrowprops=dict(arrowstyle="-|>", color="#2c3e50",
                                            lw=1 + 3.5 * (r["co2"] / mx if mx else 0),
                                            alpha=.85, shrinkA=7, shrinkB=7))
        ax.set_axis_off(); ax.set_title(str(int(y)), fontsize=12)
    sm = plt.cm.ScalarMappable(cmap="GnBu", norm=plt.Normalize(0, vmax))
    fig.colorbar(sm, ax=axes[0].tolist(), fraction=.03, pad=.02)
    fig.suptitle("Captured CO2 (colour), pipeline transport (arrows), "
                 "injection sites (purple ring)", fontsize=14, fontweight="bold")
    return fig


def fig_costs(obj):
    """Total system cost by component: the expensive ones only."""
    s = pd.Series(obj, dtype=float)
    s = s[s.abs() > 0].sort_values(ascending=False)
    if s.empty:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.text(.5, .5, "no cost data", ha="center"); ax.set_axis_off()
        return fig, s
    total = s.sum()
    keep = s[s / total >= 0.001]
    if len(keep) < len(s):
        keep = pd.concat([keep, pd.Series({"all other": s.sum() - keep.sum()})])
    fig, axes = plt.subplots(1, 2, figsize=(15, 6.2))
    cs = colors(len(keep))
    ax = axes[0]
    ax.barh(list(keep.index)[::-1], list(keep.values)[::-1], color=cs[::-1],
            edgecolor="white")
    ax.set_xlabel("cost (model units)")
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{v:,.0f}"))
    for i, v in enumerate(list(keep.values)[::-1]):
        ax.text(v, i, f"  {v:,.0f}  ({v / total * 100:.1f}%)", va="center",
                fontsize=9)
    ax.margins(x=.28); ax.grid(axis="y", visible=False)
    ax.set_title("Total cost by component")
    axes[1].pie(keep.values, labels=[f"{i}\n{v / total * 100:.1f}%"
                                     for i, v in keep.items()],
                colors=cs, startangle=90, counterclock=False,
                wedgeprops=dict(edgecolor="white", linewidth=1.4),
                textprops=dict(fontsize=9))
    axes[1].set_title(f"Share of total ({total:,.0f})")
    fig.suptitle("System cost composition", fontsize=14, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, .93))
    return fig, keep

# PP.classify() is written for the FLEET view, where `is_cc()` is tested before
# the gas-turbine test, so `CCGT+CC` lands in "industry: CCS-equipped" and
# `SMR+CC` is hidden there too. For a supply mix that is wrong: these are power
# and hydrogen plants. Reclassify on the energy side only.
def supply_category(tech, fallback):
    l = tech.lower()
    if "ccgt" in l or "ocgt" in l:
        return "gas CCS" if PP.is_cc(tech) else "gas unabated"
    if "smr" in l or "ref-" in l:
        return "SMR + CCS" if PP.is_cc(tech) else "SMR unabated"
    if "terminal" in l or "import" in l:
        return "imports / terminal"
    if l.startswith(("oil-", "coal-", "lignite")):
        return "oil / coal"
    if "nuclear" in l:
        return "nuclear"
    if l.startswith("ror") or "hydro" in l:
        return "hydro"
    if any(s in l for s in ("pem", "aec", "soec", "diaphragm")):
        return "electrolysis"
    return fallback


# --------------------------------------------- per-technology cost build-up
# The RESULTS db stores only model-wide objective terms (objective_*), so a
# cost-per-technology chart has to be reconstructed from the INPUT parameters
# multiplied by the solved variables. Everything below is validated against
# those objective totals before it is plotted - see cost_by_tech().
def _raw(val):
    idx = getattr(val, "indexes", None)
    if idx is None:
        try:
            return {"const": float(val)}
        except Exception:
            return {}
    return {int(str(i)[:4]): float(x) for i, x in zip(idx, val.values)
            if str(i)[:4].isdigit()}


def _pick(d, y):
    """Cost applying at milestone `y`.

    Cost series are keyed on the CALENDAR year of each milestone block
    (2030 / 2041 / 2050 / 2060); result variables are stamped 2030/2040/2050.
    For 2030 and 2050 the key matches exactly. For 2040 there is no key: the
    surrounding keys are 2030 and 2041, and the value SpineOpt actually used is
    their MIDPOINT. That is not assumed - taking the midpoint reproduces
    objective_unit_investment_costs to 3 parts in 1e8 (1,100,958.70 vs
    1,100,958.67), whereas picking either neighbour alone is off by -11.1% or
    +11.1% respectively.
    """
    if "const" in d:
        return d["const"]
    if y in d:
        return d[y]
    lo = [k for k in d if k < y]
    hi = [k for k in d if k > y]
    if lo and hi:
        return (d[max(lo)] + d[min(hi)]) / 2.0
    if lo:
        return d[max(lo)]
    return d[min(hi)] if hi else 0.0


def load_costs(modelpath, respath):
    """Per-unit investment + fixed-O&M cost, summed over all milestones."""
    from spinedb_api import DatabaseMapping as _DM
    inv, fom, cap = {}, {}, collections.defaultdict(float)
    with _DM("sqlite:///" + os.path.abspath(modelpath)) as db:
        for v in db.get_parameter_value_items():
            cls, p = v["entity_class_name"], v["parameter_definition_name"]
            val = from_database(v["value"], v["type"])
            if cls == "unit" and p == "unit_investment_cost":
                inv[v["entity_name"]] = _raw(val)
            elif cls == "unit" and p == "fom_cost":
                fom[v["entity_name"]] = _raw(val)
            elif cls == "unit__to_node" and p == "capacity_per_unit":
                m = _raw(val)
                cap[v["entity_byname"][0]] += list(m.values())[0] if m else 0.0
    res = collections.defaultdict(dict)
    with _DM("sqlite:///" + os.path.abspath(respath)) as db:
        for v in db.get_parameter_value_items():
            p = v["parameter_definition_name"]
            if p not in ("units_invested", "units_invested_available"):
                continue
            nm = (v["entity_name"].replace("default_report__", "")
                  .replace("__realization", ""))
            res[p][nm] = _raw(from_database(v["value"], v["type"]))

    # Fixed O&M is charged per hour of the milestone block, and each milestone
    # block carries weight 10 (it stands for a 10-year period).
    rows = []
    for nm, yr in res["units_invested"].items():
        if nm not in inv:
            continue
        for y, x in yr.items():
            if abs(x) > 1e-12:
                rows.append(dict(name=nm, year=y, kind="investment",
                                 cost=_pick(inv[nm], y) * x))
    for nm, yr in res["units_invested_available"].items():
        if nm not in fom:
            continue
        for y, x in yr.items():
            if abs(x) > 1e-12:
                rows.append(dict(name=nm, year=y, kind="fixed O&M",
                                 cost=_pick(fom[nm], y) * cap.get(nm, 0.0)
                                      * x * 8760 * 10))
    df = pd.DataFrame(rows)
    if len(df):
        df["tech"] = [PP.split_name(n)[0] for n in df["name"]]
    return df


def fig_cost_by_tech(costs, obj, n=18):
    """Cost contribution per technology (investment + fixed O&M)."""
    fig, axes = plt.subplots(1, 2, figsize=(16.5, 7.2))
    if costs.empty:
        for a in axes:
            a.text(.5, .5, "no cost data", ha="center"); a.set_axis_off()
        return fig, pd.DataFrame()
    piv = costs.pivot_table(index="tech", columns="kind", values="cost",
                            aggfunc="sum").fillna(0)
    piv["total"] = piv.sum(axis=1)
    piv = piv.sort_values("total", ascending=False)
    top = piv.head(n).drop(columns="total")
    rest = piv.iloc[n:]["total"].sum()
    grand = piv["total"].sum()

    ax = axes[0]
    labels = list(top.index)[::-1]
    bottom = np.zeros(len(top))
    cs = colors(len(top.columns))
    for k, c in enumerate(top.columns):
        v = top[c].values[::-1]
        ax.barh(labels, v, left=bottom, label=c, color=cs[k],
                edgecolor="white", linewidth=.5)
        bottom += v
    for i, v in enumerate(bottom):
        ax.text(v, i, f"  {v:,.0f} ({v / grand * 100:.1f}%)", va="center",
                fontsize=8)
    ax.set_xlabel("cost over all milestones (model units)")
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{v:,.0f}"))
    ax.margins(x=.3); ax.grid(axis="y", visible=False)
    ax.tick_params(axis="y", labelsize=8)
    ax.legend(fontsize=9)
    ax.set_title(f"Top {n} technologies by total cost")

    share = top.sum(axis=1)
    vals = list(share.values) + ([rest] if rest > 0 else [])
    labs = list(share.index) + (["all other technologies"] if rest > 0 else [])
    _lab = [l + chr(10) + f"{v / grand * 100:.1f}%" for l, v in zip(labs, vals)]
    axes[1].pie(vals, labels=_lab,
                colors=colors(len(vals)), startangle=90, counterclock=False,
                wedgeprops=dict(edgecolor="white", linewidth=1.2),
                textprops=dict(fontsize=7.5))
    axes[1].set_title(f"Share of unit cost ({grand:,.0f})")
    fig.suptitle("Cost contribution per technology "
                 "(investment + fixed O&M, all milestones)",
                 fontsize=14, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, .93))
    return fig, piv


def route_label(tech, fuel, cc):
    """Readable production-route name for the industry panels."""
    base = {"generic: reference route": "reference route",
            "generic: low-carbon route": "low-carbon route",
            "generic: EU average mix": "EU average mix",
            "other / unspecified": "other"}.get(fuel, fuel)
    return f"{base} + CC" if cc else base


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("db")
    ap.add_argument("-o", "--outdir", required=True)
    ap.add_argument("-m", "--model", default=None)
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    tag = os.path.splitext(os.path.basename(a.db))[0]

    wmap = PP.load_weights(a.model) if a.model else None
    if wmap:
        print(f"  weighting ON: {len(wmap)} modelled days")
    d = PP.load(a.db, wmap)
    supply, prod, emis = d["supply"], d["prod"], d["emis"]
    co2net, co2store, co2pipe = d["co2net"], d["co2store"], d["co2pipe"]
    obj = d["obj"]

    # Energy flows are in MWh-equivalent model units; show TWh.
    for df, col in ((supply, "energy"),):
        if len(df):
            df[col] = df[col] / 1e3

    if len(supply):
        supply["category"] = [supply_category(t, c) for t, c
                                in zip(supply["tech"], supply["category"])]

    if len(prod):
        prod["route"] = [route_label(t, f, c) for t, f, c
                         in zip(prod["tech"], prod["fuel"], prod["cc"])]

    years = [y for y in PP.MILESTONES
             if y in set(pd.concat([supply["year"], emis["year"]]).dropna())]
    print("  milestone years:", years)

    figs, csvs = [], {}

    f, t = fig_supply_mix(supply, "electricity", "Electricity supply mix")
    figs.append(("01_electricity_supply_mix", f)); csvs["electricity_supply_mix"] = t
    f, t = fig_supply_mix(supply, "hydrogen", "Hydrogen supply mix")
    figs.append(("02_hydrogen_supply_mix", f)); csvs["hydrogen_supply_mix"] = t

    if len(prod):
        secs = [s for s in PP.SECTOR_NODES.values()
                if s in set(prod["sector"]) and prod[prod.sector == s]["output"].sum() > 0]
        half = int(np.ceil(len(secs) / 2))
        for k, chunk in enumerate((secs[:half], secs[half:])):
            if not chunk:
                continue
            f, tabs = fig_industry_sector(
                prod, chunk, f"Industry decarbonisation - production route mix ({k + 1})")
            figs.append((f"0{3 + k}_industry_routes_{k + 1}", f))
            for s, tb in tabs.items():
                csvs["industry_" + re.sub(r"\W+", "_", s).strip("_")] = tb

    f, t = fig_co2_system(emis, co2net, co2store)
    figs.append(("05_co2_system", f)); csvs["co2_system"] = t

    gdf = PP.load_geo()
    if gdf is not None and years:
        figs.append(("06_co2_maps", fig_co2_maps(gdf, emis, co2net, co2store,
                                                 co2pipe, years)))
        figs.append(("07_co2_flows", fig_co2_flows(gdf, co2net, co2pipe,
                                                   co2store, years)))
    else:
        print("  (no geopandas / geojson -> skipping maps)")

    costs = load_costs(a.model, a.db) if a.model else pd.DataFrame()
    if len(costs):
        recon = costs.groupby("kind")["cost"].sum()
        print("  cost reconstruction check (recon vs objective):")
        for k, oname in (("investment", "unit_investment_costs"),
                         ("fixed O&M", "fixed_om_costs")):
            if k in recon and oname in obj:
                r = recon[k] / obj[oname]
                print(f"    {k:<12} {recon[k]:>14,.1f} vs {obj[oname]:>14,.1f}"
                      f"  ratio {r:.4f}")
                if abs(r - 1) > 0.02:
                    print(f"    WARNING: {k} reconstruction is off by "
                          f"{(r - 1) * 100:+.1f}% - do not trust that split")
    f, t = fig_cost_by_tech(costs, obj)
    figs.append(("08_cost_by_technology", f)); csvs["cost_by_technology"] = t
    f, t = fig_costs(obj)
    figs.append(("09_cost_by_component", f)); csvs["cost_by_component"] = t

    for name, fig in figs:
        p = os.path.join(a.outdir, f"{tag}_{name}.png")
        fig.savefig(p, bbox_inches="tight")
        print("  wrote", os.path.basename(p))
    pdf_path = os.path.join(a.outdir, f"{tag}_plots.pdf")
    with PdfPages(pdf_path) as pdf:
        for _, fig in figs:
            pdf.savefig(fig, bbox_inches="tight")
    for fig in [f for _, f in figs]:
        plt.close(fig)
    for name, tb in csvs.items():
        if tb is None or len(tb) == 0:
            continue
        tb.to_csv(os.path.join(a.outdir, f"{tag}_{name}.csv"))
    print(f"wrote {pdf_path} ({len(figs)} pages)")


if __name__ == "__main__":
    main()
