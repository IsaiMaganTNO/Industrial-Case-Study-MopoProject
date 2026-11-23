"""Extra slides for the IC1 deck: real maps, supply mix, industry detail.

Every function takes the shared `Data` object from build_deck plus the `save`
callback, so this module stays free of circular imports.
"""
from __future__ import annotations

import re
import textwrap

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import geo
import model as M
import taxonomy as X
import theme as T

# ORIGIN_carrier_DEST, e.g. BEC1_elec_BEC2. External links (BEC3_elec_FR) are
# matched separately so imports/exports are not silently dropped.
LINK = re.compile(r"^((?:NL|BE)C\d+)_([A-Za-z0-9\-\+]+)_((?:NL|BE)C\d+)$")
EXT = re.compile(r"^((?:NL|BE)C\d+)_([A-Za-z0-9\-\+]+)_([A-Z]{2})$")

CARRIER_LABEL = {"elec": "Electricity", "CH4": "Methane", "H2": "Hydrogen",
                 "CO2": "Carbon dioxide", "bio": "Biomass", "HC": "Hydrocarbons"}
CARRIER_COLOR = {"elec": T.BLUE, "CH4": T.SAND, "H2": T.VIOLET,
                 "CO2": T.TEAL, "bio": T.GREEN, "HC": T.SLATE}


def _wrap(text, width):
    return "\n".join(textwrap.wrap(text, width))


# ==========================================================================
# shared data helpers
# ==========================================================================
def transmission(d):
    """Internal region-to-region connection flows, tagged with carrier."""
    cf = d.cf[d.cf["direction"] == "to_node"].copy()
    m = cf["connection"].astype(str).map(LINK.match)
    cf = cf[m.notna()].copy()
    m = m[m.notna()]
    cf["origin"] = [x.group(1) for x in m]
    cf["carrier"] = [x.group(2) for x in m]
    cf["dest"] = [x.group(3) for x in m]
    return (cf.groupby(["carrier", "origin", "dest", "period"])["value_annual"]
            .sum().reset_index())


def external(d):
    """Flows on links that leave the NL+BE footprint."""
    cf = d.cf[d.cf["direction"] == "to_node"].copy()
    m = cf["connection"].astype(str).map(lambda n: EXT.match(n) if not LINK.match(n) else None)
    cf = cf[m.notna()].copy()
    m = m[m.notna()]
    cf["region"] = [x.group(1) for x in m]
    cf["carrier"] = [x.group(2) for x in m]
    cf["country"] = [x.group(3) for x in m]
    return (cf.groupby(["carrier", "region", "country", "period"])["value_annual"]
            .sum().reset_index())


def injection_links(d):
    """Captured CO2 moving from a coastal region into an offshore reservoir."""
    inj = d.uf[d.uf["node"].astype(str).str.startswith("CO2-storage")
               & (d.uf["direction"] == "to_node")].copy()
    inj["reservoir"] = inj["node"].astype(str).str.replace("CO2-storage-", "", regex=False)
    inj["region"] = inj["unit"].map(M.region_of)
    return (inj.groupby(["region", "reservoir", "period"])["value_annual"]
            .sum().reset_index())


def _net_arrows(df, value="value_annual"):
    """Collapse A->B and B->A into a single net arrow in the dominant direction."""
    acc = {}
    for row in df.itertuples():
        key = tuple(sorted((row.origin, row.dest)))
        sign = 1.0 if (row.origin, row.dest) == key else -1.0
        acc[key] = acc.get(key, 0.0) + sign * getattr(row, value)
    out = []
    for (a, b), v in acc.items():
        if abs(v) < 1e-9:
            continue
        out.append((a, b, v) if v > 0 else (b, a, -v))
    return out


def _basemap(ax, highlight=None, show_offshore=True, pad=0.06):
    reg = geo.regions()
    res = geo.reservoirs()
    colls = (reg, res) if show_offshore else (reg,)
    geo.setup_axes(ax, geo.bounds_of(*colls), pad=pad)
    if show_offshore:
        geo.paint(ax, res, default="#dce8ec", edgecolor=T.TEAL, lw=0.9, zorder=1,
                  alpha=0.75)
    geo.paint(ax, reg, facecolors=highlight, default="#eef2f5",
              edgecolor=T.WHITE, lw=0.9, zorder=2)
    return reg, res


def _country_outline(ax):
    """Thin separator so NL and BE read as two countries."""
    reg = geo.regions()
    for grp, col in (("NL", T.SLATE), ("BE", T.SLATE)):
        verts = [r for k, v in reg.items() if k.startswith(grp) for r in v["rings"]]
        for ring in verts:
            ax.plot(ring[:, 0], ring[:, 1], color=col, lw=0.35, alpha=0.5, zorder=3)


def _arrow(ax, p0, p1, color, lw, rad=0.14, alpha=0.8, zorder=5, shrink=9):
    ax.annotate("", p1, p0, zorder=zorder,
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, alpha=alpha,
                                shrinkA=shrink, shrinkB=shrink,
                                connectionstyle=f"arc3,rad={rad}"))


def _width(v, vmax, lo=0.9, hi=6.5):
    if vmax <= 0:
        return lo
    return lo + (hi - lo) * (max(v, 0.0) / vmax) ** 0.55

# ==========================================================================
# S1 - captured CO2: where it is caught, where it goes, where it is buried
# ==========================================================================
def slide_co2_geography(d, save, note):
    last = d.periods[-1]
    reg_df = d.regional().set_index(["region", "period"])
    cap = {r: float(reg_df["captured"].get((r, last), 0.0)) for r in geo.regions()}
    emi = {r: float(reg_df["emitted"].get((r, last), 0.0)) for r in geo.regions()}
    pipes = transmission(d)
    pipes = pipes[(pipes["carrier"] == "CO2") & (pipes["period"] == last)]
    arrows = _net_arrows(pipes)
    inj = injection_links(d)
    inj = inj[(inj["period"] == last) & (inj["value_annual"] > 1e-6)]

    fig = plt.figure(figsize=(13.33, 7.5))
    T.headline(fig, "The carbon network",
               "Captured in the chemical clusters, buried under the North Sea",
               f"{last}. Shading is CO\u2082 captured in each region, violet arrows are "
               "onshore pipeline flows and teal arrows are injection into the two "
               "offshore reservoirs the model actually uses.")

    ax = fig.add_axes([0.03, 0.055, 0.60, 0.72])
    shade = geo.ramp(cap, "#f2f6f8", T.TEAL, vmax=max(cap.values()) or 1.0)
    reg, res = _basemap(ax, highlight=shade)
    _country_outline(ax)

    cen = geo.centroids("onshore")
    rcen = geo.centroids("offshore")

    # emission bubbles on top of the capture choropleth
    emax = max(emi.values()) or 1.0
    for r, (x, y) in cen.items():
        e = emi.get(r, 0.0)
        if e > 1e-6:
            ax.scatter([x], [y], s=25 + 620 * (e / emax), color=T.CORAL, alpha=0.32,
                       edgecolor="none", zorder=4)

    pmax = max([v for _, _, v in arrows], default=1.0)
    for a, b, v in arrows:
        if a not in cen or b not in cen:
            continue
        _arrow(ax, cen[a], cen[b], T.VIOLET, _width(v, pmax, 1.0, 5.0), rad=0.16,
               alpha=0.85, zorder=6)

    imax = float(inj["value_annual"].max()) if len(inj) else 1.0
    for row in inj.itertuples():
        if row.region not in cen or row.reservoir not in rcen:
            continue
        _arrow(ax, cen[row.region], rcen[row.reservoir], T.TEAL,
               _width(row.value_annual, imax, 1.4, 7.0), rad=-0.18, alpha=0.75,
               zorder=6, shrink=11)

    for k, (x, y) in rcen.items():
        ax.scatter([x], [y], marker="s", s=52, color=T.TEAL, zorder=7,
                   edgecolor=T.WHITE, lw=1.0)
        ax.text(x, y + 0.14, k, fontsize=8, color=T.TEAL, ha="center", va="bottom",
                fontweight="bold", zorder=8)

    hub = sorted(cap, key=cap.get, reverse=True)[:4]
    for r, (x, y) in cen.items():
        big = r in hub or emi.get(r, 0) > 0.25 * emax
        ax.text(x, y - 0.075, r, fontsize=8.0 if big else 6.8,
                color=T.INK if big else T.FAINT, ha="center", va="top", zorder=8,
                fontweight="bold" if big else "normal")

    ax.scatter([], [], marker="s", s=52, color=T.TEAL, label="offshore reservoir")
    ax.scatter([], [], s=130, color=T.CORAL, alpha=0.32, label="CO\u2082 still emitted")
    ax.plot([], [], color=T.VIOLET, lw=3, label="onshore CO\u2082 pipeline")
    ax.plot([], [], color=T.TEAL, lw=3, label="offshore injection")
    ax.legend(loc="lower left", fontsize=8.5, frameon=False, handlelength=1.6)

    # ------------------------------------------------------------- right rail
    rx = 0.665
    tot_cap = sum(cap.values())
    tot_inj = float(inj["value_annual"].sum())
    pipe_tot = sum(v for _, _, v in arrows)
    T.card(fig, (rx, 0.595, 0.30, 0.115), f"{tot_cap/1000:,.1f} Mt",
           f"captured onshore in {last}",
           f"across {sum(1 for v in cap.values() if v > 1e-6)} of 17 regions", T.TEAL)
    T.card(fig, (rx, 0.455, 0.30, 0.115), f"{pipe_tot/1000:,.1f} Mt",
           "moved by onshore pipeline",
           f"{len(arrows)} net links carry it to the coast", T.VIOLET)
    T.card(fig, (rx, 0.315, 0.30, 0.115), f"{tot_inj/1000:,.1f} Mt",
           "injected offshore",
           "NSNL031 takes essentially all of it", T.BLUE)

    top = sorted(((v, k) for k, v in cap.items() if v > 1e-6), reverse=True)[:4]
    lines = "\n".join(f"{k}  {geo.regions()[k]['props'].get('cluster_id','').replace('_',' ')[:22]:<22s}"
                      f"{v/1000:>6,.1f} Mt" for v, k in top)
    fig.text(rx, 0.265, "Where the capture sits", fontsize=11.5, color=T.INK,
             fontweight="bold", va="top")
    fig.text(rx, 0.225, lines, fontsize=9, color=T.SUB, va="top", linespacing=1.75,
             family="DejaVu Sans Mono")
    fig.text(rx, 0.105, _wrap("Geometry is the real IC1 NUTS3 cluster definition and "
                              "the licensed North Sea blocks, not a schematic.", 52),
             fontsize=8.5, color=T.FAINT, va="top", linespacing=1.5)

    T.source_note(fig, note)
    save(fig, "co2_geography.png")

# ==========================================================================
# S2 - the transmission network, carrier by carrier
# ==========================================================================
def slide_transmission(d, save, note, carriers=("elec", "CH4", "H2")):
    last = d.periods[-1]
    tx = transmission(d)
    ext = external(d)

    fig = plt.figure(figsize=(13.33, 7.5))
    T.headline(fig, "Moving the energy",
               "Electricity spreads; methane and hydrogen stay on corridors",
               f"Net inter-regional flows in {last}. Opposing flows on a link are "
               "netted into one arrow, so the headline figure is smaller than the gross "
               "volume quoted beneath it. Each panel is scaled to its own maximum.")

    width = 0.295
    for n, carrier in enumerate(carriers):
        ax = fig.add_axes([0.035 + n * 0.315, 0.20, width, 0.56])
        sub = tx[(tx["carrier"] == carrier) & (tx["period"] == last)]
        arrows = _net_arrows(sub)
        cen = geo.centroids("onshore")

        # shade each region by net import (red) / net export (blue) balance
        bal = {r: 0.0 for r in cen}
        for a, b, v in arrows:
            bal[a] = bal.get(a, 0.0) - v
            bal[b] = bal.get(b, 0.0) + v
        _basemap(ax, highlight=None, show_offshore=False, pad=0.03)

        col = CARRIER_COLOR.get(carrier, T.SLATE)
        vmax = max([v for _, _, v in arrows], default=1.0)
        for a, b, v in arrows:
            if a not in cen or b not in cen:
                continue
            _arrow(ax, cen[a], cen[b], col, _width(v, vmax, 0.8, 5.2), rad=0.13,
                   alpha=0.85, zorder=6, shrink=4)

        # external links drawn as stubs pointing off the edge of the map
        e = ext[(ext["carrier"] == carrier) & (ext["period"] == last)]
        e = e.groupby(["region", "country"])["value_annual"].sum()
        for (r, cty), v in e.items():
            if r not in cen or v < 1e-6:
                continue
            x, y = cen[r]
            dx, dy = {"FR": (-0.35, -0.5), "DE": (0.55, 0.0), "UK": (-0.6, 0.25),
                      "LU": (0.45, -0.4)}.get(cty, (0.4, 0.4))
            ax.annotate("", (x + dx, y + dy), (x, y), zorder=5,
                        arrowprops=dict(arrowstyle="-|>", color=T.FAINT,
                                        lw=_width(v, vmax, 0.7, 3.0), alpha=0.8,
                                        shrinkA=4, shrinkB=0))
            ax.text(x + dx * 1.12, y + dy * 1.12, cty, fontsize=6.5, color=T.FAINT,
                    ha="center", va="center", zorder=7)

        gross = float(sub["value_annual"].sum())
        net = sum(v for _, _, v in arrows)
        n_links = sub[sub["value_annual"] > 1e-9].groupby(["origin", "dest"]).ngroups
        ax.set_title(CARRIER_LABEL.get(carrier, carrier), fontsize=13, color=T.INK,
                     fontweight="bold", pad=10)
        ax.text(0.5, -0.045, f"{net/1000:,.0f} GWh net between regions",
                transform=ax.transAxes, fontsize=9, color=col, ha="center",
                fontweight="bold")
        ax.text(0.5, -0.085,
                f"{len(arrows)} net arrows \u00b7 {n_links} directed links used "
                f"\u00b7 {gross/1000:,.0f} GWh gross",
                transform=ax.transAxes, fontsize=8.2, color=T.FAINT, ha="center")

    # ------------------------------------------------- bottom strip: evolution
    axb = fig.add_axes([0.035, 0.085, 0.925, 0.075])
    piv = (tx.groupby(["carrier", "period"])["value_annual"].sum()
           .unstack("period").reindex(columns=d.periods).fillna(0.0))
    order = [c for c in ("elec", "CH4", "H2", "bio", "HC", "CO2") if c in piv.index]
    piv = piv.loc[order]
    left = np.zeros(len(d.periods))
    totals = piv.sum(axis=0).values
    for carrier in order:
        vals = piv.loc[carrier].values / np.maximum(totals, 1e-9)
        for j, p in enumerate(d.periods):
            axb.barh([j], [vals[j]], left=[left[j]], height=0.62,
                     color=CARRIER_COLOR.get(carrier, T.SLATE), edgecolor=T.WHITE,
                     lw=0.8)
            if vals[j] > 0.06:
                axb.text(left[j] + vals[j] / 2, j, CARRIER_LABEL.get(carrier, carrier),
                         fontsize=7.5, color=T.WHITE, ha="center", va="center",
                         fontweight="bold")
        left += vals
    axb.set_yticks(range(len(d.periods)))
    axb.set_yticklabels([str(p) for p in d.periods], fontsize=9, color=T.INK)
    axb.set_xlim(0, 1)
    axb.set_xticks([])
    for s in axb.spines.values():
        s.set_visible(False)
    axb.tick_params(length=0)
    axb.text(0, 1.45, "Share of all inter-regional transport, by carrier",
             transform=axb.transAxes, fontsize=9.5, color=T.SUB)

    T.source_note(fig, note)
    save(fig, "transmission_network.png")

# ==========================================================================
# S3 - supply mix: what is installed vs what actually gets delivered
# ==========================================================================
def _mix(d, carrier):
    s = d.uf[(d.uf["carrier"] == carrier) & (d.uf["direction"] == "to_node")].copy()
    s["group"] = s["tech"].map(X.supply_group)
    gen = (s.groupby(["group", "period"])["value_annual"].sum()
           .unstack("period").reindex(columns=d.periods).fillna(0.0))
    units = set(s[s["value_annual"].abs() > 1e-9]["unit"])
    f = d.fleet[d.fleet["unit"].isin(units)].copy()
    f["group"] = f["tech"].map(X.supply_group)
    cap = (f.groupby(["group", "period"])["capacity_available"].sum()
           .unstack("period").reindex(columns=d.periods).fillna(0.0))
    cap = cap.reindex(gen.index).fillna(0.0)
    return gen, cap


def slide_supply_mix(d, save, note, carrier="elec"):
    gen, cap = _mix(d, carrier)
    gen = gen[gen.sum(axis=1) > 1e-6]
    cap = cap.reindex(gen.index).fillna(0.0)
    order = gen.sum(axis=1).sort_values(ascending=False).index.tolist()
    gen, cap = gen.loc[order], cap.loc[order]
    cols = [X.SUPPLY_COLOR.get(g, T.FAINT) for g in order]
    first, last = d.periods[0], d.periods[-1]

    fig = plt.figure(figsize=(13.33, 7.5))
    T.headline(fig, "Where the electricity comes from",
               f"Supply mix shifts between {first} and {last}",
               "Left: installed capacity available in each milestone year. Right: the "
               "energy those plants actually deliver. The two disagree because a solar "
               "GW and a biomass GW do very different numbers of hours.")

    def stacked(ax, df, title, unit_label, scale):
        xs = np.arange(len(d.periods))
        bottom = np.zeros(len(d.periods))
        for g, c in zip(order, cols):
            v = df.loc[g].values / scale
            ax.bar(xs, v, 0.56, bottom=bottom, color=c, edgecolor=T.WHITE, lw=0.9,
                   label=g)
            bottom += v
        for j, tot in enumerate(bottom):
            ax.annotate(f"{tot:,.0f}", (xs[j], tot), xytext=(0, 6),
                        textcoords="offset points", ha="center", fontsize=10,
                        color=T.INK, fontweight="bold")
        ax.set_xticks(xs)
        ax.set_xticklabels([str(p) for p in d.periods], fontsize=11, color=T.INK)
        ax.set_ylim(0, float(bottom.max()) * 1.16)
        ax.set_ylabel(unit_label)
        ax.set_title(title, fontsize=12.5, color=T.INK, fontweight="bold", pad=12,
                     loc="left")
        T.strip_axes(ax)

    ax1 = fig.add_axes([0.055, 0.155, 0.235, 0.56])
    stacked(ax1, cap, "Installed capacity", "GW available", 1.0)
    ax2 = fig.add_axes([0.355, 0.155, 0.235, 0.56])
    stacked(ax2, gen, "Energy delivered", "TWh per year", 1000.0)

    handles, labels = ax2.get_legend_handles_labels()
    fig.legend(handles[::-1], labels[::-1], loc="lower center",
               bbox_to_anchor=(0.32, 0.015), ncol=4, fontsize=9.5, frameon=False)

    # ----------------------------------------------- right: utilisation change
    ax3 = fig.add_axes([0.665, 0.155, 0.285, 0.56])
    rows = []
    for g in order:
        c_last, g_last = cap.loc[g, last], gen.loc[g, last]
        c_first, g_first = cap.loc[g, first], gen.loc[g, first]
        rows.append({"group": g,
                     "cf_first": (g_first / (c_first * 8760) if c_first > 1e-6 else np.nan),
                     "cf_last": (g_last / (c_last * 8760) if c_last > 1e-6 else np.nan)})
    cfm = pd.DataFrame(rows).set_index("group")
    cfm = cfm.dropna(how="all")
    ys = np.arange(len(cfm))[::-1]
    for y, (g, row) in zip(ys, cfm.iterrows()):
        col = X.SUPPLY_COLOR.get(g, T.FAINT)
        a, b = row["cf_first"], row["cf_last"]
        if not np.isnan(a) and not np.isnan(b):
            ax3.plot([a, b], [y, y], color=T.RULE, lw=3, solid_capstyle="round",
                     zorder=1)
        if not np.isnan(a):
            ax3.scatter([a], [y], s=52, color=T.WHITE, edgecolor=T.SLATE, lw=1.6,
                        zorder=2)
        if not np.isnan(b):
            ax3.scatter([b], [y], s=78, color=col, zorder=3, edgecolor="none")
            ax3.annotate(f"{b:.0%}", (b, y), xytext=(8, 0), textcoords="offset points",
                         va="center", fontsize=8.5, color=col, fontweight="bold")
    ax3.set_yticks(ys)
    ax3.set_yticklabels(cfm.index, fontsize=9.5, color=T.INK)
    ax3.set_xlim(0, float(np.nanmax(cfm.values)) * 1.32)
    ax3.xaxis.set_major_formatter(lambda v, p: f"{v:.0%}")
    ax3.set_xlabel("capacity factor")
    ax3.set_title(f"How hard each fleet works  ({first} \u2192 {last})", fontsize=12.5,
                  color=T.INK, fontweight="bold", pad=12, loc="left")
    T.strip_axes(ax3)
    ax3.grid(axis="y", visible=False)

    T.source_note(fig, note)
    save(fig, "supply_mix_electricity.png")

# ==========================================================================
# S4 - the molecules: methane, hydrogen, biomass
# ==========================================================================
def slide_fuel_supply(d, save, note, carriers=("CH4", "H2", "bio")):
    fig = plt.figure(figsize=(13.33, 7.5))
    T.headline(fig, "Where the molecules come from",
               "LNG gives way to biomethane; hydrogen arrives by ship, not by electrolyser",
               "Annual delivery of each energy carrier by the type of plant or terminal "
               "that supplies it. Electrolysis never enters the solution.")

    for n, carrier in enumerate(carriers):
        gen, _ = _mix(d, carrier)
        gen = gen[gen.sum(axis=1) > 1e-6]
        if gen.empty:
            continue
        order = gen.sum(axis=1).sort_values(ascending=False).index.tolist()
        gen = gen.loc[order]
        ax = fig.add_axes([0.055 + n * 0.315, 0.235, 0.235, 0.50])
        xs = np.arange(len(d.periods))
        bottom = np.zeros(len(d.periods))
        for g in order:
            v = gen.loc[g].values / 1000.0
            ax.bar(xs, v, 0.56, bottom=bottom, color=X.SUPPLY_COLOR.get(g, T.FAINT),
                   edgecolor=T.WHITE, lw=0.9)
            for j in range(len(xs)):
                if v[j] / max(bottom.max() + v.max(), 1e-9) > 0.07:
                    ax.text(xs[j], bottom[j] + v[j] / 2, g, fontsize=7.8,
                            color=T.WHITE, ha="center", va="center", fontweight="bold")
            bottom += v
        for j, tot in enumerate(bottom):
            ax.annotate(f"{tot:,.0f}", (xs[j], tot), xytext=(0, 6),
                        textcoords="offset points", ha="center", fontsize=9.5,
                        color=T.INK, fontweight="bold")
        ax.set_xticks(xs)
        ax.set_xticklabels([str(p) for p in d.periods], fontsize=10.5, color=T.INK)
        ax.set_ylim(0, float(bottom.max()) * 1.18)
        if n == 0:
            ax.set_ylabel("TWh per year")
        ax.set_title(CARRIER_LABEL.get(carrier, carrier), fontsize=12.5, color=T.INK,
                     fontweight="bold", pad=10, loc="left")
        T.strip_axes(ax)

    # Methane and hydrogen notes are stable across runs (LNG gives way to
    # biomethane upgrading; hydrogen is imported, never electrolysed). The biomass
    # line is computed, because whether biomass grows depends on the scenario.
    _bio = d.uf[(d.uf["carrier"] == "bio") & (d.uf["direction"] == "to_node")]
    _first_bio = float(_bio[_bio["period"] == d.periods[0]]["value_annual"].sum())
    _last_bio = float(_bio[_bio["period"] == d.periods[-1]]["value_annual"].sum())
    if _first_bio > 1e-6:
        _pct = (_last_bio - _first_bio) / _first_bio * 100.0
        _dir = "grows" if _pct > 1 else ("falls" if _pct < -1 else "is flat")
        _bio_note = (f"Biomass supply {_dir} {abs(_pct):.0f}% between {d.periods[0]} and "
                     f"{d.periods[-1]}, reaching {_last_bio / 1000.0:,.0f} TWh. The BECCS "
                     "credit on this volume matters to the net balance.")
    else:
        _bio_note = (f"Biomass supply reaches {_last_bio / 1000.0:,.0f} TWh by "
                     f"{d.periods[-1]}; the BECCS credit on it matters to the net "
                     "balance.")
    notes = [
        ("Methane", "LNG imports more than halve as biomethane and methanation take "
                    "over from 2040. Domestic extraction never runs."),
        ("Hydrogen", "All of it is imported as liquid hydrogen. No electrolyser is "
                     "built in any year \u2014 cheap import undercuts them, and the "
                     "representative day gives no cheap-power hours to exploit."),
        ("Biomass", _bio_note),
    ]
    for n, (title, body) in enumerate(notes):
        x = 0.055 + n * 0.315
        fig.patches.append(plt.Rectangle((x, 0.055), 0.004, 0.115, color=T.TEAL,
                                        transform=fig.transFigure, figure=fig))
        fig.text(x + 0.016, 0.168, title, fontsize=11, color=T.INK,
                 fontweight="bold", va="top")
        fig.text(x + 0.016, 0.133, _wrap(body, 44), fontsize=9, color=T.SUB,
                 va="top", linespacing=1.6)

    T.source_note(fig, note)
    save(fig, "fuel_supply.png")

# ==========================================================================
# S5 - industry decarbonisation, sector by sector
# ==========================================================================
def slide_industry_detail(d, save, note, top_n=12):
    first, last = d.periods[0], d.periods[-1]
    rm = d.route_mix()
    if rm.empty:
        return
    tot = (rm[rm["period"] == last].groupby("sector")["output"].sum()
           .sort_values(ascending=False))
    sectors = [s for s in tot.index if s in X.SECTORS.values()][:top_n]

    fig = plt.figure(figsize=(13.33, 7.5))
    T.headline(fig, "Industry, sector by sector",
               "Only the sectors with an explicit CCS route move at all",
               f"Each bar is one sector's {last} output split by the route that made it. "
               "Output is held fixed by demand, so the entire story is the mix, not the "
               "level. Sectors are ordered by size.")

    ax = fig.add_axes([0.175, 0.145, 0.44, 0.60])
    ys = np.arange(len(sectors))[::-1]
    piv = (rm[rm["period"] == last].pivot_table(index="sector", columns="route",
                                                values="output", aggfunc="sum")
           .reindex(sectors).fillna(0.0))
    piv = piv.div(piv.sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)
    routes = [r for r in X.ROUTE_ORDER if r in piv.columns]
    left = np.zeros(len(sectors))
    for r in routes:
        v = piv[r].values
        ax.barh(ys, v, 0.62, left=left, color=X.ROUTE_COLOR.get(r, T.FAINT),
                edgecolor=T.WHITE, lw=0.9, label=r)
        for k in range(len(ys)):
            if v[k] > 0.14:
                ax.text(left[k] + v[k] / 2, ys[k], f"{v[k]:.0%}", fontsize=8,
                        color=T.WHITE, ha="center", va="center", fontweight="bold")
        left += v
    ax.set_yticks(ys)
    ax.set_yticklabels(sectors, fontsize=10, color=T.INK)
    ax.set_xlim(0, 1)
    ax.xaxis.set_major_formatter(lambda v, p: f"{v:.0%}")
    ax.set_xlabel(f"share of {last} output")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.10), ncol=4, fontsize=9,
              frameon=False)
    T.strip_axes(ax)
    ax.grid(axis="y", visible=False)

    # ------------------------------------- middle: emission intensity movement
    ax2 = fig.add_axes([0.645, 0.145, 0.15, 0.60])
    atm = d.atm("to_node").copy()
    atm["sector"] = atm["unit"].map(
        lambda u: next((lab for pre, lab in X.SECTORS.items()
                        if M.tech_of(u).startswith(pre)), None))
    out = rm.groupby(["sector", "period"])["output"].sum()
    em = atm.groupby(["sector", "period"])["value_annual"].sum()
    vals = []
    for s in sectors:
        a = em.get((s, first), 0.0) / max(out.get((s, first), np.nan), 1e-9)
        b = em.get((s, last), 0.0) / max(out.get((s, last), np.nan), 1e-9)
        vals.append((a, b))
    vmax = max([max(a, b) for a, b in vals] + [1e-9])
    for y, (a, b) in zip(ys, vals):
        ax2.plot([a, b], [y, y], color=T.RULE, lw=3, solid_capstyle="round", zorder=1)
        ax2.scatter([a], [y], s=48, color=T.WHITE, edgecolor=T.SLATE, lw=1.5, zorder=2)
        ax2.scatter([b], [y], s=70, color=T.CORAL if b > 0.02 * vmax else T.TEAL,
                    zorder=3, edgecolor="none")
    ax2.set_yticks(ys)
    ax2.tick_params(labelleft=False, length=0)
    ax2.set_ylim(ax.get_ylim())
    ax2.set_xlim(-0.03 * vmax, vmax * 1.12)
    ax2.set_xlabel("t CO\u2082 per unit output")
    ax2.set_title(f"{first} \u2192 {last}", fontsize=10, color=T.SUB, pad=8, loc="left")
    T.strip_axes(ax2)
    ax2.grid(axis="y", visible=False)

    # ------------------------------------------------------------- right rail
    rx = 0.825
    fig.text(rx, 0.735, "What moves, and what does not", fontsize=12.5, color=T.INK,
             fontweight="bold", va="top")
    # The steel bullet used to assert that primary steel never moves because the
    # legacy fleet is never retired. That is only true of the unmodified model, so
    # decide it from the data instead of stating it.
    first_p, last_p = d.periods[0], d.periods[-1]
    steel = d.uf[(d.uf["carrier"] == "steel-primary")
                 & (d.uf["direction"] == "to_node")]
    bf_last = float(steel[(steel["period"] == last_p)
                          & (steel["tech"] == "BF-BOF")]["value_annual"].sum())
    tot_last = float(steel[steel["period"] == last_p]["value_annual"].sum())
    if tot_last > 1e-9 and bf_last / tot_last > 0.99:
        steel_title = "Primary steel does not move"
        steel_body = (f"Output stays coal BF-BOF through {last_p}. The legacy fleet is "
                      "never forced to retire, so the clean route has nothing to "
                      "replace.")
    else:
        alt = (steel[(steel["period"] == last_p) & (steel["tech"] != "BF-BOF")]
               .groupby("tech")["value_annual"].sum().sort_values(ascending=False))
        winner = str(alt.index[0]) if not alt.empty else "an alternative route"
        bf_share = 100.0 * bf_last / tot_last if tot_last > 1e-9 else 0.0
        steel_title = "Primary steel switches route"
        steel_body = (f"BF-BOF falls to {bf_share:.0f}% of primary steel by {last_p}, "
                      f"with {winner} taking over the balance.")
    bullets = [
        (T.TEAL, "Routes with a capture variant",
         "Where an MEA capture variant exists, the model takes it as soon as the cap "
         "bites."),
        (T.CORAL, steel_title, steel_body),
        (T.FAINT, "Most light industry is a placeholder",
         "Sectors without a modelled process route carry demand through a generic "
         "unit, so their mix is not meaningful."),
    ]
    y = 0.665
    for col, title, body in bullets:
        fig.patches.append(plt.Rectangle((rx, y - 0.145), 0.0035, 0.155, color=col,
                                        transform=fig.transFigure, figure=fig))
        fig.text(rx + 0.014, y, title, fontsize=10.5, color=T.INK,
                 fontweight="bold", va="top")
        fig.text(rx + 0.014, y - 0.035, _wrap(body, 36), fontsize=9, color=T.SUB,
                 va="top", linespacing=1.6)
        y -= 0.215

    T.source_note(fig, note)
    save(fig, "industry_detail.png")
