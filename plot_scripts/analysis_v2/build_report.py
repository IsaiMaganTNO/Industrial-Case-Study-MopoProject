"""Regenerate the IC1 summer CO2-rebuild report with corrected CO2 accounting,
explicit units and auditable technology groupings.

Writes everything to analysis_v2/out/ with a `v2_` prefix. Nothing in the parent
directory is read-write; the original report is left untouched.

    python analysis_v2/build_report.py
"""
from __future__ import annotations

import argparse
import os
import sys
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import TwoSlopeNorm

import model as M
import spine_io as sio

RESULTS_DB = os.path.join(ROOT, "RESULTS_Investment_Results.summer_co2rebuild.sqlite")
INPUT_DB = os.path.join(ROOT, "INPUT_Final_SpineOpt_Model.tiny.summer_co2rebuild.sqlite")
OUT = os.path.join(HERE, "out")

UNITS = "kt CO\u2082/yr (representative day \u00d7 365)"
ENERGY_CARRIERS = ("elec", "heat", "cool", "CH4", "H2")
CAVEAT = ("Single representative day: 19 August, weight 365. Summer-day bias \u2014 "
          "solar is above its annual mean, heating demand below it.")
RUN_LABEL = "CO2 rebuild"


def _parse_args(argv=None):
    p = argparse.ArgumentParser(description="Build the IC1 analysis_v2 report.")
    p.add_argument("--results", default=RESULTS_DB, help="results SQLite database")
    p.add_argument("--input", dest="input_db", default=INPUT_DB,
                   help="input SQLite database")
    p.add_argument("--out", default=OUT, help="output directory")
    p.add_argument("--caveat", default=CAVEAT,
                   help="temporal caveat printed on each figure")
    p.add_argument("--label", default=RUN_LABEL,
                   help="run name used in the summary heading")
    return p.parse_args(argv)

plt.rcParams.update({
    "figure.dpi": 130, "savefig.dpi": 130, "font.size": 9,
    "axes.grid": True, "grid.alpha": 0.25, "axes.axisbelow": True,
    "axes.spines.top": False, "axes.spines.right": False,
})


def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("  figure ->", os.path.relpath(path, ROOT))


def dump(df, name, **kw):
    path = os.path.join(OUT, name)
    df.to_csv(path, **kw)
    print("  table  ->", os.path.relpath(path, ROOT))


def footer(fig, text, y=-0.06):
    fig.text(0.5, y, textwrap.fill(text, 150), ha="center", va="top", fontsize=7,
             color="#555")


# ==========================================================================
def main(argv=None):
    global RESULTS_DB, INPUT_DB, OUT, CAVEAT, RUN_LABEL
    args = _parse_args(argv)
    RESULTS_DB = os.path.abspath(args.results)
    INPUT_DB = os.path.abspath(args.input_db)
    OUT = os.path.abspath(args.out)
    CAVEAT = args.caveat
    RUN_LABEL = args.label
    for path, what in ((RESULTS_DB, "results"), (INPUT_DB, "input")):
        if not os.path.exists(path):
            raise SystemExit(f"{what} database not found: {path}")
    print("  results ->", RESULTS_DB)
    print("  input   ->", INPUT_DB)
    os.makedirs(OUT, exist_ok=True)
    rcon, icon = sio.connect(RESULTS_DB), sio.connect(INPUT_DB)
    year_map, weight = M.temporal_structure(icon)
    total_w = M.annual_weight(weight, year_map)
    n_days = len([k for k in weight if k is not None]) // max(len(set(year_map.values())), 1) \
        if isinstance(weight, dict) else 1
    print(f"representative periods = {n_days} day(s)/year, total weight {total_w:g}")
    if isinstance(weight, dict):
        for ts, w in sorted((k, v) for k, v in weight.items() if k is not None):
            print(f"    {ts:%Y-%m-%d}  weight {w:.4f}")
    print(f"calendar year -> milestone    = {year_map}")

    uf = M.unit_flows(rcon, year_map, weight)
    cf = M.connection_flows(rcon, year_map, weight)
    atm_coef = M.atmosphere_coefficients(icon)
    factors = M.implied_ch4_factors(uf)
    lo, mid, hi = M.factor_band(factors)
    print(f"implied CO2-per-fossil-fuel factor: low {lo:.4f} / median {mid:.4f} / high {hi:.4f}")

    cls = M.classify_co2_producers(uf, atm_coef, mid)
    bal = M.co2_balance(uf, cls)
    bands = {k: M.co2_balance(uf, M.classify_co2_producers(uf, atm_coef, f))
             for k, f in (("low", lo), ("high", hi))}
    cap, smax = M.co2_cap(icon, weight, year_map)
    unbooked = M.unbooked_fuel_emissions(uf, cls, mid)
    dbl = M.fuel_carbon_double_booking(uf, atm_coef)
    flt = M.fleet(rcon, icon)
    evn = M.existing_vs_new(flt, icon)

    periods = sorted(bal.index)

    # ----------------------------------------------------------------- tables
    print("\n== tables ==")
    dump(bal.round(3), "v2_T01_co2_balance_annual.csv")
    dump(cls.sort_values(["treatment", "period", "co2_to_network"],
                         ascending=[True, True, False]).round(4),
         "v2_T02_co2_producer_classification.csv", index=False)

    atm_flows = uf[uf["node"] == M.ATMOSPHERE].copy()
    atm_flows["tech"] = atm_flows["unit"].map(M.tech_of)
    atm_flows["region"] = atm_flows["unit"].map(M.region_of)
    hourly = atm_flows[["period", "ts", "hour", "unit", "tech", "region", "direction",
                        "value_hourly", "value_annual"]].sort_values(["period", "hour", "unit"])
    dump(hourly, "v2_T03_atmosphere_flows_hourly.csv", index=False)

    emis = (atm_flows[atm_flows["direction"] == "to_node"]
            .groupby(["period", "tech", "region"])["value_annual"].sum()
            .reset_index().rename(columns={"value_annual": "gross_emissions"}))
    dump(emis[emis["gross_emissions"] > 0].sort_values(
        ["period", "gross_emissions"], ascending=[True, False]),
        "v2_T04_gross_emissions_by_tech_region.csv", index=False)

    prod = uf[(uf["node"].astype(str).str.fullmatch(M.CO2_NODE_RE)) &
              (uf["direction"] == "to_node")].merge(
        cls[["unit", "period", "treatment"]].drop_duplicates(), on=["unit", "period"])
    prod["tech"] = prod["unit"].map(M.tech_of)
    origin = (prod.groupby(["period", "treatment", "tech"])["value_annual"].sum()
              .reset_index().rename(columns={"value_annual": "co2_to_network"}))
    dump(origin[origin["co2_to_network"] > 0].sort_values(
        ["period", "co2_to_network"], ascending=[True, False]),
        "v2_T05_capture_by_origin.csv", index=False)

    dump(unbooked.round(3), "v2_T06_unbooked_fuel_emissions.csv", index=False)
    dump(flt.round(6), "v2_T07_fleet_units_and_capacity.csv", index=False)
    dump(evn[["unit", "tech", "region", "period", "initial", "existing_retained",
              "existing_retired", "new_build", "units_invested_available"]].round(6),
         "v2_T08_existing_vs_new.csv", index=False)

    sup = uf.copy()
    sup["carrier"] = sup["node"].astype(str).str.rsplit("_", n=1).str[0]
    sup = sup[sup["carrier"].isin(ENERGY_CARRIERS)]
    sup["signed"] = np.where(sup["direction"] == "to_node",
                             sup["value_annual"], -sup["value_annual"])
    sup["tech"] = sup["unit"].map(M.tech_of)
    supply = (sup.groupby(["period", "carrier", "tech"])["signed"].sum()
              .reset_index().rename(columns={"signed": "net_production_annual"}))
    dump(supply[supply["net_production_annual"].abs() > 1e-6],
         "v2_T09_net_supply_by_carrier_tech.csv", index=False)

    dump(dbl.sort_values(["period", "double_booked"], ascending=[True, False]).round(3),
         "v2_T10_fuel_carbon_double_booked.csv", index=False)

    # ---------------------------------------------------------------- figures
    print("\n== figures ==")
    fig_co2_balance(bal, cap, periods)
    fig_waterfall(bal, periods)
    fig_emissions_top_tech(emis, bal, periods)
    fig_capture_origin(origin, cls, periods)
    fig_dac_sensitivity(bal, bands, unbooked, (lo, mid, hi), periods)
    fig_net_by_region(uf, cls, periods)
    fig_fleet_capacity(flt, periods)
    fig_existing_vs_new(evn, periods)
    fig_supply(supply, periods)
    fig_cap_binding(bal, cap, periods)
    fig_fuel_double_booking(dbl, bal, periods)

    # ---------------------------------------------------------------- summary
    write_summary(bal, bands, cap, cls, origin, unbooked, (lo, mid, hi), flt, evn, factors,
                  year_map, weight, smax, periods, dbl)
    print("\nDone. Outputs in", os.path.relpath(OUT, ROOT))


# ==========================================================================
# figures
# ==========================================================================
def fig_co2_balance(bal, cap, periods):
    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    x = np.arange(len(periods))
    w = 0.27
    series = [("net reported by the model", "net_reported_by_model", "#8ab4f8", "#1a73e8"),
              ("+ remove the duplicated stack credit", "net_corrected_core", "#fdd663", "#b06000"),
              ("+ remove credit on never-booked fossil carbon", "net_corrected_full",
               "#f28b82", "#c5221f")]
    for i, (label, col, fc, ec) in enumerate(series):
        v = bal.loc[periods, col]
        ax.bar(x + (i - 1) * w, v, w, label=label, color=fc, edgecolor=ec)
        for xi, val in enumerate(v):
            ax.annotate(f"{val:,.0f}", (xi + (i - 1) * w, val), ha="center",
                        va="bottom" if val >= 0 else "top", fontsize=7.5,
                        fontweight="bold" if i == 2 else "normal")
    capv = [cap.get(p, cap.get(p + 1, np.nan)) for p in periods]
    ax.plot(x, capv, ls="none", marker="_", ms=58, mew=1.8, color="k",
            label="CO\u2082 cap (annual equivalent)")
    ax.axhline(0, color="k", lw=0.9)
    ax.set_xticks(x); ax.set_xticklabels(periods)
    ax.set_ylabel(UNITS)
    ax.set_title("Net CO\u2082 to atmosphere: as reported vs corrected", loc="left",
                 fontweight="bold")
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.09),
              ncol=2, fontsize=8)
    footer(fig, "2050 is reported as net zero. Removing only the unambiguous duplicate gives "
                f"{bal.loc[periods[-1], 'net_corrected_core']:,.0f}; also charging fossil "
                f"carbon that never entered the emission account gives "
                f"{bal.loc[periods[-1], 'net_corrected_full']:,.0f}.", y=-0.20)
    save(fig, "v2_F01_net_co2_reported_vs_corrected.png")


def fig_waterfall(bal, periods):
    labels = ["gross\nemissions", "valid removal\n(air + biogenic)", "CORRECTED\nnet",
              "credit on unbooked\nfossil carbon", "credit duplicating\nstack netting",
              "reported\nnet"]
    fig, axes = plt.subplots(1, len(periods), figsize=(3.8 * len(periods), 5.2), sharey=True)
    axes = np.atleast_1d(axes)
    for ax, p in zip(axes, periods):
        r = bal.loc[p]
        deltas = [r["gross_emissions_to_atmosphere"], -r["credit_that_is_valid"], None,
                  -r["credit_on_unbooked_fossil_carbon"],
                  -r["credit_duplicating_stack_netting"], None]
        colors = ["#c5221f", "#188038", "#1a73e8", "#fdd663", "#bdbdbd", "#9aa0a6"]
        scale = max(1.0, abs(r["gross_emissions_to_atmosphere"]))
        run = 0.0
        tops = []
        for i, (delta, color) in enumerate(zip(deltas, colors)):
            if delta is None:
                ax.bar(i, run, 0.6, color=color, edgecolor="k", lw=0.5)
                ax.annotate(f"{run:,.0f}", (i, run), ha="center", va="bottom",
                            fontsize=8, fontweight="bold")
                tops.append(run)
            else:
                ax.bar(i, delta, 0.6, bottom=run, color=color, edgecolor="k", lw=0.5)
                if abs(delta) > 0.06 * scale:
                    ax.annotate(f"{delta:+,.0f}", (i, run + delta / 2), ha="center",
                                va="center", fontsize=7, color="white", clip_on=False)
                run += delta
                tops.append(run)
            if i < len(deltas) - 1:
                ax.plot([i + 0.3, i + 0.7], [run, run], color="#9e9e9e", lw=0.8, ls=":")
        ax.axhline(0, color="k", lw=0.9)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, fontsize=7, rotation=45, ha="right")
        ax.set_title(str(p), fontweight="bold", pad=16)
    top = float(bal["gross_emissions_to_atmosphere"].max())
    axes[0].set_ylim(min(0.0, float(bal["net_corrected_full"].min()) * 1.1), top * 1.14)
    axes[0].set_ylabel(UNITS)
    fig.suptitle("Where the reported CO\u2082 balance comes from", x=0.02, y=1.02,
                 ha="left", fontweight="bold")
    fig.subplots_adjust(bottom=0.30)
    footer(fig, "Grey = credit for capture that was already subtracted at the stack. "
                "Yellow = credit for fossil carbon that never entered the emission account.",
           y=-0.02)
    save(fig, "v2_F02_co2_balance_waterfall.png")


def fig_emissions_top_tech(emis, bal, periods, top=12):
    piv = emis.pivot_table(index="tech", columns="period", values="gross_emissions",
                           aggfunc="sum").fillna(0.0).reindex(columns=periods, fill_value=0.0)
    order = piv.sum(axis=1).sort_values(ascending=False)
    keep = order.head(top).index
    small = piv.drop(index=keep).sum()
    plot = piv.loc[keep]
    plot.loc[f"all other technologies (n={len(order) - len(keep)})"] = small

    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(12.6, 5.2),
                                  gridspec_kw={"width_ratios": [1.6, 1.0]})
    x = np.arange(len(periods))
    bottom = np.zeros(len(periods))
    cmap = plt.get_cmap("tab20")
    for i, tech in enumerate(plot.index):
        vals = plot.loc[tech].values
        ax.bar(x, vals, 0.6, bottom=bottom, label=tech, color=cmap(i % 20), edgecolor="white", lw=0.4)
        bottom += vals
    for xi, v in enumerate(bottom):
        ax.annotate(f"{v:,.0f}", (xi, v), ha="center", va="bottom", fontsize=8, fontweight="bold")
    ax.set_xticks(x); ax.set_xticklabels(periods)
    ax.set_ylabel(UNITS)
    ax.set_title("GROSS CO\u2082 emitted to the atmosphere, by technology", loc="left",
                 fontweight="bold")
    ax.legend(frameon=False, fontsize=7, ncol=2, loc="upper center",
              bbox_to_anchor=(0.5, -0.08))

    rem = bal.loc[periods, ["credit_that_is_valid", "credit_on_unbooked_fossil_carbon",
                            "credit_duplicating_stack_netting"]]
    base = np.zeros(len(periods))
    for col, color, lab in [
            ("credit_that_is_valid", "#188038", "valid removal (air + biogenic)"),
            ("credit_on_unbooked_fossil_carbon", "#fdd663", "fossil carbon never booked"),
            ("credit_duplicating_stack_netting", "#bdbdbd", "already netted at the stack")]:
        ax2.bar(x, -rem[col].values, 0.6, bottom=base, color=color, label=lab)
        base -= rem[col].values
    ax2.axhline(0, color="k", lw=0.9)
    ax2.set_xticks(x); ax2.set_xticklabels(periods)
    ax2.set_ylabel(UNITS)
    ax2.set_title("Removals, shown separately", loc="left", fontweight="bold")
    ax2.legend(frameon=False, fontsize=7.5, loc="upper center", bbox_to_anchor=(0.5, -0.08))
    footer(fig, "Unlike the original figure 08, geological injection is NOT netted inside "
                "an 'other' category here.", y=-0.28)
    save(fig, "v2_F03_gross_emissions_by_technology.png")


TREAT_SUFFIX = {
    "netted_at_source": "already netted at stack",
    "no_emission_booked": "no stack emission booked",
}
TREAT_COLOR = {"netted_at_source": "#bdbdbd", "no_emission_booked": "#188038"}


def fig_capture_origin(origin, cls, periods):
    g = (cls.groupby(["treatment", "tech", "period"])[
             ["co2_to_network", "credit_eligible"]].sum().reset_index())
    g = g[g["co2_to_network"] > 1e-6]
    piv = g.pivot_table(index=["treatment", "tech"], columns="period",
                        values="co2_to_network", aggfunc="sum").fillna(0.0)
    piv = piv.reindex(columns=periods, fill_value=0.0).sort_values(periods[-1])
    elig = (g.pivot_table(index=["treatment", "tech"], columns="period",
                          values="credit_eligible", aggfunc="sum")
            .fillna(0.0).reindex(index=piv.index, columns=periods, fill_value=0.0))

    labels = [f"{t}\n({TREAT_SUFFIX[tr]})" for tr, t in piv.index]
    fig, ax = plt.subplots(figsize=(10.0, 0.80 * len(piv) + 2.6))
    y = np.arange(len(piv))
    h = 0.24
    for yi, (tr, _) in enumerate(piv.index):
        ax.axhspan(y[yi] - 0.45, y[yi] + 0.45, color=TREAT_COLOR[tr], alpha=0.10, zorder=0)
    for i, p in enumerate(periods):
        off = (i - 1) * h
        ax.barh(y + off, piv[p].values, h, color="#e0e0e0", edgecolor="#9e9e9e", lw=0.4,
                label="CO\u2082 into the network" if i == 0 else None)
        ax.barh(y + off, elig[p].values, h, color="#188038", edgecolor="#0b5c23", lw=0.4,
                label="of which the removal credit is valid" if i == 0 else None)
        for yi, v in enumerate(piv[p].values):
            if v > 0:
                ax.annotate(f"{p}: {v:,.0f}", (v, y[yi] + off), va="center", ha="left",
                            fontsize=6.5, xytext=(4, 0), textcoords="offset points")
    ax.set_yticks(y); ax.set_yticklabels(labels, fontsize=7.5)
    ax.set_xlabel(UNITS)
    ax.set_xscale("symlog", linthresh=1.0)
    ax.set_xlim(left=0)
    ax.set_title("CO\u2082 sent into the capture network, by source (log scale)", loc="left",
                 fontweight="bold")
    ax.legend(frameon=False, fontsize=7.5, loc="lower right")
    ax.grid(axis="y", visible=False)
    footer(fig, "Green fill is the part of each source that genuinely removes carbon from the "
                "air or from biomass. Grey-shaded rows already have their capture subtracted "
                "from their own stack emission, so the injector credit duplicates it.", y=-0.04)
    save(fig, "v2_F04_capture_by_origin_and_treatment.png")


def fig_dac_sensitivity(bal, bands, unbooked, band, periods):
    lo, mid, hi = band
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(11.6, 5.0),
                                  gridspec_kw={"width_ratios": [1.2, 1.0]})
    x = np.arange(len(periods))
    mid_v = bal.loc[periods, "net_corrected_full"].values
    lo_v = bands["low"].loc[periods, "net_corrected_full"].values
    hi_v = bands["high"].loc[periods, "net_corrected_full"].values
    ax.bar(x, mid_v, 0.5, color="#f28b82", edgecolor="#c5221f",
           label=f"fully corrected (median factor {mid:.3f})")
    ax.errorbar(x, mid_v, yerr=[np.maximum(mid_v - lo_v, 0), np.maximum(hi_v - mid_v, 0)],
                fmt="none", ecolor="k", capsize=6, lw=1.1,
                label=f"factor inter-quartile range {lo:.3f}\u2013{hi:.3f}")
    ax.plot(x, bal.loc[periods, "net_reported_by_model"], "o--", color="#1a73e8",
            label="as reported in the original report")
    for xi, v in enumerate(mid_v):
        ax.annotate(f"{v:,.0f}", (xi, v), ha="center", va="bottom", fontsize=8,
                    fontweight="bold")
    ax.axhline(0, color="k", lw=0.9)
    ax.set_xticks(x); ax.set_xticklabels(periods)
    ax.set_ylabel(UNITS)
    ax.set_title("Net CO\u2082 after the full correction,\nand its sensitivity to the assumed "
                 "emission factor", loc="left", fontweight="bold", fontsize=10)
    ax.legend(frameon=False, fontsize=7.5, loc="upper center", bbox_to_anchor=(0.5, -0.08))

    top = unbooked.copy()
    top["label"] = top["unit"] + "   " + top["period"].astype(str)
    top = top.sort_values("fossil_co2_implied")
    yy = np.arange(len(top))
    ax2.barh(yy, top["fossil_co2_implied"].values, 0.45, color="#e37400",
             edgecolor="k", lw=0.3)
    for i, v in enumerate(top["fossil_co2_implied"].values):
        ax2.annotate(f"{v:,.0f}", (v, yy[i]), va="center", ha="left", fontsize=8,
                     xytext=(4, 0), textcoords="offset points")
    ax2.set_yticks(yy); ax2.set_yticklabels(top["label"], fontsize=8)
    ax2.set_ylim(-0.8, len(top) - 0.2)
    ax2.set_xlabel(UNITS)
    ax2.set_xlim(0, float(top["fossil_co2_implied"].max()) * 1.35)
    ax2.set_title("Fossil CO\u2082 implied by the fuel burnt in units\nthat book no stack "
                  "emission at all", loc="left", fontweight="bold", fontsize=10)
    ax2.grid(axis="y", visible=False)
    footer(fig, "`DAC`, `SMR+CC` and `CCGT+CC` have no `atmosphere` relationship in the input "
                "database, so the fuel they burn produces no booked emission. Factors inferred "
                "from CH\u2084-only units that do report to the atmosphere.", y=-0.22)
    save(fig, "v2_F05_unbooked_fossil_carbon_sensitivity.png")


def fig_net_by_region(uf, cls, periods):
    atm = uf[uf["node"] == M.ATMOSPHERE].copy()
    atm["region"] = atm["unit"].map(M.region_of)
    sign = np.where(atm["direction"] == "to_node", 1.0, -1.0)
    atm["signed"] = atm["value_annual"] * sign
    piv = atm.pivot_table(index="region", columns="period", values="signed",
                          aggfunc="sum").fillna(0.0).reindex(columns=periods, fill_value=0.0)
    piv = piv.loc[piv.abs().sum(axis=1).sort_values(ascending=False).index]

    vmax = float(np.abs(piv.values).max())
    norm = TwoSlopeNorm(vmin=-vmax, vcenter=0.0, vmax=vmax)
    fig, ax = plt.subplots(figsize=(6.4, 0.32 * len(piv) + 2.2))
    im = ax.imshow(piv.values, cmap="RdBu_r", norm=norm, aspect="auto")
    ax.set_xticks(range(len(periods))); ax.set_xticklabels(periods)
    ax.set_yticks(range(len(piv))); ax.set_yticklabels(piv.index, fontsize=8)
    for i in range(piv.shape[0]):
        for j in range(piv.shape[1]):
            v = piv.values[i, j]
            ax.text(j, i, f"{v:,.0f}", ha="center", va="center", fontsize=7,
                    color="white" if abs(v) > 0.55 * vmax else "black")
    ax.grid(visible=False)
    fig.colorbar(im, ax=ax, label=UNITS, fraction=0.05, pad=0.03)
    ax.set_title("Net CO\u2082 to atmosphere by region, as the model books it\n"
                 "diverging scale centred on zero", loc="left", fontweight="bold")
    footer(fig, "Negative values sit where the injection WELL is, not where the CO\u2082 was "
                "produced. Read as an artefact of credit allocation, not regional performance.")
    save(fig, "v2_F06_net_co2_by_region.png")


def fig_fleet_capacity(flt, periods, top=18):
    real = flt[~flt["is_placeholder"]].copy()
    piv = real.pivot_table(index="tech", columns="period", values="capacity_available",
                           aggfunc="sum").fillna(0.0)
    piv = piv.reindex(columns=periods, fill_value=0.0)
    piv = piv.loc[piv.sum(axis=1).sort_values(ascending=False).head(top).index].iloc[::-1]

    n_ph = int(flt["is_placeholder"].sum())
    fig, ax = plt.subplots(figsize=(9.4, 0.36 * len(piv) + 2.8))
    y = np.arange(len(piv)); h = 0.26
    for i, p in enumerate(periods):
        ax.barh(y + (i - 1) * h, piv[p].values, h, label=str(p),
                color=plt.get_cmap("viridis")(0.15 + 0.35 * i), edgecolor="k", lw=0.3)
    ax.set_yticks(y); ax.set_yticklabels(piv.index, fontsize=8)
    ax.set_xscale("log")
    ax.set_xlabel("available capacity (log scale)  =  units_invested_available "
                  "\u00d7 capacity_per_unit")
    ax.set_title(f"Installed fleet in CAPACITY terms, top {top} real technologies", loc="left",
                 fontweight="bold")
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    ax.grid(axis="y", visible=False)
    footer(fig, f"{n_ph} generic '*-production-reference' entity-periods are excluded: they are "
                f"sector stand-ins whose capacity_per_unit is arbitrary, and most sit exactly on "
                f"their own 1000-unit investment bound.", y=-0.05)
    save(fig, "v2_F07_fleet_capacity_real_technologies.png")


def fig_existing_vs_new(evn, periods):
    real = evn[~evn["is_placeholder"]]
    g = real.groupby("period")[["existing_retained", "existing_retired", "new_build"]].sum()
    g = g.reindex(periods).fillna(0.0)
    allu = evn.groupby("period")[["existing_retained", "new_build"]].sum().reindex(periods)

    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(10.4, 4.3))
    x = np.arange(len(periods))
    ax.bar(x, g["existing_retained"], 0.55, label="pre-2030 fleet retained", color="#1a73e8")
    ax.bar(x, g["existing_retired"], 0.55, bottom=g["existing_retained"],
           label="pre-2030 fleet retired", color="#d93025", alpha=0.75)
    for xi in x:
        tot = g["existing_retained"].iloc[xi] + g["existing_retired"].iloc[xi]
        ax.annotate(f"{g['existing_retained'].iloc[xi]:,.1f} kept",
                    (xi, g["existing_retained"].iloc[xi] / 2), ha="center", va="center",
                    fontsize=7.5, color="white")
        ax.annotate(f"{tot:,.1f}", (xi, tot), ha="center", va="bottom", fontsize=8)
    ax.set_xticks(x); ax.set_xticklabels(periods)
    ax.set_ylabel("units (placeholders excluded)")
    ax.set_title("What survives of the fleet that existed in 2030", loc="left", fontweight="bold")
    ax.legend(frameon=False, fontsize=8)

    ax2.bar(x - 0.2, allu["existing_retained"], 0.4, label="existing retained", color="#1a73e8")
    ax2.bar(x + 0.2, allu["new_build"], 0.4, label="new build", color="#f9ab00")
    ax2.set_yscale("log")
    ax2.set_xticks(x); ax2.set_xticklabels(periods)
    ax2.set_ylabel("units, log scale (all entities)")
    ax2.set_title("Why the original chart was unreadable", loc="left", fontweight="bold")
    ax2.legend(frameon=False, fontsize=8)
    for xi in x:
        ax2.annotate(f"{allu['existing_retained'].iloc[xi]:,.1f}",
                     (xi - 0.2, allu["existing_retained"].iloc[xi]), ha="center", va="bottom",
                     fontsize=7)
        ax2.annotate(f"{allu['new_build'].iloc[xi]:,.0f}",
                     (xi + 0.2, allu["new_build"].iloc[xi]), ha="center", va="bottom", fontsize=7)
    footer(fig, "'Existing' is min(units_available, investment_count_initial_cumulative) \u2014 "
                "NOT total fleet minus this period's additions.")
    save(fig, "v2_F08_existing_fleet_retained_vs_retired.png")


def fig_supply(supply, periods):
    carriers = [c for c in ENERGY_CARRIERS
                if supply.loc[supply["carrier"] == c, "net_production_annual"].sum() > 0]
    fig, axes = plt.subplots(1, len(carriers), figsize=(2.9 * len(carriers), 4.8),
                             squeeze=False)
    axes = axes[0]
    x = np.arange(len(periods))
    cmap = plt.get_cmap("tab20")
    for ax, carrier in zip(axes, carriers):
        sub = supply[(supply["carrier"] == carrier) & (supply["net_production_annual"] > 0)]
        piv = (sub.pivot_table(index="tech", columns="period", values="net_production_annual",
                               aggfunc="sum").fillna(0.0)
               .reindex(columns=periods, fill_value=0.0))
        order = piv.sum(axis=1).sort_values(ascending=False)
        keep = order.head(7).index
        plot = piv.loc[keep].copy()
        if len(order) > len(keep):
            plot.loc["other"] = piv.drop(index=keep).sum()
        bottom = np.zeros(len(periods))
        for i, tech in enumerate(plot.index):
            ax.bar(x, plot.loc[tech].values, 0.62, bottom=bottom, label=tech,
                   color=cmap(i % 20), edgecolor="white", lw=0.4)
            bottom += plot.loc[tech].values
        ax.set_xticks(x); ax.set_xticklabels(periods, fontsize=8)
        ax.set_title(carrier, fontweight="bold")
        ax.legend(frameon=False, fontsize=6, loc="upper center", bbox_to_anchor=(0.5, -0.09))
    axes[0].set_ylabel("net annual production (representative day \u00d7 365)")
    fig.subplots_adjust(wspace=0.45)
    fig.suptitle("Net production by energy carrier \u2014 annualised from one August day",
                 x=0.02, y=1.02, ha="left", fontweight="bold")
    footer(fig, CAVEAT + "  Storage round-trips are netted out (to_node minus from_node on "
                         "the same carrier).", y=-0.30)
    save(fig, "v2_F09_net_supply_by_carrier.png")


def fig_cap_binding(bal, cap, periods):
    fig, ax = plt.subplots(figsize=(7.6, 4.0))
    x = np.arange(len(periods))
    capv = np.array([cap.get(p, cap.get(p + 1, np.nan)) for p in periods], dtype=float)
    net = bal.loc[periods, "net_reported_by_model"].values
    ax.bar(x, capv, 0.5, color="#e8eaed", edgecolor="#5f6368", label="cap (annual equivalent)")
    ax.plot(x, net, "o-", color="#c5221f", lw=2, label="net emissions as solved")
    for xi in x:
        slack = capv[xi] - net[xi]
        ax.annotate(f"cap {capv[xi]:,.0f}\nsolved {net[xi]:,.0f}\nslack {slack:,.2g}",
                    (xi, max(capv[xi], net[xi])), ha="center", va="bottom", fontsize=7.5,
                    xytext=(0, 6), textcoords="offset points")
    ax.set_ylim(0, max(capv) * 1.32)
    ax.set_xticks(x); ax.set_xticklabels(periods)
    ax.set_ylabel(UNITS)
    ax.set_title("The CO\u2082 cap binds in every period\nthis run is cap-driven, not cost-driven",
                 loc="left", fontweight="bold", fontsize=10)
    ax.legend(frameon=False, fontsize=8, loc="upper right")
    footer(fig, "Cap = atmosphere.storage_investment_count_max_cumulative \u00d7 storage_state_max "
                "\u00d7 representative weight. The cover page rounds 0.45315 to '0.5'.")
    save(fig, "v2_F10_cap_binding_check.png")


# ==========================================================================
def fig_fuel_double_booking(dbl, bal, periods):
    if dbl.empty:
        return
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(12.0, 5.0),
                                  gridspec_kw={"width_ratios": [1.0, 1.25]})
    x = np.arange(len(periods))
    g = dbl.groupby(["carrier", "period"])["double_booked"].sum().unstack("period")
    g = g.reindex(columns=periods, fill_value=0.0).fillna(0.0)
    gross = bal.loc[periods, "gross_emissions_to_atmosphere"].values
    ax.bar(x, gross, 0.55, color="#e0e0e0", edgecolor="#9e9e9e",
           label="gross emissions as the model books them")
    bottom = np.zeros(len(periods))
    for i, carrier in enumerate(g.index):
        ax.bar(x, g.loc[carrier].values, 0.55, bottom=bottom, color=["#c5221f", "#e8710a"][i % 2],
               label=f"of which {carrier} carbon charged twice")
        bottom += g.loc[carrier].values
    for xi in x:
        ax.annotate(f"{bottom[xi] / gross[xi]:.0%}", (xi, bottom[xi]), ha="center",
                    va="bottom", fontsize=9, fontweight="bold", color="#c5221f")
    ax.set_xticks(x); ax.set_xticklabels(periods)
    ax.set_ylabel(UNITS)
    ax.set_title("Fuel carbon counted at two steps of the same chain", loc="left",
                 fontweight="bold")
    ax.legend(frameon=False, fontsize=7.5, loc="upper center", bbox_to_anchor=(0.5, -0.08))

    top = (dbl.groupby("tech")[["consumed", "own_emission",
                                "carbon_already_charged_upstream", "double_booked"]].sum()
           .sort_values("double_booked", ascending=False).head(10).iloc[::-1])
    yy = np.arange(len(top))
    ax2.barh(yy, top["own_emission"].values, 0.55, color="#e0e0e0", edgecolor="#9e9e9e",
             label="emission the unit books itself")
    ax2.barh(yy, top["double_booked"].values, 0.55, color="#c5221f",
             label="of which already charged at the supply step")
    for i, (own, d) in enumerate(zip(top["own_emission"], top["double_booked"])):
        ax2.annotate(f"{d / own:.0%}" if own else "", (own, yy[i]), va="center", ha="left",
                     fontsize=7.5, xytext=(4, 0), textcoords="offset points")
    ax2.set_yticks(yy)
    ax2.set_yticklabels([t if len(t) <= 28 else t[:26] + "\u2026" for t in top.index], fontsize=8)
    ax2.set_xlabel(UNITS + "  (summed over all three milestones)")
    ax2.set_title("Which technologies are charged twice", loc="left", fontweight="bold")
    ax2.legend(frameon=False, fontsize=7.5, loc="lower right")
    ax2.grid(axis="y", visible=False)
    footer(fig, "`LNG-terminal` is the fossil-methane import route: it delivers CH\u2084 1:1 and "
                "books 0.2 CO\u2082 per unit, the full combustion factor of natural gas. "
                "`CCGT`/`OCGT` rely on that and book nothing; `(NG)PEA`, `(NG)NH3`, `REF-SMR` "
                "and `(LN)O` book their own combustion emission on top.", y=-0.22)
    save(fig, "v2_F11_fuel_carbon_double_booked.png")


def write_summary(bal, bands, cap, cls, origin, unbooked, band, flt, evn, factors,
                  year_map, weight, smax, periods, dbl):
    lo, mid, hi = band
    ph = int(flt["is_placeholder"].sum())
    total_w = M.annual_weight(weight, year_map)
    rep_days = (sorted((k, v) for k, v in weight.items() if k is not None)
                if isinstance(weight, dict) else [])
    lines = []
    A = lines.append
    n_days = len(rep_days) // max(len(set(year_map.values())), 1) if rep_days else 1
    A(f"# Corrected summary - IC1 {n_days}-day run, {RUN_LABEL}")
    A("")
    A("Regenerated directly from the two SQLite databases. The original report in the")
    A("parent directory is untouched. All CO2 values are **annual** (each representative")
    A(f"day x its own weight; the weights total {total_w:g}).")
    A("")
    if rep_days:
        A("| representative day | weight |")
        A("|---|---|")
        for ts, w in rep_days:
            A(f"| {ts:%Y-%m-%d} | {w:.4f} |")
        A("")
    A("## 1. Temporal mapping actually used by the solver")
    A("")
    A("| calendar year in the result DB | milestone label |")
    A("|---|---|")
    for y, m in sorted(year_map.items()):
        A(f"| {y} | {m} |")
    A("")
    A("The 2040 milestone is solved on calendar **2041** while investment decisions are")
    A("indexed at 2040-01-01. Any chart that keys on `ts.year` silently drops it.")
    A("")
    A("## 2. CO2 balance")
    A("")
    cols = ["gross_emissions_to_atmosphere", "injection_credit_applied_by_model",
            "credit_that_is_valid", "credit_duplicating_stack_netting",
            "credit_on_unbooked_fossil_carbon", "net_reported_by_model",
            "net_corrected_core", "net_corrected_full"]
    A("| period | " + " | ".join(c.replace("_", " ") for c in cols) + " |")
    A("|" + "---|" * (len(cols) + 1))
    for p in periods:
        A(f"| {p} | " + " | ".join(f"{bal.loc[p, c]:,.1f}" for c in cols) + " |")
    A("")
    A("### 2a. Credit that duplicates stack netting (no assumptions needed)")
    A("")
    A("In the input database an abated route books only its residual stack emission")
    A("(`REF-SMR-MEA` atmosphere coefficient 0.002) while the unabated route books the")
    A("full 0.019 and the captured 0.017 goes to the CO2 network. The injector then")
    A("*also* withdraws 1 t from the `atmosphere` node per tonne injected, so that")
    A("capture is counted twice. Affected routes:")
    A("")
    dup = (cls[cls["treatment"] == "netted_at_source"]
           .groupby("tech")["co2_to_network"].sum().sort_values(ascending=False))
    for tech, v in dup[dup > 0].items():
        A(f"- `{tech}` - {v:,.1f} over the three milestones")
    A("")
    A(f"2050 is reported as net zero; removing only this duplicate gives "
      f"**{bal.loc[periods[-1], 'net_corrected_core']:,.0f}**.")
    A("")
    A("### 2b. Credit on fossil carbon that was never booked as an emission")
    A("")
    A("`DAC`, `SMR+CC` and `CCGT+CC` have no `atmosphere` relationship at all in the")
    A("input database. They consume fossil fuel, emit nothing on paper, and then earn a")
    A("full removal credit at the injector. Only the share of their CO2 that cannot be")
    A("explained by their own fossil input is a genuine removal.")
    A("")
    A("| unit | period | fossil input | implied fossil CO2 | CO2 to network | valid credit |")
    A("|---|---|---|---|---|---|")
    for r in unbooked.head(12).itertuples():
        A(f"| {r.unit} | {r.period} | {r.fossil_input:,.0f} | {r.fossil_co2_implied:,.0f} | "
          f"{r.co2_to_network:,.0f} | {r.credit_eligible:,.0f} |")
    A("")
    A(f"Emission factor inferred from CH4-only units that *do* report to the atmosphere: "
      f"median **{mid:.4f}**, inter-quartile {lo:.4f}-{hi:.4f} "
      f"(n={int(factors['books_atmosphere'].sum()) if len(factors) else 0}).")
    A("")
    A("| period | reported | core correction | full correction (low / median / high) |")
    A("|---|---|---|---|")
    for p in periods:
        A(f"| {p} | {bal.loc[p, 'net_reported_by_model']:,.0f} | "
          f"{bal.loc[p, 'net_corrected_core']:,.0f} | "
          f"{bands['low'].loc[p, 'net_corrected_full']:,.0f} / "
          f"{bal.loc[p, 'net_corrected_full']:,.0f} / "
          f"{bands['high'].loc[p, 'net_corrected_full']:,.0f} |")
    A("")
    A("## 3. Fuel carbon charged at two steps of the same chain")
    A("")
    A("`LNG-terminal` is not a terminal in the physical sense. In the input database it")
    A("takes `fossil-CH4` and delivers `CH4_<region>` 1:1 while emitting **0.2** per unit")
    A("to `atmosphere` - the standard combustion factor of natural gas, not a")
    A("liquefaction or leakage term. So the model books the carbon content of imported")
    A("gas where it enters the system.")
    A("")
    A("That convention is fine on its own, but it is not applied uniformly:")
    A("")
    A("- `CCGT-existing`, `CCGT`, `OCGT` have **no** `atmosphere` relationship and book")
    A("  nothing. Consistent with the supply-step convention.")
    A("- `(NG)PEA`, `(NG)NH3`, `REF-SMR`, `(LN)O` and the `*-production-reference` units")
    A("  book their own combustion emission on top. For `(NG)PEA_BEC4`:")
    A("  `atmosphere/chemical-PEA = 0.459` and `chemical-PEA/CH4 = 0.442`, so")
    A("  0.459 x 0.442 = **0.2029 CO2 per CH4** - the same combustion factor the")
    A("  terminal already charged.")
    A("")
    A("| period | carrier | double booked | % of gross emissions |")
    A("|---|---|---|---|")
    gd = dbl.groupby(["period", "carrier"])["double_booked"].sum()
    for (p, c), v in gd.items():
        A(f"| {p} | {c} | {v:,.0f} | "
          f"{v / bal.loc[p, 'gross_emissions_to_atmosphere'] * 100:.1f}% |")
    tot = dbl.groupby("period")["double_booked"].sum()
    A("")
    A("| period | gross as booked | double-booked fuel carbon | % |")
    A("|---|---|---|---|")
    for p in periods:
        v = tot.get(p, 0.0)
        g = bal.loc[p, "gross_emissions_to_atmosphere"]
        A(f"| {p} | {g:,.0f} | {v:,.0f} | {v / g * 100:.1f}% |")
    A("")
    A("The same pattern holds on the `HC` (refinery product) chain: `REF-SMR` books an")
    A("emission when it produces HC, and `(LN)O` books one again when it consumes HC.")
    A("")
    A("**This pushes the opposite way to section 2.** Double-booked fuel carbon inflates")
    A("gross emissions; double-counted capture inflates removals. The reported net is the")
    A("difference of two large errors, so it cannot be repaired by post-processing - the")
    A("input database needs one convention applied consistently. The corrected nets in")
    A("section 2 fix only the removal side and should be read as upper bounds on gross.")
    A("")
    A("## 4. The cap binds in every period")
    A("")
    A(f"`atmosphere.storage_state_max` = {smax:g}; the cap is")
    A("`storage_investment_count_max_cumulative x storage_state_max x weight`.")
    A("")
    A("| period | cap (annual) | solved net | slack |")
    A("|---|---|---|---|")
    for p in periods:
        c = cap.get(p, cap.get(p + 1, float("nan")))
        n = bal.loc[p, "net_reported_by_model"]
        A(f"| {p} | {c:,.1f} | {n:,.1f} | {c - n:,.3g} |")
    A("")
    A("The emission trajectory is therefore an input, not a result. The cover page of the")
    A("original report prints 0.5 / 0.1 / 0.0 for caps that are 0.45315 / 0.10082 / 0.0.")
    A("")
    A("## 5. Fleet")
    A("")
    A(f"{ph} entity-periods are generic `*-production-reference` placeholders sitting")
    A("exactly on their own 1000-unit investment bound. They are ~99.9% of any 'units'")
    A("total, which is why the original figures 02, 03, 05 and 07 show a single flat bar.")
    A("Figures F07/F08 here exclude them and report capacity instead.")
    A("")
    A("| period | existing retained | existing retired | new build (real tech) |")
    A("|---|---|---|---|")
    real = evn[~evn["is_placeholder"]].groupby("period")[
        ["existing_retained", "existing_retired", "new_build"]].sum()
    for p in periods:
        if p in real.index:
            r = real.loc[p]
            A(f"| {p} | {r['existing_retained']:,.2f} | {r['existing_retired']:,.2f} | "
              f"{r['new_build']:,.2f} |")
    A("")
    A("`existing` = min(units_invested_available, investment_count_initial_cumulative).")
    A("The original report derives `vintage` from the `-existing` suffix in the technology")
    A("name, so endowed plant such as `REF-SMR` (initial count 45.1 in NLC6) is labelled")
    A("'new'. Its figure 06 then computes `total fleet - this period's additions`, which is")
    A("why it shows 'retained existing capacity' growing from 0 to 175,000.")
    A("")
    A("## 6. Standing caveat")
    A("")
    A(textwrap.fill(CAVEAT, 88))
    A("")
    A("Treat every annual energy figure as a summer-day extrapolation. Wind falling to")
    A("exactly zero by 2050 and cooling demand exceeding heat demand are artefacts of")
    A("this sampling, not findings.")
    A("")
    A("## 7. Files")
    A("")
    A("`v2_T03_atmosphere_flows_hourly.csv` carries an explicit `hour` column. The")
    A("original CSVs write one row per hour with no timestamp, so the rows look like")
    A("exact duplicates and any `drop_duplicates()` or `aggfunc='first'` understates")
    A("totals by a factor of 24.")
    A("")

    path = os.path.join(OUT, "v2_SUMMARY.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print("  summary->", os.path.relpath(path, ROOT))


if __name__ == "__main__":
    main()
