"""Presentation deck for an IC1 run.

Builds the slides plus a combined PDF. Defaults to the summer run databases in
the parent directory; point it at any other pair with --results/--input.

    python presentation\\build_deck.py
    python presentation\\build_deck.py --results ..\\RESULTS_x.sqlite --out out_3day \\
                                       --label "three representative days"
"""
from __future__ import annotations

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "analysis_v2"))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages

import model as M
import spine_io as sio
import slides_extra as E
import taxonomy as X
import theme as T

OUT = os.path.join(HERE, "out")
RESULTS_DB = os.path.join(ROOT, "RESULTS_Investment_Results.summer_co2rebuild.sqlite")
INPUT_DB = os.path.join(ROOT, "INPUT_Final_SpineOpt_Model.tiny.summer_co2rebuild.sqlite")

NOTE_TEMPLATE = ("IC1 industrial decarbonisation case \u00b7 SpineOpt 1.0 \u00b7 "
                 "Netherlands + Belgium, 17 regions \u00b7 {label}")
DEFAULT_LABEL = "annualised from a representative day (19 Aug \u00d7 365)"
NOTE = NOTE_TEMPLATE.format(label=DEFAULT_LABEL)

PDF_NAME = "IC1_summer_run_deck.pdf"
TITLE = "Where the summer run stands"
SOLVER_NOTE = "Gurobi 13.0 \u00b7 33 min"
TEMPORAL_NOTE = ("Three milestone years (2030, 2040, 2050), each represented by one "
                 "24-hour day \u2014 19 August \u2014 weighted \u00d7365 to an annual "
                 "total. Seasonal detail is not resolved, so solar is above and heating "
                 "below their annual means.")

PAGES = []


def _parse_args(argv=None):
    p = argparse.ArgumentParser(description="Build the IC1 presentation deck.")
    p.add_argument("--results", default=RESULTS_DB, help="results SQLite database")
    p.add_argument("--input", dest="input_db", default=INPUT_DB,
                   help="input SQLite database")
    p.add_argument("--out", default=OUT, help="output directory for slides and PDF")
    p.add_argument("--label", default=DEFAULT_LABEL,
                   help="temporal description shown in the source note")
    p.add_argument("--pdf", default=PDF_NAME, help="file name of the combined PDF")
    p.add_argument("--title", default=TITLE, help="cover-slide headline")
    p.add_argument("--solver-note", default=SOLVER_NOTE,
                   help="solver/runtime caption on the cover card")
    p.add_argument("--temporal-note", default=TEMPORAL_NOTE,
                   help="'Temporal resolution' paragraph on the method slide")
    return p.parse_args(argv)


def save(fig, name):
    # Page numbers follow the order slides are built in main(), so inserting a
    # new slide never requires renaming the ones after it.
    import re as _re
    stem = _re.sub(r"^P\d+_", "", name)
    path = os.path.join(OUT, f"P{len(PAGES) + 1:02d}_{stem}")
    fig.savefig(path, bbox_inches=None, facecolor=T.WHITE)
    PAGES.append(fig)
    print("  slide ->", os.path.relpath(path, ROOT))


# ==========================================================================
# data
# ==========================================================================
class Data:
    def __init__(self):
        self.r = sio.connect(RESULTS_DB)
        self.i = sio.connect(INPUT_DB)
        self.year_map, self.weight = M.temporal_structure(self.i)
        self.uf = M.unit_flows(self.r, self.year_map, self.weight)
        self.cf = M.connection_flows(self.r, self.year_map, self.weight)
        self.uf["carrier"] = self.uf["node"].astype(str).str.rsplit("_", n=1).str[0]
        self.uf["tech"] = self.uf["unit"].map(M.tech_of)
        self.uf["region"] = self.uf["unit"].map(M.region_of)
        self.periods = sorted(self.uf["period"].unique())
        self.cap, _ = M.co2_cap(self.i, self.weight, self.year_map)
        self.fleet = M.fleet(self.r, self.i)
        # generic sector stand-ins: capacity_per_unit is arbitrary, so they cannot be
        # ranked against real plant
        generic = self.fleet["tech"].str.contains(
            "production-reference|production-alternative", na=False)
        self.fleet = self.fleet[~(self.fleet["is_placeholder"] | generic)]

    def atm(self, direction="to_node"):
        a = self.uf[(self.uf["node"] == M.ATMOSPHERE) & (self.uf["direction"] == direction)]
        return a

    def net_co2(self):
        g = self.atm("to_node").groupby("period")["value_annual"].sum()
        r = self.atm("from_node").groupby("period")["value_annual"].sum()
        return (g - r.reindex(g.index).fillna(0.0)).reindex(self.periods)

    def gross_co2(self):
        return self.atm("to_node").groupby("period")["value_annual"].sum().reindex(self.periods)

    def stored_co2(self):
        return self.atm("from_node").groupby("period")["value_annual"].sum().reindex(
            self.periods).fillna(0.0)

    def emissions_by_group(self):
        a = self.atm("to_node").copy()
        a["group"] = a["tech"].map(X.emission_group)
        return (a.groupby(["group", "period"])["value_annual"].sum()
                .unstack("period").reindex(columns=self.periods).fillna(0.0))

    def capture_by_source(self):
        c = self.uf[(self.uf["carrier"] == "CO2") & (self.uf["direction"] == "to_node")].copy()
        c["group"] = c["tech"].map(X.capture_group)
        return c

    def capture_leaders(self, period, n=2):
        """Technologies sending the most CO2 to the network in `period`.

        Returns [(tech, value_annual), ...] sorted descending, so slide text can
        name the routes this particular run actually used instead of repeating a
        narrative written for an earlier scenario.
        """
        c = self.capture_by_source()
        c = c[(c["period"] == period) & (c["value_annual"] > 1e-9)]
        if c.empty:
            return []
        g = c.groupby("tech")["value_annual"].sum().sort_values(ascending=False)
        return [(str(t), float(v)) for t, v in g.head(n).items()]

    def injection(self):
        inj = self.uf[(self.uf["node"].astype(str).str.startswith("CO2-storage"))
                      & (self.uf["direction"] == "to_node")].copy()
        inj["reservoir"] = inj["node"].astype(str)
        return inj

    def product(self, prefix, period=None):
        p = self.uf[(self.uf["carrier"] == prefix) & (self.uf["direction"] == "to_node")]
        return p if period is None else p[p["period"] == period]

    def sector_table(self):
        """Output and CCS-equipped share for every industrial product."""
        ccs_units = set(self.uf[(self.uf["carrier"] == "CO2")
                                & (self.uf["direction"] == "to_node")
                                & (self.uf["value_annual"] > 1e-9)]["unit"])
        rows = []
        for prefix, label in X.SECTORS.items():
            p = self.uf[(self.uf["carrier"] == prefix) & (self.uf["direction"] == "to_node")]
            if p.empty:
                continue
            for period, g in p.groupby("period"):
                tot = g["value_annual"].sum()
                ccs = g[g["unit"].isin(ccs_units)]["value_annual"].sum()
                rows.append({"sector": label, "period": period, "output": tot,
                             "ccs_output": ccs, "ccs_share": ccs / tot if tot else 0.0})
        return pd.DataFrame(rows)

    def carrier_mix(self, carrier):
        s = self.uf[(self.uf["carrier"] == carrier) & (self.uf["direction"] == "to_node")].copy()
        s["group"] = s["tech"].map(X.supply_group)
        return (s.groupby(["group", "period"])["value_annual"].sum()
                .unstack("period").reindex(columns=self.periods).fillna(0.0))

    def unit_inputs(self):
        """(unit, period) -> {carrier: annual volume consumed}"""
        ins = self.uf[self.uf["direction"] == "from_node"]
        g = ins.groupby(["unit", "period", "carrier"])["value_annual"].sum()
        out = {}
        for (u, p, c), v in g.items():
            out.setdefault((u, p), {})[c] = v
        return out

    def ccs_units(self):
        return set(self.uf[(self.uf["carrier"] == "CO2")
                           & (self.uf["direction"] == "to_node")
                           & (self.uf["value_annual"] > 1e-9)]["unit"])

    def route_mix(self):
        """Industrial output split by how the route is powered and whether it captures."""
        inputs = self.unit_inputs()
        ccs = self.ccs_units()
        rows = []
        for prefix, label in X.SECTORS.items():
            p = self.uf[(self.uf["carrier"] == prefix) & (self.uf["direction"] == "to_node")]
            if p.empty:
                continue
            for (unit, period), g in p.groupby(["unit", "period"]):
                v = g["value_annual"].sum()
                if v <= 1e-9:
                    continue
                cat = X.route_category(inputs.get((unit, period), {}), unit in ccs)
                rows.append({"sector": label, "period": period, "unit": unit,
                             "tech": M.tech_of(unit), "route": cat, "output": v})
        return pd.DataFrame(rows)

    def capacity_split(self):
        evn = M.existing_vs_new(self.fleet, self.i)
        evn["cap_existing"] = evn["existing_retained"] * evn["capacity_per_unit"]
        evn["cap_new"] = evn["new_build"] * evn["capacity_per_unit"]
        return evn

    def regional(self):
        atm = self.atm("to_node").groupby(["region", "period"])["value_annual"].sum()
        cap = (self.uf[(self.uf["carrier"] == "CO2") & (self.uf["direction"] == "to_node")]
               .groupby(["region", "period"])["value_annual"].sum())
        inj = (self.uf[self.uf["node"].astype(str).str.startswith("CO2-storage")
                       & (self.uf["direction"] == "to_node")]
               .groupby(["region", "period"])["value_annual"].sum())
        df = pd.DataFrame({"emitted": atm, "captured": cap, "injected": inj}).fillna(0.0)
        return df.reset_index()

    def pipelines(self):
        cf = self.cf[self.cf["node"].astype(str).str.startswith("CO2_")
                     & (self.cf["direction"] == "to_node")].copy()
        cf["dest"] = cf["node"].astype(str).str.replace("CO2_", "", regex=False)
        cf["origin"] = [c.split("_CO2_")[0] for c in cf["connection"]]
        return cf.groupby(["origin", "dest", "period"])["value_annual"].sum().reset_index()

    def objective(self):
        rows = sio.scalars(self.r, ["total_costs"])
        return float(rows["value"].iloc[0]) if len(rows) else float("nan")


# ==========================================================================
# slides
# ==========================================================================
def slide_cover(d):
    fig = plt.figure(figsize=(13.33, 7.5))
    fig.text(0.045, 0.90, "INDUSTRIAL DECARBONISATION \u00b7 CASE IC1", fontsize=10,
             color=T.TEAL, fontweight="bold", va="top")
    fig.text(0.045, 0.845, TITLE, fontsize=34,
             color=T.INK, fontweight="bold", va="top")
    fig.text(0.045, 0.755,
             "Netherlands and Belgium, 17 industrial regions, three milestone years.\n"
             "Capacity-planning optimum under a declining CO\u2082 budget.",
             fontsize=13, color=T.SUB, va="top", linespacing=1.6)

    net = d.net_co2()
    stored = d.stored_co2()
    gross = d.gross_co2()
    last = d.periods[-1]
    first = d.periods[0]
    cards = [
        (f"{gross[first]/1000:,.0f}", f"Mt CO\u2082 emitted in {first}", "gross, all sources", T.CORAL),
        (f"{(1 - net[last]/net[first]):.0%}", f"cut in net CO\u2082 by {last}",
         f"{net[first]/1000:,.0f} \u2192 {max(net[last],0)/1000:,.0f} Mt", T.GREEN),
        (f"{stored[last]/1000:,.1f}", f"Mt CO\u2082 stored in {last}",
         f"from {stored[first]/1000:,.2f} Mt in {first}", T.BLUE),
    ]
    cards2 = [
        ("17", "regions modelled", "9 Dutch \u00b7 8 Belgian", T.TEAL),
        ("2", "offshore reservoirs", "NSNL031 \u00b7 NSNL012", T.VIOLET),
        ("OPTIMAL", "solver status", SOLVER_NOTE, T.SLATE),
    ]
    for i, (v, l, n, c) in enumerate(cards):
        T.card(fig, (0.045 + i * 0.315, 0.40, 0.28, 0.17), v, l, n, c)
    for i, (v, l, n, c) in enumerate(cards2):
        T.card(fig, (0.045 + i * 0.315, 0.19, 0.28, 0.17), v, l, n, c)

    T.source_note(fig, NOTE)
    save(fig, "P01_cover.png")


def slide_pathway(d):
    fig = plt.figure(figsize=(13.33, 7.5))
    T.headline(fig, "CO\u2082 trajectory",
               "The budget tightens to net zero by 2050",
               "Net CO\u2082 reaching the atmosphere after geological storage, "
               "against the budget set for each milestone year.")
    ax = fig.add_axes([0.075, 0.17, 0.52, 0.60])

    net = d.net_co2() / 1000.0
    gross = d.gross_co2() / 1000.0
    stored = d.stored_co2() / 1000.0
    caps = np.array([d.cap.get(p, d.cap.get(p + 1, np.nan)) for p in d.periods]) / 1000.0
    x = np.arange(len(d.periods))

    ax.bar(x, gross, 0.52, color=T.CORAL, alpha=0.18, edgecolor="none",
           label="gross emissions")
    ax.bar(x, net.values, 0.52, color=T.CORAL, edgecolor="none", label="net of storage")
    headroom = float(gross.max()) * 1.26
    for xi, (g, n, s) in enumerate(zip(gross, net.values, stored)):
        T.label_bar(ax, xi, g, f"{g:,.0f}", color=T.CORAL, fontsize=13, dy=4)
        if s > 0.5:
            ax.annotate(f"\u2212{s:,.0f} stored", (xi, (n + g) / 2), ha="center",
                        va="center", fontsize=9.5, color=T.CORAL)
    for xi, c in enumerate(caps):
        ax.plot([xi - 0.30, xi + 0.30], [c, c], color=T.INK, lw=2.2, zorder=5,
                solid_capstyle="butt")
        ax.annotate(f"budget {c:,.0f}", (xi + 0.32, c), ha="left", va="center",
                    fontsize=9, color=T.INK)
    ax.set_xticks(x)
    ax.set_xticklabels([str(p) for p in d.periods], fontsize=13, color=T.INK)
    ax.set_ylabel("Mt CO\u2082 per year")
    ax.set_ylim(0, headroom)
    T.strip_axes(ax)
    ax.legend(loc="upper right", fontsize=9.5, bbox_to_anchor=(1.0, 0.98))

    # right rail
    rx = 0.655
    fig.text(rx, 0.70, "What drives the curve", fontsize=13, color=T.INK,
             fontweight="bold", va="top")
    # Derived from this run's own results, not hardcoded. Each milestone bullet
    # reports gross emissions, the amount stored, and the technologies actually
    # doing the capturing in that period.
    bullets = []
    for color, period in zip((T.CORAL, T.AMBER, T.BLUE), d.periods):
        g = float(gross.loc[period]) if period in gross.index else 0.0
        s = float(stored.loc[period]) if period in stored.index else 0.0
        top = d.capture_leaders(period, n=2)
        if top:
            who = " and ".join(f"{t} ({v / 1000.0:,.0f} Mt)" for t, v in top)
            text = (f"Gross {g:,.0f} Mt, of which {s:,.0f} Mt is captured and stored. "
                    f"Largest contributors: {who}.")
        else:
            text = f"Gross {g:,.0f} Mt with {s:,.0f} Mt captured; no single dominant route."
        bullets.append((color, str(period), text))
    y = 0.615
    for color, year, text in bullets:
        fig.patches.append(plt.Rectangle((rx, y - 0.075), 0.0035, 0.085, color=color,
                                         transform=fig.transFigure, figure=fig))
        fig.text(rx + 0.018, y, year, fontsize=12, color=color, fontweight="bold",
                 va="top")
        fig.text(rx + 0.018, y - 0.038, _wrap(text, 46), fontsize=10.5, color=T.SUB,
                 va="top", linespacing=1.6)
        y -= 0.145

    T.source_note(fig, NOTE)
    save(fig, "P02_co2_pathway.png")


def slide_sources(d):
    fig = plt.figure(figsize=(13.33, 7.5))
    T.headline(fig, "Emission sources",
               "Gas supply and heavy industry dominate throughout",
               "Gross CO\u2082 released to the atmosphere, grouped by part of the system.")
    ax = fig.add_axes([0.075, 0.14, 0.50, 0.62])

    g = d.emissions_by_group() / 1000.0
    g = g.drop(index=[i for i in g.index if "stored" in i], errors="ignore")
    small = g.index[g.max(axis=1) < 0.5]
    if len(small) > 1:
        g.loc["Other"] = g.loc[small].sum() + g.loc["Other"] if "Other" in g.index \
            else g.loc[small].sum()
        g = g.drop(index=[s for s in small if s != "Other"])
    g = g.loc[g.sum(axis=1).sort_values(ascending=False).index]
    x = np.arange(len(d.periods))
    bottom = np.zeros(len(d.periods))
    for name in g.index:
        vals = g.loc[name].values
        ax.bar(x, vals, 0.5, bottom=bottom, color=X.EMISSION_COLOR.get(name, T.FAINT),
               edgecolor=T.WHITE, lw=1.0, label=name)
        bottom += vals
    for xi, v in enumerate(bottom):
        T.label_bar(ax, xi, v, f"{v:,.0f}", fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels([str(p) for p in d.periods], fontsize=13, color=T.INK)
    ax.set_ylabel("Mt CO\u2082 per year")
    ax.set_ylim(0, float(bottom.max()) * 1.16)
    T.strip_axes(ax)

    # direct-labelled legend with values
    rx = 0.635
    fig.text(rx, 0.735, "Mt CO\u2082 per year", fontsize=9, color=T.FAINT, va="top")
    fig.text(rx + 0.185, 0.735, "2030", fontsize=9, color=T.FAINT, va="top", ha="right")
    fig.text(rx + 0.255, 0.735, "2040", fontsize=9, color=T.FAINT, va="top", ha="right")
    fig.text(rx + 0.325, 0.735, "2050", fontsize=9, color=T.FAINT, va="top", ha="right")
    y = 0.695
    for name in g.index:
        c = X.EMISSION_COLOR.get(name, T.FAINT)
        fig.patches.append(plt.Rectangle((rx, y - 0.012), 0.012, 0.018, color=c,
                                         transform=fig.transFigure, figure=fig))
        fig.text(rx + 0.021, y, name, fontsize=10, color=T.INK, va="center")
        for j, p in enumerate(d.periods):
            v = g.loc[name, p]
            fig.text(rx + 0.185 + j * 0.070, y, f"{v:,.1f}" if v else "\u2013",
                     fontsize=10, color=T.INK if v else T.FAINT, va="center", ha="right")
        y -= 0.052

    T.source_note(fig, NOTE)
    save(fig, "P03_emission_sources.png")


def slide_ccs_chain(d):
    period = d.periods[-1]
    fig = plt.figure(figsize=(13.33, 7.5))
    stored = d.stored_co2()[period] / 1000.0
    T.headline(fig, f"Carbon capture and storage \u00b7 {period}",
               f"{stored:,.0f} Mt a year routed from capture to the North Sea",
               "Every tonne entering the CO\u2082 network is injected into the NSNL031 "
               "and NSNL012 reservoirs; none is vented or used for products.")
    ax = fig.add_axes([0.06, 0.06, 0.88, 0.63])

    cap = d.capture_by_source()
    cap = cap[(cap["period"] == period) & (cap["value_annual"] > 1e-6)].copy()
    total = cap["value_annual"].sum() / 1000.0
    by_src = cap.groupby("group")["value_annual"].sum().sort_values(ascending=False) / 1000.0

    hub_tot = cap.groupby("region")["value_annual"].sum() / 1000.0
    major = hub_tot[hub_tot >= 0.02 * total].sort_values(ascending=False)
    minor = hub_tot[hub_tot < 0.02 * total]
    OTHER_HUB = f"{len(minor)} smaller hubs"
    cap["hub"] = cap["region"].map(
        lambda r: f"{r} hub" if r in major.index else OTHER_HUB)

    STORE = "North Sea storage"
    links = []
    for (grp, hub), v in cap.groupby(["group", "hub"])["value_annual"].sum().items():
        if v > 1e-6:
            links.append((grp, hub, v / 1000.0))
    for hub, v in cap.groupby("hub")["value_annual"].sum().items():
        links.append((hub, STORE, v / 1000.0))

    hub_order = [f"{r} hub" for r in major.index] + ([OTHER_HUB] if len(minor) else [])
    cols = [list(by_src.index), hub_order, [STORE]]
    colors = {n: X.CAPTURE_COLOR.get(n, T.SLATE) for n in by_src.index}
    colors.update({h: T.SLATE for h in hub_order})
    colors[STORE] = T.INK
    link_colors = {(s, t): X.CAPTURE_COLOR.get(s, T.SLATE) for s, t, _ in links}

    T.sankey(ax, links, cols, node_colors=colors, link_colors=link_colors,
             value_fmt="{v:,.1f} Mt", fontsize=10, gap_frac=0.07)

    for xf, label in ((0.0, "CAPTURED AT"), (0.5, "REGIONAL CO\u2082 HUB"),
                      (1.0, "INJECTED INTO")):
        ax.text(xf, 1.075, "  ".join(label), fontsize=8.5, color=T.FAINT, ha="center",
                fontweight="bold")

    T.source_note(fig, NOTE)
    save(fig, "P04_ccs_chain.png")


def slide_industry(d):
    fig = plt.figure(figsize=(13.33, 7.5))
    T.headline(fig, "Carbon capture",
               "Capture lands on chemicals and cement, not on steel",
               "Share of each sector's output coming from a route fitted with carbon "
               "capture. Feedstock switching, shown on the previous slide, carries the "
               "rest of the abatement.")
    st = d.sector_table()
    first, last = d.periods[0], d.periods[-1]
    piv = st.pivot_table(index="sector", columns="period", values="ccs_share").fillna(0.0)
    out = st[st["period"] == last].set_index("sector")["output"]
    piv = piv.loc[[s for s in piv.index if s in X.HEAVY_INDUSTRY or piv.loc[s].max() > 0]]
    piv = piv.sort_values(last)

    ax = fig.add_axes([0.26, 0.14, 0.44, 0.62])
    y = np.arange(len(piv))
    for i, s in enumerate(piv.index):
        a, b = piv.loc[s, first] * 100, piv.loc[s, last] * 100
        ax.plot([a, b], [i, i], color=T.RULE, lw=3, solid_capstyle="round", zorder=1)
        ax.scatter([a], [i], s=70, color=T.WHITE, edgecolor=T.SLATE, lw=1.8, zorder=2)
        ax.scatter([b], [i], s=90, color=T.TEAL if b > 0 else T.FAINT, zorder=3,
                   edgecolor="none")
        if b > 0.3:
            ax.annotate(f"{b:.0f}%", (b, i), xytext=(9, 0), textcoords="offset points",
                        va="center", fontsize=10, color=T.TEAL, fontweight="bold")
        else:
            ax.annotate("no capture", (0, i), xytext=(9, 0), textcoords="offset points",
                        va="center", fontsize=9, color=T.FAINT)
    ax.set_yticks(y)
    ax.set_yticklabels(piv.index, fontsize=10.5, color=T.INK)
    ax.set_xlabel("share of sector output from a CCS-equipped route (%)")
    ax.set_xlim(-1, max(float(piv.max().max()) * 100 * 1.35, 12))
    T.strip_axes(ax)
    ax.grid(axis="y", visible=False)
    ax.scatter([], [], s=70, color=T.WHITE, edgecolor=T.SLATE, lw=1.8, label=str(first))
    ax.scatter([], [], s=90, color=T.TEAL, label=str(last))
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.09), ncol=2, fontsize=10)

    ax2 = fig.add_axes([0.745, 0.14, 0.195, 0.62], sharey=ax)
    sizes = [out.get(s, 0.0) / 1000.0 for s in piv.index]
    ax2.barh(y, sizes, 0.55, color=T.PANEL, edgecolor=T.RULE)
    for i, v in enumerate(sizes):
        ax2.annotate(f"{v:,.1f}", (v, i), xytext=(5, 0), textcoords="offset points",
                     va="center", fontsize=9, color=T.SUB)
    ax2.tick_params(labelleft=False, length=0)
    ax2.set_xlabel("output, Mt or TWh\nper year (2050)")
    ax2.set_xlim(0, max(sizes) * 1.45)
    T.strip_axes(ax2)
    ax2.grid(visible=False)

    T.source_note(fig, NOTE)
    save(fig, "P06_industry_capture.png")


def slide_carriers(d):
    fig = plt.figure(figsize=(13.33, 7.5))
    T.headline(fig, "Energy supply",
               "Bioenergy becomes the backbone of the system",
               "Share of annual production by source. Hydrogen appears at scale from "
               "2040, entirely through the liquid-hydrogen import terminal.")
    specs = [("elec", "Electricity"), ("CH4", "Methane"), ("H2", "Hydrogen")]
    for k, (carrier, label) in enumerate(specs):
        ax = fig.add_axes([0.075 + k * 0.305, 0.145, 0.215, 0.53])
        mix = d.carrier_mix(carrier)
        mix = mix.loc[mix.sum(axis=1).sort_values(ascending=False).index]
        tot = mix.sum(axis=0)
        shares = mix / tot.replace(0, np.nan) * 100
        x = np.arange(len(d.periods))
        bottom = np.zeros(len(d.periods))
        for name in mix.index:
            v = shares.loc[name].fillna(0.0).values
            ax.bar(x, v, 0.54, bottom=bottom, color=X.SUPPLY_COLOR.get(name, T.FAINT),
                   edgecolor=T.WHITE, lw=0.9)
            for xi in x:
                if v[xi] >= 11:
                    ax.text(xi, bottom[xi] + v[xi] / 2, name.replace(" ", "\n"),
                            ha="center", va="center", fontsize=7.6, color=T.WHITE,
                            fontweight="bold", linespacing=1.3)
            bottom += v
        ax.set_xticks(x)
        ax.set_xticklabels([str(p) for p in d.periods], fontsize=11, color=T.INK)
        ax.set_ylim(0, 100)
        ax.set_yticks([0, 25, 50, 75, 100])
        ax.set_yticklabels(["0", "25", "50", "75", "100%"] if k == 0 else [])
        ax.set_title(label, fontsize=13, fontweight="bold", loc="left", pad=26)
        for xi, p in enumerate(d.periods):
            ax.annotate(f"{tot[p]/1000:,.0f}", (xi, 100), xytext=(0, 7),
                        textcoords="offset points", ha="center", fontsize=9.5,
                        color=T.SUB)
        T.strip_axes(ax)
    fig.text(0.075, 0.762, "figures above each bar are total annual production, TWh",
             fontsize=9, color=T.FAINT)
    T.source_note(fig, NOTE)
    save(fig, "P07_energy_carriers.png")


def slide_buildout(d):
    first, last = d.periods[0], d.periods[-1]
    fig = plt.figure(figsize=(13.33, 7.5))
    T.headline(fig, "Capacity build-out",
               f"What the fleet gains and loses between {first} and {last}",
               f"Change in available capacity between {first} and {last}. Each row is "
               "measured in its own technology's units, so compare rows by direction "
               "and relative size, not absolute value.")
    f = d.fleet.copy()
    active = set(d.uf.loc[d.uf["value_annual"] > 1e-6, "tech"])
    f = f[f["tech"].isin(active)]
    piv = (f.pivot_table(index="tech", columns="period", values="capacity_available",
                         aggfunc="sum").fillna(0.0)
           .reindex(columns=d.periods, fill_value=0.0))
    chg = (piv[last] - piv[first]).sort_values()
    chg = pd.concat([chg[chg < -1e-6].head(8), chg[chg > 1e-6].tail(8)]).sort_values()
    if chg.empty:
        return

    ax = fig.add_axes([0.325, 0.13, 0.595, 0.60])
    y = np.arange(len(chg))
    colors = [T.CORAL if v < 0 else T.GREEN for v in chg.values]
    ax.barh(y, chg.values, 0.62, color=colors, edgecolor="none")
    span = float(np.abs(chg.values).max())
    for i, v in enumerate(chg.values):
        ax.annotate(f"{v:+,.1f}", (v, y[i]), xytext=(7 if v > 0 else -7, 0),
                    textcoords="offset points", va="center",
                    ha="left" if v > 0 else "right", fontsize=9.5,
                    color=T.GREEN if v > 0 else T.CORAL, fontweight="bold")
    ax.axvline(0, color=T.INK, lw=1.1)
    ax.set_yticks(y)
    ax.set_yticklabels([t if len(t) <= 22 else t[:20] + "\u2026" for t in chg.index],
                       fontsize=10.5, color=T.INK)
    ax.set_xlim(-span * 1.30, span * 1.30)
    ax.set_xticks([])
    ax.set_xlabel(f"capacity retired  \u2190     {first} \u2192 {last}     \u2192  capacity added")
    T.strip_axes(ax)
    ax.grid(visible=False)

    fig.text(0.045, 0.66, "ADDED", fontsize=10, color=T.GREEN, fontweight="bold")
    # Named from this run's own ranking rather than a fixed narrative.
    added = [t for t, v in chg.sort_values(ascending=False).items() if v > 1e-6][:3]
    retired = [t for t, v in chg.sort_values().items() if v < -1e-6][:3]
    added_txt = (", ".join(added[:-1]) + " and " + added[-1]) if len(added) > 1 else (
        added[0] if added else "nothing")
    retired_txt = (", ".join(retired[:-1]) + " and " + retired[-1]) if len(retired) > 1 else (
        retired[0] if retired else "nothing")
    fig.text(0.045, 0.625, _wrap(f"Largest additions between {first} and {last}: "
                                 f"{added_txt}.", 26),
             fontsize=10, color=T.SUB, va="top", linespacing=1.6)
    fig.text(0.045, 0.42, "RETIRED", fontsize=10, color=T.CORAL, fontweight="bold")
    fig.text(0.045, 0.385, _wrap(f"Largest reductions: {retired_txt}.", 26),
             fontsize=10, color=T.SUB, va="top", linespacing=1.6)

    T.source_note(fig, NOTE)
    save(fig, "P08_capacity_change.png")


def slide_routes(d):
    first, last = d.periods[0], d.periods[-1]
    rm = d.route_mix()
    piv = (rm.pivot_table(index=["sector", "period"], columns="route", values="output",
                          aggfunc="sum").fillna(0.0))
    piv = piv.reindex(columns=[c for c in X.ROUTE_ORDER if c in piv.columns], fill_value=0.0)
    totals = piv.sum(axis=1)
    share = piv.div(totals, axis=0) * 100

    size = rm[rm["period"] == last].groupby("sector")["output"].sum()
    changed = []
    for s in size.sort_values(ascending=False).index:
        if (s, first) in share.index and (s, last) in share.index:
            moved = float(np.abs(share.loc[(s, last)] - share.loc[(s, first)]).sum())
            changed.append((s, moved, size[s]))
    sectors = [s for s, _, _ in sorted(changed, key=lambda r: (-r[1], -r[2]))[:10]]
    sectors = sorted(sectors, key=lambda s: -size[s])

    fig = plt.figure(figsize=(13.33, 7.5))
    n_moved = sum(1 for s, m, _ in changed if m > 1)
    T.headline(fig, "Process routes",
               f"{n_moved} of {len(changed)} sectors change how they make their product",
               "Share of each sector's output by route, 2030 (upper bar) and 2050 "
               "(lower bar). Capture is only part of the story \u2014 most of the shift "
               "is a switch of feedstock.")

    ax = fig.add_axes([0.21, 0.13, 0.55, 0.62])
    ypos, ylabels = [], []
    for i, s in enumerate(sectors):
        base = len(sectors) - i
        for j, p in enumerate((first, last)):
            y = base - j * 0.34
            ypos.append(y)
            ylabels.append(str(p))
            left = 0.0
            if (s, p) not in share.index:
                continue
            for route in share.columns:
                v = float(share.loc[(s, p), route])
                if v <= 1e-6:
                    continue
                ax.barh(y, v, 0.30, left=left, color=X.ROUTE_COLOR[route],
                        edgecolor=T.WHITE, lw=0.8)
                if v >= 16:
                    ax.text(left + v / 2, y, f"{v:.0f}%", ha="center", va="center",
                            fontsize=8, color=T.WHITE, fontweight="bold")
                left += v
    ax.set_yticks(ypos)
    ax.set_yticklabels(ylabels, fontsize=8, color=T.FAINT)
    for i, s in enumerate(sectors):
        ax.text(-11, len(sectors) - i - 0.17, s, ha="right", va="center",
                fontsize=10.5, color=T.INK)
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xticklabels(["0", "25", "50", "75", "100%"])
    ax.set_ylim(0.3, len(sectors) + 0.7)
    T.strip_axes(ax)
    ax.grid(axis="y", visible=False)

    rx = 0.80
    fig.text(rx, 0.735, "ROUTE", fontsize=8.5, color=T.FAINT, fontweight="bold", va="top")
    y = 0.695
    for route in X.ROUTE_ORDER:
        if route not in share.columns:
            continue
        fig.patches.append(plt.Rectangle((rx, y - 0.011), 0.013, 0.019,
                                         color=X.ROUTE_COLOR[route],
                                         transform=fig.transFigure, figure=fig))
        fig.text(rx + 0.022, y, route, fontsize=10, color=T.INK, va="center")
        y -= 0.047
    # Describe the sectors that actually moved in this run, rather than asserting
    # a fixed list of sectors that stay on their 2030 route.
    first_p, last_p = d.periods[0], d.periods[-1]
    moved, static = [], []
    for s in sectors:
        if (s, first_p) not in share.index or (s, last_p) not in share.index:
            continue
        delta = (share.loc[(s, last_p)] - share.loc[(s, first_p)]).abs().sum() / 2.0
        (moved if delta >= 5.0 else static).append((s, delta))
    moved.sort(key=lambda t: -t[1])
    if moved:
        names = ", ".join(s for s, _ in moved[:3])
        body = (f"{len(moved)} of {len(sectors)} sectors change route between "
                f"{first_p} and {last_p}; the largest shifts are {names}.")
    else:
        body = (f"No sector changes its process route between {first_p} and {last_p}.")
    if static:
        body += f" {len(static)} stay on their {first_p} route."
    fig.text(rx, y - 0.02, _wrap(body, 26),
             fontsize=9.5, color=T.SUB, va="top", linespacing=1.6)

    T.source_note(fig, NOTE)
    save(fig, "P05_industry_routes.png")


def slide_capacity_vintage(d):
    last = d.periods[-1]
    cs = d.capacity_split()
    active = set(d.uf.loc[d.uf["value_annual"] > 1e-6, "tech"])
    cs = cs[(cs["period"] == last) & (cs["tech"].isin(active))]
    g = cs.groupby("tech")[["cap_existing", "cap_new"]].sum()
    g = g[g.sum(axis=1) > 1e-6]
    g = g.loc[g.sum(axis=1).sort_values(ascending=False).head(14).index].iloc[::-1]
    new_share = g["cap_new"].sum() / g.sum().sum()

    fig = plt.figure(figsize=(13.33, 7.5))
    T.headline(fig, "Capacity vintage",
               "The legacy refinery and import fleet stays; the new build is capture",
               f"Available capacity in {last}, split between plant that already existed "
               f"in {d.periods[0]} and plant the model invests in. "
               f"{new_share:.0%} of the {last} fleet is new.")
    ax = fig.add_axes([0.235, 0.13, 0.62, 0.61])
    y = np.arange(len(g))
    ax.barh(y, g["cap_existing"].values, 0.6, color=T.SLATE, alpha=0.45,
            edgecolor="none", label=f"existing in {d.periods[0]}")
    ax.barh(y, g["cap_new"].values, 0.6, left=g["cap_existing"].values,
            color=T.TEAL, edgecolor="none", label="newly built")
    for i in range(len(g)):
        tot = g["cap_existing"].iloc[i] + g["cap_new"].iloc[i]
        nw = g["cap_new"].iloc[i]
        txt = f"{tot:,.1f}" + (f"   ({nw/tot:.0%} new)" if nw > 1e-6 else "")
        ax.annotate(txt, (tot, y[i]), xytext=(7, 0), textcoords="offset points",
                    va="center", fontsize=9, color=T.SUB)
    ax.set_yticks(y)
    ax.set_yticklabels(g.index, fontsize=10.5, color=T.INK)
    ax.set_xlim(0, float(g.sum(axis=1).max()) * 1.30)
    ax.set_xlabel("available capacity (each technology in its own units)")
    T.strip_axes(ax)
    ax.grid(axis="y", visible=False)
    ax.legend(loc="lower right", fontsize=10)
    T.source_note(fig, NOTE)
    save(fig, "P09_capacity_vintage.png")


def slide_map(d):
    last = d.periods[-1]
    reg = d.regional()
    reg = reg[reg["period"] == last].set_index("region")
    pipes = d.pipelines()
    pipes = pipes[(pipes["period"] == last) & (pipes["value_annual"] > 1e-6)]

    fig = plt.figure(figsize=(13.33, 7.5))
    T.headline(fig, "Regional picture",
               "Every tonne captured is Dutch; Belgium emits without abating",
               f"Industrial regions in {last}. Circle area is CO\u2082 emitted, the inner "
               "ring is CO\u2082 captured, arrows are pipeline flows to the North Sea.")
    ax = fig.add_axes([0.045, 0.06, 0.60, 0.70])
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(0.02, 1.04)
    ax.set_axis_off()

    ax.add_patch(plt.Rectangle((-0.02, 0.56), 1.04, 0.48, facecolor="#eef3f6",
                               edgecolor="none", zorder=0))
    ax.add_patch(plt.Rectangle((-0.02, 0.17), 1.04, 0.36, facecolor="#f6f2ee",
                               edgecolor="none", zorder=0))
    ax.text(1.0, 1.0, "NETHERLANDS", fontsize=9, color=T.FAINT, ha="right",
            fontweight="bold", zorder=1)
    ax.text(1.0, 0.195, "BELGIUM", fontsize=9, color=T.FAINT, ha="right",
            fontweight="bold", zorder=1)

    emax = float(reg["emitted"].max())
    cmax = float(reg["captured"].max())
    for r, (x, y) in X.REGION_XY.items():
        e = float(reg["emitted"].get(r, 0.0))
        c = float(reg["captured"].get(r, 0.0))
        s = 90 + 1500 * (e / emax)
        ax.scatter([x], [y], s=s, color=T.CORAL, alpha=0.30, edgecolor="none", zorder=2)
        if c > 1e-6:
            ax.scatter([x], [y], s=90 + 1500 * (c / cmax), facecolor="none",
                       edgecolor=T.TEAL, lw=2.4, zorder=4)
        ax.text(x, y - 0.055, r, fontsize=8.5, color=T.INK, ha="center", va="top",
                zorder=5)

    for sx, (name, (x, y)) in enumerate(X.STORAGE_XY.items()):
        ax.scatter([x], [y], marker="s", s=130, color=T.INK, zorder=4)
        ax.text(x + 0.025, y, name.replace("CO2-storage-", ""), fontsize=8.5,
                color=T.INK, ha="left", va="center", zorder=5)

    pmax = float(pipes["value_annual"].max()) if len(pipes) else 1.0
    for row in pipes.itertuples():
        if row.origin not in X.REGION_XY or row.dest not in X.REGION_XY:
            continue
        x0, y0 = X.REGION_XY[row.origin]
        x1, y1 = X.REGION_XY[row.dest]
        ax.annotate("", (x1, y1), (x0, y0), zorder=3,
                    arrowprops=dict(arrowstyle="-|>", color=T.VIOLET,
                                    lw=1.0 + 3.5 * row.value_annual / pmax,
                                    alpha=0.75, shrinkA=14, shrinkB=14,
                                    connectionstyle="arc3,rad=0.16"))
    inj_region = reg["injected"].idxmax() if reg["injected"].max() > 0 else "NLC5"
    for src in (inj_region, "NLC6"):
        if src not in X.REGION_XY:
            continue
        ax.annotate("", X.STORAGE_XY["CO2-storage-NSNL031"], X.REGION_XY[src], zorder=2,
                    arrowprops=dict(arrowstyle="-|>", color=T.TEAL, lw=3.4, alpha=0.6,
                                    shrinkA=16, shrinkB=12,
                                    connectionstyle="arc3,rad=0.22"))
    ax.text(0.30, 0.655, "injection offshore", fontsize=8.5, color=T.TEAL, zorder=5)

    # size key
    for i, frac in enumerate((1.0, 0.5, 0.1)):
        ax.scatter([0.06 + i * 0.075], [0.10], s=90 + 1500 * frac, color=T.CORAL,
                   alpha=0.30, edgecolor="none", zorder=2)
        ax.text(0.06 + i * 0.075, 0.045, f"{emax*frac/1000:,.0f}", fontsize=7.5,
                color=T.SUB, ha="center", zorder=5)
    ax.text(0.245, 0.10, "Mt CO\u2082 emitted", fontsize=8.5, color=T.FAINT,
            va="center", zorder=5)
    ax.scatter([0.46], [0.10], s=400, facecolor="none", edgecolor=T.TEAL, lw=2.2,
               zorder=4)
    ax.text(0.50, 0.10, "ring = CO\u2082 captured", fontsize=8.5, color=T.FAINT,
            va="center", zorder=5)

    rx = 0.685
    nl = reg.loc[[r for r in reg.index if r.startswith("NL")]]
    be = reg.loc[[r for r in reg.index if r.startswith("BE")]]
    T.card(fig, (rx, 0.555, 0.265, 0.115), f"{nl['emitted'].sum()/1000:,.0f} Mt",
           "emitted by Dutch regions", f"{nl['captured'].sum()/1000:,.0f} Mt captured",
           T.TEAL)
    T.card(fig, (rx, 0.415, 0.265, 0.115), f"{be['emitted'].sum()/1000:,.0f} Mt",
           "emitted by Belgian regions", "no capture anywhere in Belgium", T.CORAL)
    T.card(fig, (rx, 0.275, 0.265, 0.115),
           f"{pipes['value_annual'].sum()/1000:,.0f} Mt", "moved by CO\u2082 pipeline",
           f"{len(pipes)} links in use of 6 built", T.VIOLET)
    fig.text(rx, 0.215, _wrap("Schematic layout \u2014 the databases carry no coordinates. "
                              "Positions are editable in taxonomy.REGION_XY.", 46),
             fontsize=8.5, color=T.FAINT, va="top", linespacing=1.5)

    T.source_note(fig, NOTE)
    save(fig, "P10_regional_map.png")


def slide_region_table(d):
    first, last = d.periods[0], d.periods[-1]
    reg = d.regional()
    e = reg.pivot_table(index="region", columns="period", values="emitted").fillna(0.0) / 1000
    c = reg.pivot_table(index="region", columns="period", values="captured").fillna(0.0) / 1000
    order = e[last].sort_values().index

    fig = plt.figure(figsize=(13.33, 7.5))
    # Count how many regions it actually takes to reach two thirds of the
    # remaining emissions in this run, rather than asserting "four".
    _tail = e[last].sort_values(ascending=False)
    _total = float(_tail.sum())
    _n = 0
    if _total > 1e-9:
        _run = 0.0
        for _v in _tail:
            _run += float(_v)
            _n += 1
            if _run / _total >= 2.0 / 3.0:
                break
    _sub = (f"{_n} regions carry two thirds of what is left in {last}"
            if _n else f"No emissions remain in {last}")
    T.headline(fig, "Regions ranked", _sub,
               f"Emissions in {first} and {last} for each industrial region, with the "
               f"CO\u2082 captured there in {last}.")

    ax = fig.add_axes([0.11, 0.13, 0.40, 0.62])
    y = np.arange(len(order))
    for i, r in enumerate(order):
        a, b = e.loc[r, first], e.loc[r, last]
        ax.plot([b, a], [i, i], color=T.RULE, lw=3, solid_capstyle="round", zorder=1)
        ax.scatter([a], [i], s=62, color=T.WHITE, edgecolor=T.SLATE, lw=1.7, zorder=2)
        ax.scatter([b], [i], s=84, color=T.CORAL, zorder=3, edgecolor="none")
        ax.annotate(f"{b:,.1f}", (b, i), xytext=(8, 0), textcoords="offset points",
                    va="center", fontsize=9, color=T.CORAL, fontweight="bold")
    ax.set_yticks(y)
    ax.set_yticklabels([f"{r}   {r[:2]}" for r in order], fontsize=10, color=T.INK)
    ax.set_xlabel("Mt CO\u2082 emitted per year")
    ax.set_xlim(0, float(e.max().max()) * 1.22)
    ax.scatter([], [], s=62, color=T.WHITE, edgecolor=T.SLATE, lw=1.7, label=str(first))
    ax.scatter([], [], s=84, color=T.CORAL, label=str(last))
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.07), ncol=2, fontsize=10)
    T.strip_axes(ax)
    ax.grid(axis="y", visible=False)

    ax2 = fig.add_axes([0.565, 0.13, 0.25, 0.62])
    vals = [c.loc[r, last] for r in order]
    ax2.barh(y, vals, 0.6, color=T.TEAL, edgecolor="none")
    for i, v in enumerate(vals):
        if v > 1e-6:
            ax2.annotate(f"{v:,.1f}", (v, i), xytext=(6, 0), textcoords="offset points",
                         va="center", fontsize=9, color=T.TEAL, fontweight="bold")
    ax2.tick_params(labelleft=False, length=0)
    ax2.set_ylim(ax.get_ylim())
    ax2.set_xlabel(f"Mt CO\u2082 captured in {last}")
    ax2.set_xlim(0, max(vals) * 1.30)
    T.strip_axes(ax2)
    ax2.grid(axis="y", visible=False)

    rx = 0.845
    fig.text(rx, 0.70, "Read across", fontsize=12, color=T.INK, fontweight="bold",
             va="top")
    # Derived per run: which regions lead on emissions, which on capture, and
    # which emit without capturing. Naming regions in fixed text goes stale as
    # soon as the scenario changes.
    emit_last = e[last].sort_values(ascending=False)
    cap_last = c[last].reindex(emit_last.index).fillna(0.0)
    top_emit = [str(r) for r in emit_last.head(2).index]
    top_cap = [str(r) for r in cap_last.sort_values(ascending=False).head(2).index]
    both = [r for r in top_emit if r in top_cap]
    no_cap = [str(r) for r in emit_last.head(6).index if float(cap_last.get(r, 0.0)) <= 1e-6]

    if both:
        line1 = (f"{' and '.join(both)} {'are' if len(both) > 1 else 'is'} both a top "
                 f"emitter and a top capture site in {last}.")
    else:
        line1 = (f"The largest emitters in {last} ({', '.join(top_emit)}) are not the "
                 f"main capture sites ({', '.join(top_cap)}).")
    fig.text(rx, 0.655, _wrap(line1, 24),
             fontsize=10, color=T.SUB, va="top", linespacing=1.6)

    lead_cap = cap_last.sort_values(ascending=False)
    if not lead_cap.empty and float(lead_cap.iloc[0]) > 1e-6:
        lr = str(lead_cap.index[0])
        line2 = (f"{lr} captures {float(lead_cap.iloc[0]):,.1f} Mt, the largest of any "
                 f"region, against {float(emit_last.get(lr, 0.0)):,.1f} Mt emitted.")
    else:
        line2 = f"No region records CO2 capture in {last}."
    fig.text(rx, 0.47, _wrap(line2, 24),
             fontsize=10, color=T.SUB, va="top", linespacing=1.6)

    if no_cap:
        line3 = (f"{', '.join(no_cap[:3])} remain emitters with no capture taken up.")
    else:
        line3 = "Every leading emitter has some capture in place."
    fig.text(rx, 0.32, _wrap(line3, 24),
             fontsize=10, color=T.SUB, va="top", linespacing=1.6)

    T.source_note(fig, NOTE)
    save(fig, "P11_regions_ranked.png")


def slide_notes(d):
    fig = plt.figure(figsize=(13.33, 7.5))
    T.headline(fig, "Scope and method",
               "How to read these numbers",
               "Conventions used in this run, and the items still open before the "
               "results are final.")
    caps = []
    for p in d.periods:
        v = d.cap.get(p, d.cap.get(p + 1))
        caps.append(f"{v/1000:,.0f} Mt in {p}" if v is not None and v > 0.5
                    else f"zero in {p}")
    left = [
        ("Temporal resolution", TEMPORAL_NOTE),
        ("CO\u2082 budget",
         "A declining cap on the atmosphere node: " + ", ".join(caps) +
         ". The cap binds in every period, so the emission path is an "
         "input to the run rather than an outcome of it."),
        ("Costs",
         "Fixed O&M is 83% of the objective; fuel is priced through commodity taxes "
         "rather than a fuel-cost term, and there is no explicit CO\u2082 price."),
    ]
    # The fleet-turnover caveat describes the unmodified model. When a run forces
    # retirement, state what that run actually did instead.
    _steel = d.uf[(d.uf["carrier"] == "steel-primary") & (d.uf["direction"] == "to_node")]
    _last = d.periods[-1]
    _bf = float(_steel[(_steel["period"] == _last)
                       & (_steel["tech"] == "BF-BOF")]["value_annual"].sum())
    _tot = float(_steel[_steel["period"] == _last]["value_annual"].sum())
    _frozen = _tot > 1e-9 and _bf / _tot > 0.99
    if _frozen:
        fleet_note = (
            "Incumbent plant endowed through `units_existing` is never forced to "
            "retire: lifetime is an upper bound, not a mandate, and no commissioning "
            "vintage is given. Primary steel therefore stays 100% coal BF-BOF in "
            "every year even though DRI-EAF is cheaper to build. 57% of IC1 "
            "endowments are affected.")
        next_note = (
            "Settle on a single emission-accounting convention, fix the retirement "
            "logic above, and introduce a CO\u2082 price so abatement is driven "
            "by economics as well as by the cap.")
    else:
        fleet_note = (
            "This run overrides the default fleet behaviour: selected endowed units "
            "have a declining `investment_count_max_cumulative` forcing capacity to "
            f"zero by {_last}, so incumbent plant must exit rather than merely being "
            "permitted to. Units not in that scope still face no retirement mandate.")
        next_note = (
            "Settle on a single emission-accounting convention, extend the forced "
            "retirement scope to the remaining endowed units, and introduce a "
            "CO\u2082 price so abatement is driven by economics as well as the cap.")
    right = [
        ("Emission accounting",
         "Carbon is booked at both the supply step (gas import) and the conversion "
         "step for several industrial routes, and capture is netted both at the stack "
         "and at the injection well. A full reconciliation is in analysis_v2/."),
        ("Coverage",
         "Sectors without an explicit process route are represented by generic "
         "placeholder units. They carry demand correctly but their unit counts and "
         "capacities are not comparable with real plant."),
        ("Fleet turnover", fleet_note),
        ("Next steps", next_note),
    ]
    for col, items in ((0.045, left), (0.525, right)):
        # spread whatever number of items the column has over the same band
        step = 0.645 / max(len(items), 1)
        bar = min(0.155, step * 0.72)
        y = 0.72
        for title, body in items:
            fig.patches.append(plt.Rectangle((col, y - bar), 0.004, bar + 0.01,
                                             color=T.TEAL, transform=fig.transFigure,
                                             figure=fig))
            fig.text(col + 0.022, y, title, fontsize=12.5, color=T.INK,
                     fontweight="bold", va="top")
            fig.text(col + 0.022, y - 0.042, _wrap(body, 62), fontsize=9.8,
                     color=T.SUB, va="top", linespacing=1.6)
            y -= step
    T.source_note(fig, NOTE)
    save(fig, "P12_scope_and_method.png")


def _wrap(text, width):
    import textwrap
    return "\n".join(textwrap.wrap(text, width))


# ==========================================================================
def main(argv=None):
    global OUT, RESULTS_DB, INPUT_DB, NOTE, PDF_NAME, TITLE, SOLVER_NOTE, TEMPORAL_NOTE
    args = _parse_args(argv)
    RESULTS_DB = os.path.abspath(args.results)
    INPUT_DB = os.path.abspath(args.input_db)
    OUT = os.path.abspath(args.out)
    NOTE = NOTE_TEMPLATE.format(label=args.label)
    PDF_NAME = args.pdf
    TITLE = args.title
    SOLVER_NOTE = args.solver_note
    TEMPORAL_NOTE = args.temporal_note
    for path, what in ((RESULTS_DB, "results"), (INPUT_DB, "input")):
        if not os.path.exists(path):
            raise SystemExit(f"{what} database not found: {path}")
    print("  results ->", RESULTS_DB)
    print("  input   ->", INPUT_DB)

    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.startswith("P") and f.endswith(".png"):
            os.remove(os.path.join(OUT, f))
    T.apply()
    d = Data()

    unmatched = sorted({t for t in d.atm("to_node")["tech"].unique()
                        if X.emission_group(t) == "Other"})
    if unmatched:
        print("  [taxonomy] emission techs falling through to 'Other':", unmatched[:12])

    print("== slides ==")
    slide_cover(d)
    slide_pathway(d)
    slide_sources(d)
    slide_ccs_chain(d)
    E.slide_co2_geography(d, save, NOTE)
    slide_routes(d)
    slide_industry(d)
    E.slide_industry_detail(d, save, NOTE)
    slide_carriers(d)
    E.slide_supply_mix(d, save, NOTE, carrier="elec")
    E.slide_fuel_supply(d, save, NOTE)
    E.slide_transmission(d, save, NOTE)
    slide_buildout(d)
    slide_capacity_vintage(d)
    # slide_map(d) is superseded by E.slide_co2_geography, which draws the real
    # IC1 NUTS3 geometry from geodata/ instead of hand-placed schematic points.
    slide_region_table(d)
    slide_notes(d)

    pdf_path = os.path.join(OUT, PDF_NAME)
    with PdfPages(pdf_path) as pdf:
        for fig in PAGES:
            pdf.savefig(fig, facecolor=T.WHITE)
    print("  deck  ->", os.path.relpath(pdf_path, ROOT))
    for fig in PAGES:
        plt.close(fig)


if __name__ == "__main__":
    main()
