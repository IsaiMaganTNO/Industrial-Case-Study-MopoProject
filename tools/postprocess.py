r"""Standalone post-processor for IC1 Investment_Results.

Reads a SpineOpt results SQLite and writes plots + CSVs to a report folder.
Does NOT touch any pipeline code.

Usage:
  .\.venv\Scripts\python.exe tools\postprocess.py [results.sqlite] [-o outdir]
                                                  [-m model.sqlite]
"""
from __future__ import annotations
import argparse, os, re, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from spinedb_api import DatabaseMapping
from spinedb_api.parameter_value import from_database

warnings.filterwarnings("ignore")

DEFAULT_DB = r".spinetoolbox\items\investment_results\Investment_Results.sqlite"
MODEL_DB = r".spinetoolbox\items\final_spineopt_model\Final_SpineOpt_Model.sqlite"
GEOJSON = r"geodata\IC1.geojson"
REGION = re.compile(r"_((?:BE|NL)C\d)$")
# Matches a region code anywhere in a name, e.g. connection 'NLC2_CO2_NLC5'.
REGION_ANY = re.compile(r"(?:BE|NL)C\d")

# Milestone (investment) years actually modelled. Operational temporal blocks
# may sit on a *different* calendar year than the milestone they represent:
# the pipeline places operations_y2040 / representative_period_2040_1 on
# calendar 2041. Timestamps are snapped to the nearest milestone so that all
# plots are labelled 2030 / 2040 / 2050.
MILESTONES = (2030, 2040, 2050)

# Industrial commodity nodes -> heavy-industry sector label.
SECTOR_NODES = {
    "steel-primary": "steel (primary)",
    "steel-secondary": "steel (secondary)",
    "cement": "cement",
    "chemical-olefins": "olefins",
    "chemical-chlorine": "chlorine",
    "fertiliser-ammonia-NH3": "ammonia",
    "glass-float": "glass (float)",
    "glass-container": "glass (container)",
    "glass-fibre": "glass (fibre)",
    "aluminium-primary": "aluminium",
    "pulp": "pulp",
    "paper": "paper",
}

# Energy-carrier nodes -> label for the supply-mix plots.
#
# These are the carriers whose SUPPLY MIX we chart, as opposed to the
# industrial commodity nodes above (whose PRODUCTION ROUTES we chart).
#
# Why this matters: the fleet plots show installed CAPACITY, which can move in
# the opposite direction to delivered ENERGY. In the 2-representative-day run
# the model built zero new solar PV yet retained 42.5 units of existing solar
# (vs 3.3 in the 1-rep run) - a decarbonisation choice expressed entirely
# through DECOMMISSIONING, and completely invisible in a "new investment" chart.
CARRIER_NODES = {
    "elec": "electricity",
    "heat": "heat",
    "H2": "hydrogen",
    "CH4": "methane",
    "cool": "cooling",
}

# Capture-equipped process routes are flagged by these tokens in the tech name.
# Matching MUST be on token boundaries, not bare substrings: a plain "cal"
# also matches "other-chemi(cal)s" and "pharmaceuti(cal)s", which are ordinary
# sector routes with no capture. Tokens are delimited by start/end or - + _ ( )
CC_TOKENS = ("cc", "mea", "dea", "cal", "oxy")
_CC_RE = re.compile(
    r"(?:^|[-+_()])(?:" + "|".join(CC_TOKENS) + r")(?:$|[-+_()])", re.I)


def to_milestone(year):
    if year is None:
        return None
    return min(MILESTONES, key=lambda m: abs(m - year))


# ---------------------------------------------------------------- categories
def classify(t: str) -> str:
    l = t.lower()
    if "production-alternative" in l:      return "industry: clean process route"
    if "production-reference" in l:        return "industry: reference process"
    if is_cc(t):                           return "industry: CCS-equipped"
    if l.startswith("dac"):                return "CO2 removal (DAC)"
    if "ref(h2)" in l or "smr" in l:       return "hydrogen production"
    if any(s in l for s in ("pem", "aec", "soec", "diaphragm")): return "electrolysis"
    if "meoh" in l or "(bm)ft" in l or "nh3" in l: return "e-fuels / green chemicals"
    if l.startswith("bio"):                return "bioenergy"
    if "solar" in l or "pv" in l:          return "solar PV"
    if "wind-of" in l or "wind-fo" in l or "wind-fb" in l: return "wind offshore"
    if "wind" in l:                        return "wind onshore"
    if "heatpump" in l:                    return "electrification (heat pumps)"
    if "ocgt" in l or "ccgt" in l or "gas-boiler" in l: return "unabated fossil"
    if "boiler" in l:                      return "boilers (other fuels)"
    if "-dr_" in l or l.endswith("-dr"):   return "demand response"
    return "other"


def is_cc(tech: str) -> bool:
    """True if this process route carries carbon capture."""
    return bool(_CC_RE.search(tech))


def fuel_of(tech: str) -> str:
    """Primary energy carrier implied by an industrial route's name."""
    l = tech.lower()
    if "(h2)" in l:                              return "hydrogen"
    if "(el)" in l or "+el" in l or "moe" in l:  return "electricity"
    if "(bm" in l or "(bmw)" in l:               return "biomass"
    if "(ng)" in l or "(ln" in l:                return "natural gas"
    if "(coal)" in l or "bf-bof" in l:           return "coal"
    if "(afm)" in l:                             return "alt. fuel mix"
    if "meoh" in l:                              return "methanol"
    if "scraps" in l:                            return "scrap"
    # Generic sector routes carry no fuel token; the carrier is implicit in the
    # unit's input flows rather than the label.
    if "production-alternative" in l:            return "generic: low-carbon route"
    if "production-reference" in l:              return "generic: reference route"
    if "eu-mix" in l:                            return "generic: EU average mix"
    if "diaphragm" in l:                         return "electricity"
    return "other / unspecified"


def co2_source(tech: str) -> str:
    """Where a tonne entering the CO2 network came from."""
    l = tech.lower()
    if l.startswith("dac"):                       return "direct air capture"
    if "smr" in l or "ref-" in l:                 return "hydrogen (SMR+CC)"
    if "ccgt" in l or "ocgt" in l:                return "power generation"
    if l.startswith("bio"):                       return "bioenergy (BECCS)"
    if "cem2" in l or "lc3" in l:                 return "cement"
    if "nh3" in l:                                return "ammonia"
    if "_gco" in l or "_gfl" in l or "_gfi" in l: return "glass"
    if "bof" in l or "dri" in l:                  return "steel"
    if "meoh" in l or "ft-" in l or ")o-" in l:   return "chemicals / e-fuels"
    if "pe-" in l or "pea-" in l:                 return "plastics"
    if "injection" in l:                          return "injection to storage"
    return "other industry"


def split_name(entity_name: str):
    """'default_report__X_BEC1__realization' -> (tech, region)."""
    n = entity_name.replace("default_report__", "").replace("__realization", "").strip("_")
    m = REGION.search(n)
    if m:
        return REGION.sub("", n), m.group(1)
    return n, None


def unpack(v):
    """Yield (milestone_year:int, value:float) from a Spine parameter value."""
    val = from_database(v["value"], v["type"])
    idx = getattr(val, "indexes", None)
    if idx is None:
        try:
            yield None, float(val)
        except Exception:
            pass
        return
    for i, x in zip(idx, val.values):
        try:
            x = float(x)
        except Exception:
            continue
        s = str(i)
        y = int(s[:4]) if s[:4].isdigit() else None
        yield to_milestone(y), x


def unpack_flow(v, wmap):
    """Like unpack(), but scales each hourly value by its representative-period
    weight so that the sum is an ANNUAL total rather than a raw sum over the
    few modelled days.

    SpineOpt only simulates a handful of representative days per milestone year
    (e.g. 12 Jan / 18 Feb / 19 Aug) and gives each one a `weight` on its
    `representative_period_*` temporal block, counting how many days of the real
    year that day stands for (108.49 / 154.00 / 102.51 -> 365). Flow variables
    are reported RAW, per modelled hour. Summing them unweighted understates the
    year by ~365x AND - worse - silently reweights the mix, because the days do
    not carry equal weight. Every energy number in this report depends on this.

    `wmap` maps 'YYYY-MM-DD' -> weight. A date absent from the map is not part
    of any representative period (SpineOpt emits a couple of zero-valued
    milestone-boundary stamps such as 2040-01-02) and contributes nothing.
    If `wmap` is None no weighting is applied and totals stay raw.
    """
    if wmap is None:
        yield from unpack(v)
        return
    val = from_database(v["value"], v["type"])
    idx = getattr(val, "indexes", None)
    if idx is None:
        try:
            yield None, float(val)
        except Exception:
            pass
        return
    for i, x in zip(idx, val.values):
        try:
            x = float(x)
        except Exception:
            continue
        s = str(i)
        w = wmap.get(s[:10])
        if not w:
            # Outside every representative period. These cells are zero in
            # practice; flag it loudly if that ever stops being true.
            if abs(x) > 1e-9:
                _UNWEIGHTED.append((s, x))
            continue
        y = int(s[:4]) if s[:4].isdigit() else None
        yield to_milestone(y), x * w


# Non-zero flow values found outside any representative period (should be none).
_UNWEIGHTED: list = []


def load_weights(modelpath: str):
    """Build 'YYYY-MM-DD' -> representative-period weight from the model DB.

    Returns None if the model DB is unreadable or declares no representative
    periods, which means the run is not clustered and needs no weighting.
    """
    if not modelpath or not os.path.exists(modelpath):
        return None
    blocks = {}
    try:
        with DatabaseMapping("sqlite:///" + os.path.abspath(modelpath)) as db:
            for v in db.get_parameter_value_items():
                if v["entity_class_name"] != "temporal_block":
                    continue
                par = v["parameter_definition_name"]
                if par not in ("block_start", "block_end", "weight"):
                    continue
                ent = v["entity_name"]
                if not ent.startswith("representative_period"):
                    continue
                val = from_database(v["value"], v["type"])
                blocks.setdefault(ent, {})[par] = getattr(val, "value", val)
    except Exception as e:
        print(f"  WARNING: cannot read temporal weights from {modelpath}: {e}",
              flush=True)
        return None

    wmap = {}
    for name, b in blocks.items():
        start, end, w = b.get("block_start"), b.get("block_end"), b.get("weight")
        if start is None or end is None or w is None:
            continue
        start, end = pd.Timestamp(start), pd.Timestamp(end)
        w = float(w)
        # Representative periods are whole days in this pipeline; expanding to a
        # date->weight map makes the per-hour lookup a single dict hit. Anything
        # not day-aligned would be mis-binned, so refuse rather than guess.
        if start != start.normalize() or end != end.normalize():
            print(f"  WARNING: {name} is not day-aligned ({start} -> {end}); "
                  "weighting skipped", flush=True)
            return None
        for d in pd.date_range(start, end, freq="D", inclusive="left"):
            wmap[d.strftime("%Y-%m-%d")] = w
    return wmap or None


# ---------------------------------------------------------------- extraction
def load(dbpath: str, wmap=None) -> dict:
    """Pull every quantity we plot out of the results DB in one pass.

    `wmap` (see load_weights) scales flow variables from the modelled
    representative days up to annual totals. Stock quantities - capacities,
    investment counts, storage state - are NOT scaled: they are already
    point-in-time values.
    """
    url = "sqlite:///" + os.path.abspath(dbpath)
    inv, fleet, decom, emis, flows, storage, state = [], [], [], [], [], [], []
    co2store, co2net, co2pipe = [], [], []
    supply = []
    objective = {}
    with DatabaseMapping(url) as db:
        ents = {e["id"]: e for e in db.get_entity_items()}
        for v in db.get_parameter_value_items():
            cls = v["entity_class_name"]
            par = v["parameter_definition_name"]
            name = v["entity_name"]

            if cls == "report__model" and par.startswith("objective"):
                objective[par.replace("objective_", "")] = sum(x for _, x in unpack(v))

            elif cls == "report__unit__stochastic_scenario" and par in (
                    "units_invested", "units_invested_available", "units_mothballed"):
                tech, reg = split_name(name)
                rec = dict(tech=tech, region=reg, category=classify(tech),
                           vintage="existing" if "existing" in tech.lower() else "new",
                           cc=is_cc(tech))
                bucket = {"units_invested": inv,
                          "units_invested_available": fleet,
                          "units_mothballed": decom}[par]
                for y, x in unpack(v):
                    if abs(x) > 1e-9:
                        bucket.append(dict(rec, year=y, units=x))

            elif cls == "report__unit__node__direction__stochastic_scenario" and par == "unit_flow":
                e = ents.get(v["entity_id"])
                bn = e["entity_byname"] if e else ()
                if len(bn) < 4:
                    continue
                tech, reg = split_name(bn[1])
                node, _ = split_name(bn[2])
                if bn[2] == "atmosphere":
                    sign = 1.0 if bn[3] == "to_node" else -1.0
                    for y, x in unpack_flow(v, wmap):
                        emis.append(dict(tech=tech, region=reg, year=y,
                                         co2=sign * x, category=classify(tech),
                                         cc=is_cc(tech)))
                elif node in SECTOR_NODES and bn[3] == "to_node":
                    for y, x in unpack_flow(v, wmap):
                        if x > 1e-9:
                            flows.append(dict(tech=tech, region=reg, year=y,
                                              sector=SECTOR_NODES[node], output=x,
                                              cc=is_cc(tech), fuel=fuel_of(tech)))
                elif node in CARRIER_NODES and bn[3] == "to_node":
                    # Energy DELIVERED into a carrier node, i.e. the supply mix.
                    # Only to_node: from_node on the same carrier is consumption,
                    # and summing both would double-count every conversion step.
                    for y, x in unpack_flow(v, wmap):
                        if x > 1e-9:
                            supply.append(dict(tech=tech, region=reg, year=y,
                                               carrier=CARRIER_NODES[node],
                                               energy=x, category=classify(tech),
                                               vintage="existing" if "existing" in tech.lower() else "new"))
                elif bn[2].startswith("CO2-storage"):
                    # CO2 permanently injected into a geological reservoir.
                    if bn[3] == "to_node":
                        for y, x in unpack_flow(v, wmap):
                            if x > 1e-9:
                                co2store.append(dict(reservoir=bn[2], injector=tech,
                                                     region=reg, year=y, co2=x))
                elif node == "CO2":
                    # The CO2 transport network: captured volumes in, utilised
                    # or injected volumes out.
                    role = "captured" if bn[3] == "to_node" else "used / injected"
                    for y, x in unpack_flow(v, wmap):
                        if x > 1e-9:
                            co2net.append(dict(tech=tech, region=reg, year=y,
                                               co2=x, role=role,
                                               source=co2_source(tech)))

            elif (cls == "report__connection__node__direction__stochastic_scenario"
                  and par == "connection_flow"):
                e = ents.get(v["entity_id"])
                bn = e["entity_byname"] if e else ()
                if len(bn) < 4 or "CO2" not in bn[2] or bn[3] != "to_node":
                    continue
                regs = REGION_ANY.findall(bn[1])
                for y, x in unpack_flow(v, wmap):
                    if x > 1e-9:
                        co2pipe.append(dict(connection=bn[1], year=y, co2=x,
                                            origin=regs[0] if regs else None,
                                            dest=regs[1] if len(regs) > 1 else None))

            elif cls == "report__node__stochastic_scenario" and par == "storages_invested":
                node, reg = split_name(name)
                for y, x in unpack(v):
                    if x > 0:
                        storage.append(dict(node=node, region=reg, year=y, units=x))

            elif cls == "report__node__stochastic_scenario" and par == "node_state_longterm":
                node, _ = split_name(name)
                if node == "atmosphere":
                    for y, x in unpack(v):
                        state.append(dict(year=y, level=x))

    return dict(inv=pd.DataFrame(inv), fleet=pd.DataFrame(fleet),
                decom=pd.DataFrame(decom), emis=pd.DataFrame(emis),
                prod=pd.DataFrame(flows), sto=pd.DataFrame(storage),
                atm=pd.DataFrame(state), supply=pd.DataFrame(supply),
                co2store=pd.DataFrame(co2store), co2net=pd.DataFrame(co2net),
                co2pipe=pd.DataFrame(co2pipe),
                obj=pd.Series(objective, dtype=float).sort_values(ascending=False))


# ---------------------------------------------------------------- helpers
def _slug(s: str) -> str:
    """Filesystem-safe fragment. Windows rejects ':' in filenames, and our
    category labels contain them (e.g. 'industry: CCS-equipped'), which
    silently drops the PNG."""
    return re.sub(r"[^0-9A-Za-z]+", "_", s).strip("_").lower()


def _blank(ax, title):
    ax.text(.5, .5, "no data", ha="center", va="center")
    ax.set_title(title)


def _pivot(df, index, columns, values):
    p = df.pivot_table(index=index, columns=columns, values=values,
                       aggfunc="sum").fillna(0)
    return p.loc[:, p.sum().sort_values(ascending=False).index]


def _bar(p, ax, title, ylabel, pct=False, cmap="tab20"):
    if pct:
        tot = p.sum(axis=1).replace(0, np.nan)
        p = p.div(tot, axis=0) * 100
    p.plot(kind="bar", stacked=True, ax=ax, colormap=cmap, width=.6)
    ax.set_title(title); ax.set_ylabel(ylabel); ax.set_xlabel("")
    ax.legend(fontsize=6.5, ncol=2, loc="upper left")
    ax.grid(axis="y", ls=":", alpha=.5)
    ax.tick_params(axis="x", rotation=0)


def _capture_share(prod):
    """Sector x milestone-year table of % output from CC-equipped routes.

    Sectors that produce but never capture must read 0, not NaN, so the
    reindex/fill happens on both the numerator and the result.
    """
    tot = prod.groupby(["sector", "year"])["output"].sum().unstack()
    cc = prod[prod["cc"]].groupby(["sector", "year"])["output"].sum().unstack()
    cc = cc.reindex(index=tot.index, columns=tot.columns).fillna(0.0)
    share = (cc / tot.replace(0, np.nan) * 100).fillna(0.0)
    return share.reindex(columns=[y for y in MILESTONES if y in share.columns])


# ---------------------------------------------------------------- figures
def fig_costs(obj):
    fig, ax = plt.subplots(figsize=(9, 5))
    s = obj[obj.abs() > 0]
    if s.empty:
        _blank(ax, "Objective cost breakdown"); return fig
    tot = s.sum()
    bars = ax.barh(s.index[::-1], s.values[::-1], color="#3b6ea5")
    for b, v in zip(bars, s.values[::-1]):
        ax.text(b.get_width(), b.get_y() + b.get_height() / 2,
                f"  {v:,.0f} ({100*v/tot:.1f}%)", va="center", fontsize=8)
    ax.set_title(f"Objective cost breakdown  (total {tot:,.0f})")
    ax.set_xlabel("cost [model units]"); ax.margins(x=.25)
    fig.tight_layout(); return fig


def fig_fleet_vs_new(fleet, inv, decom):
    """Total installed fleet, with new build and decommissioning alongside."""
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    if fleet.empty:
        for a in axes: _blank(a, "fleet")
        return fig
    _bar(_pivot(fleet, "year", "category", "units"), axes[0],
         "TOTAL installed fleet by category\n(existing stock + new builds)",
         "units available")
    if not inv.empty:
        _bar(_pivot(inv, "year", "category", "units"), axes[1],
             "NEW investment only", "units built")
    else:
        _blank(axes[1], "NEW investment only")
    if not decom.empty:
        _bar(_pivot(decom, "year", "category", "units"), axes[2],
             "Decommissioned / mothballed", "units retired")
    else:
        _blank(axes[2], "Decommissioned")
    fig.tight_layout(); return fig


def fig_fleet_vintage(fleet):
    """How much of the standing fleet is inherited vs newly built."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    if fleet.empty:
        for a in axes: _blank(a, "fleet vintage")
        return fig
    p = _pivot(fleet, "year", "vintage", "units")
    _bar(p, axes[0], "Installed fleet: inherited vs new", "units", cmap="Set2")
    _bar(p, axes[1], "Installed fleet: share inherited vs new", "% of fleet",
         pct=True, cmap="Set2")
    axes[1].set_ylim(0, 100)
    fig.tight_layout(); return fig


def fig_top_tech(fleet, inv, n=18):
    fig, axes = plt.subplots(1, 2, figsize=(15, 7))
    for ax, df, lab, col in ((axes[0], fleet, "installed fleet", "#2c7fb8"),
                             (axes[1], inv, "new investment", "#8c6bb1")):
        if df.empty:
            _blank(ax, lab); continue
        s = df.groupby("tech")["units"].sum().nlargest(n)[::-1]
        ax.barh(s.index, s.values, color=col)
        for i, v in enumerate(s.values):
            ax.text(v, i, f" {v:,.2f}", va="center", fontsize=7)
        ax.set_title(f"Top {n} technologies - {lab}\n(summed over all years)")
        ax.tick_params(axis="y", labelsize=7); ax.margins(x=.18)
        ax.grid(axis="x", ls=":", alpha=.5)
    fig.tight_layout(); return fig


def fig_supply_mix(supply):
    """Energy DELIVERED per carrier, by technology category.

    The counterpart to the fleet plots. Capacity and delivered energy can move
    in OPPOSITE directions, so a capacity-only report can hide the actual
    decarbonisation story.
    """
    if supply.empty:
        fig, ax = plt.subplots(figsize=(10, 5)); _blank(ax, "energy supply mix")
        return fig
    carriers = [c for c in ("electricity", "heat", "hydrogen", "methane", "cooling")
                if c in set(supply["carrier"])]
    n = len(carriers)
    fig, axes = plt.subplots(2, n, figsize=(4.2 * n, 9), squeeze=False)
    for j, car in enumerate(carriers):
        sub = supply[supply["carrier"] == car]
        p = _pivot(sub, "year", "category", "energy")
        _bar(p, axes[0][j], f"{car}: supply mix", "energy delivered")
        _bar(p, axes[1][j], f"{car}: share of supply", "% of supply", pct=True)
        axes[1][j].set_ylim(0, 100)
    fig.suptitle("Energy supply mix by carrier - who actually DELIVERS the energy\n"
                 "(not installed capacity; see the capacity-vs-energy figure)",
                 fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, .95)); return fig


def fig_capacity_vs_energy(fleet, supply):
    """Installed capacity next to delivered energy, for the same categories.

    THE POINT OF THIS FIGURE. Decarbonisation is not only about what gets
    BUILT - it is equally about what gets KEPT and what gets RETIRED. A
    technology can hold flat or shrink in capacity while growing its share of
    delivered energy, or be retained purely to avoid the cost of replacement.
    Reading investment charts alone systematically misses that.
    """
    if fleet.empty or supply.empty:
        fig, ax = plt.subplots(figsize=(10, 5)); _blank(ax, "capacity vs energy")
        return fig
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    _bar(_pivot(fleet, "year", "category", "units"), axes[0],
         "INSTALLED CAPACITY by category\n(units available)", "units", pct=True)
    axes[0].set_ylim(0, 100)
    _bar(_pivot(supply, "year", "category", "energy"), axes[1],
         "DELIVERED ENERGY by category\n(all carriers combined)", "% of energy",
         pct=True)
    axes[1].set_ylim(0, 100)
    fig.suptitle("Capacity share vs energy share - the same categories, two very "
                 "different pictures", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, .94)); return fig


def fig_retained_vs_retired(fleet, inv, decom):
    """What the model CHOSE TO KEEP, versus what it built or retired.

    Retained = standing fleet that is not new build. This is the quantity that
    an investment-only view omits, and it can dominate: keeping an existing
    asset avoids both capital cost and the fixed O&M of its replacement.
    """
    fig, axes = plt.subplots(1, 3, figsize=(17, 5.5))
    if fleet.empty:
        for a in axes: _blank(a, "retained vs retired")
        return fig
    new_by = (inv.groupby(["year", "category"])["units"].sum()
              if not inv.empty else pd.Series(dtype=float))
    tot = fleet.groupby(["year", "category"])["units"].sum()
    retained = (tot - new_by.reindex(tot.index).fillna(0)).clip(lower=0)
    _bar(retained.reset_index().pivot(index="year", columns="category",
                                      values="units").fillna(0),
         axes[0], "RETAINED existing capacity\n(standing fleet minus new build)",
         "units kept")
    if not inv.empty:
        _bar(_pivot(inv, "year", "category", "units"), axes[1],
             "NEW build", "units built")
    else:
        _blank(axes[1], "NEW build")
    if not decom.empty:
        _bar(_pivot(decom, "year", "category", "units"), axes[2],
             "RETIRED / mothballed", "units retired")
    else:
        _blank(axes[2], "RETIRED / mothballed")
    fig.suptitle("Decarbonisation is a choice about KEEPING and RETIRING, "
                 "not only about BUILDING", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, .93)); return fig


def fig_emissions(emis):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    if emis.empty:
        for a in axes: _blank(a, "emissions")
        return fig
    _bar(_pivot(emis, "year", "category", "co2"), axes[0],
         "CO2 to atmosphere by category\n(sum over 24 h representative day)",
         "CO2 per representative day")
    net = emis.groupby("year")["co2"].sum()
    axes[1].bar([str(i) for i in net.index], net.values,
                color=["#c0392b" if v > 0 else "#27ae60" for v in net.values],
                width=.5)
    for i, v in enumerate(net.values):
        axes[1].text(i, v, f"{v:,.1f}", ha="center",
                     va="bottom" if v >= 0 else "top", fontsize=9)
    axes[1].axhline(0, color="k", lw=.8)
    axes[1].set_title("NET CO2 to atmosphere\n(emissions minus DAC/removals)")
    axes[1].set_ylabel("CO2 per representative day")
    axes[1].grid(axis="y", ls=":", alpha=.5)
    fig.tight_layout(); return fig


def fig_atm(atm):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    if atm.empty:
        _blank(ax, "atmosphere"); return fig
    s = atm.groupby("year")["level"].max()
    ax.bar([str(i) for i in s.index], s.values, color="#c0392b", width=.5)
    for i, v in enumerate(s.values):
        ax.text(i, v, f"{v:,.0f}", ha="center", va="bottom", fontsize=9)
    ax.set_title("Cumulative CO2 budget used (atmosphere node_state_longterm)")
    ax.set_ylabel("level"); ax.grid(axis="y", ls=":", alpha=.5)
    fig.tight_layout(); return fig


# ------------------------------------------------- industry decarbonisation
def fig_industry_routes(prod):
    fig, axes = plt.subplots(1, 2, figsize=(15, 5.5))
    if prod.empty:
        for a in axes: _blank(a, "industrial output")
        return fig
    _bar(_pivot(prod, "year", "sector", "output"), axes[0],
         "Industrial output by sector", "output per rep. day")
    d = prod.copy()
    d["route"] = np.where(d["cc"], "with carbon capture", "unabated")
    _bar(_pivot(d, "year", "route", "output"), axes[1],
         "Industrial output: abated vs unabated", "% of output",
         pct=True, cmap="RdYlGn_r")
    axes[1].set_ylim(0, 100)
    fig.tight_layout(); return fig


def fig_industry_capture_by_sector(prod):
    fig, ax = plt.subplots(figsize=(11, 5.5))
    if prod.empty:
        _blank(ax, "capture rate by sector"); return fig
    share = _capture_share(prod)
    share = share.loc[share.mean(axis=1).sort_values(ascending=False).index]
    share.plot(kind="bar", ax=ax, colormap="viridis", width=.75)
    ax.set_title("Carbon-capture penetration by industrial sector")
    ax.set_ylabel("% of sector output from CC-equipped routes")
    ax.set_xlabel(""); ax.set_ylim(0, 100)
    ax.legend(title="year", fontsize=8)
    ax.grid(axis="y", ls=":", alpha=.5)
    ax.tick_params(axis="x", rotation=30, labelsize=8)
    for lab in ax.get_xticklabels():
        lab.set_ha("right")
    fig.tight_layout(); return fig


def fig_sector_heatmap(prod):
    fig, ax = plt.subplots(figsize=(8, 6))
    if prod.empty:
        _blank(ax, "capture heatmap"); return fig
    share = _capture_share(prod)
    share = share.loc[share.mean(axis=1).sort_values().index]
    im = ax.imshow(share.values, cmap="RdYlGn", vmin=0, vmax=100, aspect="auto")
    ax.set_xticks(range(len(share.columns)))
    ax.set_xticklabels([str(c) for c in share.columns])
    ax.set_yticks(range(len(share.index)))
    ax.set_yticklabels(share.index, fontsize=8)
    for i in range(share.shape[0]):
        for j in range(share.shape[1]):
            ax.text(j, i, f"{share.values[i, j]:.0f}%", ha="center",
                    va="center", fontsize=8)
    ax.set_title("CC penetration by sector and year (%)")
    fig.colorbar(im, ax=ax, fraction=.04)
    fig.tight_layout(); return fig


def fig_industry_fuel(prod):
    fig, axes = plt.subplots(1, 2, figsize=(15, 5.5))
    if prod.empty:
        for a in axes: _blank(a, "industrial fuel mix")
        return fig
    p = _pivot(prod, "year", "fuel", "output")
    _bar(p, axes[0], "Industrial output by energy carrier",
         "output per rep. day", cmap="tab20b")
    _bar(p, axes[1], "Industrial fuel mix (share)", "% of output", pct=True,
         cmap="tab20b")
    axes[1].set_ylim(0, 100)
    fig.tight_layout(); return fig


def fig_industry_top_routes(prod, n=18):
    fig, ax = plt.subplots(figsize=(10, 7))
    if prod.empty:
        _blank(ax, "process routes"); return fig
    g = prod.groupby(["tech", "cc"])["output"].sum().reset_index()
    g = g.nlargest(n, "output").iloc[::-1]
    ax.barh(g["tech"], g["output"],
            color=["#27ae60" if c else "#c0392b" for c in g["cc"]])
    for i, v in enumerate(g["output"].values):
        ax.text(v, i, f" {v:,.1f}", va="center", fontsize=7)
    ax.set_title(f"Top {n} industrial process routes by output\n"
                 "green = carbon capture, red = unabated")
    ax.tick_params(axis="y", labelsize=7); ax.margins(x=.18)
    ax.grid(axis="x", ls=":", alpha=.5)
    fig.tight_layout(); return fig


# ------------------------------------------------------------ CO2 handling
def fig_co2_fate(co2net, co2store, emis):
    """Where does captured carbon come from, and does it balance?"""
    fig, axes = plt.subplots(1, 2, figsize=(15, 5.5))
    if co2net.empty:
        for a in axes: _blank(a, "CO2 network")
        return fig
    cap = co2net[co2net.role == "captured"]
    _bar(_pivot(cap, "year", "source", "co2"), axes[0],
         "CO2 captured into the CO2 network, by origin",
         "CO2 per representative day", cmap="tab20c")
    rows = {}
    for y in MILESTONES:
        rows[y] = {
            "captured": cap[cap.year == y]["co2"].sum(),
            "injected to geological storage":
                co2store[co2store.year == y]["co2"].sum() if len(co2store) else 0.0,
            "emitted to atmosphere (net)":
                emis[emis.year == y]["co2"].sum() if len(emis) else 0.0,
        }
    p = pd.DataFrame(rows).T
    p.plot(kind="bar", ax=axes[1], width=.72,
           color=["#2980b9", "#8e44ad", "#c0392b"])
    axes[1].set_title("Carbon balance: captured / stored / emitted")
    axes[1].set_ylabel("CO2 per representative day")
    axes[1].axhline(0, color="k", lw=.8)
    axes[1].legend(fontsize=7.5); axes[1].grid(axis="y", ls=":", alpha=.5)
    axes[1].tick_params(axis="x", rotation=0)
    fig.tight_layout(); return fig


def fig_co2_storage(co2store):
    """Injection into each geological reservoir, and who does the injecting."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    if co2store.empty:
        for a in axes:
            _blank(a, "no CO2 reached geological storage")
        return fig
    _bar(_pivot(co2store, "year", "reservoir", "co2"), axes[0],
         "CO2 injected into geological storage, by reservoir",
         "CO2 per representative day", cmap="viridis")
    g = co2store.groupby(["injector", "region"])["co2"].sum().sort_values()
    lbl = [f"{i}  [{r}]" for i, r in g.index]
    axes[1].barh(lbl, g.values, color="#8e44ad")
    for i, v in enumerate(g.values):
        axes[1].text(v, i, f" {v:,.2f}", va="center", fontsize=8)
    axes[1].set_title("Injection units (all years)\nCO2 routed to offshore reservoirs")
    axes[1].tick_params(axis="y", labelsize=8); axes[1].margins(x=.2)
    axes[1].grid(axis="x", ls=":", alpha=.5)
    fig.tight_layout(); return fig


def fig_co2_sankey(co2net, co2store, emis):
    """Source -> network -> fate flow diagram for the final milestone year."""
    fig, ax = plt.subplots(figsize=(11, 6.5))
    ax.set_axis_off()
    if co2net.empty:
        _blank(ax, "CO2 flows"); return fig
    year = max(MILESTONES)
    cap = co2net[(co2net.role == "captured") & (co2net.year == year)]
    if cap.empty:
        _blank(ax, f"no CO2 captured in {year}"); return fig
    src = cap.groupby("source")["co2"].sum().sort_values(ascending=False)
    stored = co2store[co2store.year == year]["co2"].sum() if len(co2store) else 0.0
    total = src.sum()

    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    cmap = plt.get_cmap("tab20c")
    y0 = .93
    for i, (name, val) in enumerate(src.items()):
        share = val / total
        h = share * .82
        ax.add_patch(plt.Rectangle((.04, y0 - h), .17, h,
                                   color=cmap(i % 20), ec="white"))
        ax.text(.225, y0 - h / 2, f"{name}\n{val:,.1f}", va="center", fontsize=8)
        ax.plot([.21, .58], [y0 - h / 2, .52], color=cmap(i % 20),
                lw=max(1.0, share * 26), alpha=.45, solid_capstyle="round")
        y0 -= h + .012

    ax.add_patch(plt.Rectangle((.58, .30), .09, .44, color="#34495e", ec="white"))
    ax.text(.625, .76, "CO2 network", ha="center", fontsize=9, weight="bold")

    fates = [("geological storage", stored, "#8e44ad"),
             ("utilised / other", max(0.0, total - stored), "#16a085")]
    y0 = .74
    for name, val, col in fates:
        if val <= 1e-9:
            continue
        h = (val / total) * .44
        ax.add_patch(plt.Rectangle((.80, y0 - h), .13, h, color=col, ec="white"))
        ax.text(.94, y0 - h / 2, f"{name}\n{val:,.1f}", va="center", fontsize=8.5)
        ax.plot([.67, .80], [.52, y0 - h / 2], color=col,
                lw=max(1.0, (val / total) * 26), alpha=.5, solid_capstyle="round")
        y0 -= h + .02

    net = emis[emis.year == year]["co2"].sum() if len(emis) else 0.0
    ax.set_title(f"CO2 flows in {year}: capture sources -> network -> fate\n"
                 f"total captured {total:,.1f} | injected {stored:,.1f} | "
                 f"net to atmosphere {net:,.1f}", fontsize=11)
    fig.tight_layout(); return fig


# ---------------------------------------------------------------- maps
def load_geo():
    try:
        import geopandas as gpd
    except ImportError:
        return None
    if not os.path.exists(GEOJSON):
        return None
    return gpd.read_file(GEOJSON).set_index("id")


def map_panels(gdf, table, valcol, title, cmap, fmt="{:,.1f}"):
    years = [y for y in MILESTONES if y in set(table["year"].dropna())]
    if not years:
        years = sorted(table["year"].dropna().unique())
    fig, axes = plt.subplots(1, max(1, len(years)),
                             figsize=(4.2 * max(1, len(years)), 5.2))
    axes = np.atleast_1d(axes)
    piv = table.pivot_table(index="region", columns="year", values=valcol,
                            aggfunc="sum").reindex(gdf.index).fillna(0)
    vmax = float(np.nanmax(piv.values)) if piv.size else 1.0
    vmin = min(0.0, float(np.nanmin(piv.values)) if piv.size else 0.0)
    vmax = vmax if vmax > vmin else vmin + 1.0
    for ax, y in zip(axes, years):
        g = gdf.copy()
        g["v"] = piv[y] if y in piv.columns else 0.0
        g.plot(column="v", ax=ax, cmap=cmap, vmin=vmin, vmax=vmax,
               edgecolor="white", linewidth=.6)
        for rid, row in g.iterrows():
            c = row.geometry.representative_point()
            ax.annotate(f"{rid}\n{fmt.format(row['v'])}", (c.x, c.y),
                        ha="center", fontsize=5.5)
        ax.set_title(str(int(y))); ax.set_axis_off()
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin, vmax))
    fig.colorbar(sm, ax=axes.tolist(), fraction=.03, pad=.02)
    fig.suptitle(title, fontsize=12)
    return fig


def map_co2_chain(gdf, co2net, co2pipe, co2store):
    """Capture per region as choropleth, with pipeline flows drawn as arrows.

    Regions hosting an injection unit are ringed, so one map shows the whole
    chain: where carbon is caught, how it moves, where it goes underground.
    """
    fig, axes = plt.subplots(1, len(MILESTONES),
                             figsize=(4.6 * len(MILESTONES), 5.6))
    axes = np.atleast_1d(axes)
    cap = co2net[co2net.role == "captured"] if len(co2net) else pd.DataFrame()
    piv = (cap.pivot_table(index="region", columns="year", values="co2",
                           aggfunc="sum").reindex(gdf.index).fillna(0)
           if len(cap) else pd.DataFrame(index=gdf.index))
    vmax = float(np.nanmax(piv.values)) if piv.size else 1.0
    vmax = vmax if vmax > 0 else 1.0
    inj_regions = set(co2store["region"].dropna()) if len(co2store) else set()
    cent = {r: g.representative_point() for r, g in gdf.geometry.items()}

    for ax, y in zip(axes, MILESTONES):
        g = gdf.copy()
        g["v"] = piv[y] if y in getattr(piv, "columns", []) else 0.0
        g.plot(column="v", ax=ax, cmap="YlOrRd", vmin=0, vmax=vmax,
               edgecolor="white", linewidth=.6)
        for rid, row in g.iterrows():
            c = cent[rid]
            ax.annotate(f"{rid}\n{row['v']:,.1f}", (c.x, c.y), ha="center",
                        fontsize=5.5)
            if rid in inj_regions:
                ax.plot(c.x, c.y, "o", ms=13, mfc="none", mec="#8e44ad", mew=2)
        if len(co2pipe):
            pp = co2pipe[co2pipe.year == y]
            mx = pp["co2"].max() if len(pp) else 0
            for _, r in pp.iterrows():
                if (not r["origin"] or not r["dest"]
                        or r["origin"] not in cent or r["dest"] not in cent):
                    continue
                a, b = cent[r["origin"]], cent[r["dest"]]
                ax.annotate("", xy=(b.x, b.y), xytext=(a.x, a.y),
                            arrowprops=dict(arrowstyle="-|>", color="#2c3e50",
                                            lw=1 + 3 * (r["co2"] / mx if mx else 0),
                                            alpha=.85, shrinkA=6, shrinkB=6))
        ax.set_title(str(y)); ax.set_axis_off()
    sm = plt.cm.ScalarMappable(cmap="YlOrRd", norm=plt.Normalize(0, vmax))
    fig.colorbar(sm, ax=axes.tolist(), fraction=.03, pad=.02)
    fig.suptitle("CO2 capture by region (colour), pipeline transport (arrows)\n"
                 "purple ring = region hosting an injection point to offshore storage",
                 fontsize=11)
    return fig


# ------------------------------------------------------------- run metadata
def _dur(v):
    """Render a Spine Duration / relativedelta compactly (e.g. '1h', '365D')."""
    for attr, suffix in (("hours", "h"), ("days", "D"), ("months", "M"),
                         ("years", "y"), ("minutes", "min")):
        n = getattr(v, attr, 0) or 0
        if n:
            return f"{int(n)}{suffix}"
    return str(v)


def _flatten(val, prefix=""):
    """Flatten a (possibly nested) Spine Map into {label: value}."""
    out = {}
    if hasattr(val, "indexes"):
        for i, x in zip(val.indexes, val.values):
            key = f"{prefix}{i}"
            if hasattr(x, "indexes"):
                out.update(_flatten(x, key + " / "))
            else:
                out[key] = x
    else:
        out[prefix.rstrip(" /")] = val
    return out


def load_meta(dbpath: str, modelpath: str) -> dict:
    """Collect run provenance: solver status, timings, temporal + CO2 setup.

    Best-effort throughout: a missing model DB must not stop the report.
    """
    meta = {"results DB": os.path.abspath(dbpath)}
    try:
        with DatabaseMapping("sqlite:///" + os.path.abspath(dbpath)) as db:
            for v in db.get_parameter_value_items():
                par = v["parameter_definition_name"]
                if par == "solution_stats":
                    for k, x in _flatten(from_database(v["value"], v["type"])).items():
                        meta[k.replace('(model = "', "").replace('",)', "")] = x
                elif par == "total_costs":
                    meta["total_costs"] = sum(x for _, x in unpack(v))
    except Exception as e:
        meta["results DB error"] = str(e)

    if not os.path.exists(modelpath):
        return meta
    meta["model DB"] = os.path.abspath(modelpath)
    try:
        with DatabaseMapping("sqlite:///" + os.path.abspath(modelpath)) as db:
            blocks, co2 = {}, None
            for v in db.get_parameter_value_items():
                cls, par, ent = (v["entity_class_name"],
                                 v["parameter_definition_name"], v["entity_name"])
                if cls == "model" and par in ("model_start", "model_end",
                                              "discount_rate", "solver_mip"):
                    val = from_database(v["value"], v["type"])
                    meta[par] = getattr(val, "value", val)
                elif cls == "temporal_block" and par in ("block_start", "block_end",
                                                         "resolution", "weight"):
                    val = from_database(v["value"], v["type"])
                    blocks.setdefault(ent, {})[par] = getattr(val, "value", val)
                elif (ent == "atmosphere"
                      and par == "storage_investment_count_max_cumulative"):
                    co2 = from_database(v["value"], v["type"])

            rep = {k: b for k, b in blocks.items() if k.startswith("representative")}
            ops = {k: b for k, b in blocks.items() if k.startswith("operations")}
            meta["temporal: operational blocks"] = ", ".join(sorted(ops)) or "n/a"
            meta["temporal: representative periods"] = (
                f"{len(rep)} total  ({len(rep) // max(1, len(ops))} per milestone year)"
                if ops else str(len(rep)))
            for k in sorted(rep):
                b = rep[k]
                start, end = b.get("block_start"), b.get("block_end")
                hours = ""
                try:
                    hours = f"  ({int((end - start).total_seconds() // 3600)} h)"
                except Exception:
                    pass
                w = b.get("weight")
                wtxt = f"  x{float(w):.2f} days" if w is not None else ""
                meta[f"   {k}"] = (f"{start} -> {end}"
                                   f"  @ {_dur(b.get('resolution'))}{hours}{wtxt}")
            if co2 is not None:
                for i, x in zip(co2.indexes, co2.values):
                    y = to_milestone(int(str(i)[:4]))
                    meta[f"CO2 cap {y}"] = f"{float(x):,.1f}"
    except Exception as e:
        meta["model DB error"] = str(e)
    return meta


def fig_cover(meta, obj, fleet, inv, prod, co2store, tag):
    """Front page: what was run, how, and the headline numbers."""
    fig = plt.figure(figsize=(8.27, 11.69))          # A4 portrait
    fig.text(.5, .955, "IC1 Industrial Case Study", ha="center",
             fontsize=20, weight="bold")
    fig.text(.5, .930, "Mopo project - Belgium & Netherlands", ha="center",
             fontsize=13, color="#444")
    fig.text(.5, .910, f"results: {tag}", ha="center", fontsize=9,
             color="#777", style="italic")
    fig.text(.5, .894, "generated " + pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
             ha="center", fontsize=8, color="#777")
    fig.patches.append(plt.Rectangle((.08, .888), .84, .0025,
                                     transform=fig.transFigure,
                                     color="#3b6ea5", zorder=3))

    def block(y, title, rows):
        fig.text(.09, y, title, fontsize=11, weight="bold", color="#3b6ea5")
        y -= .020
        for k, v in rows:
            fig.text(.11, y, str(k), fontsize=8.5, color="#333")
            fig.text(.50, y, str(v), fontsize=8.5, weight="bold")
            y -= .0165
        return y - .012

    status = meta.get("termination_status / capacity_planning", "n/a")
    y = block(.862, "Run status", [
        ("termination status", status),
        ("objective / total costs", f"{meta.get('total_costs', float('nan')):,.0f}"),
        ("SpineOpt version", meta.get("SpineOpt_version", "n/a")),
        ("solver", meta.get("solver_mip", "n/a")),
        ("build time", meta.get("build_time / capacity_planning", "n/a")),
        ("solve time", meta.get("solve_time / capacity_planning", "n/a")),
        ("total elapsed", meta.get("elapsed_time", "n/a")),
    ])

    rep_rows = [(k.strip(), v) for k, v in meta.items() if k.startswith("   represent")]
    y = block(y, "Time representation", [
        ("model horizon", f"{meta.get('model_start','?')}  ->  {meta.get('model_end','?')}"),
        ("milestone years", ", ".join(str(m) for m in MILESTONES)),
        ("representative periods", meta.get("temporal: representative periods", "n/a")),
        ("discount rate", meta.get("discount_rate", "n/a")),
    ] + rep_rows)

    co2_rows = [(k, v) for k, v in meta.items() if k.startswith("CO2 cap")]
    y = block(y, "CO2 targets (cumulative budget, 'atmosphere' storage node)",
              co2_rows or [("no cap found", "-")])

    y = block(y, "Geographical resolution", [
        ("regions", "17 sub-national polygons (BEC1-BEC8, NLC1-NLC9)"),
        ("countries", "Belgium, Netherlands (+ exogenous neighbours)"),
        ("geometry", GEOJSON),
    ])

    tot_new = inv["units"].sum() if len(inv) else 0.0
    rows = [("technologies tracked", f"{fleet['tech'].nunique() if len(fleet) else 0}"),
            ("total new investment (all years)", f"{tot_new:,.2f} units")]
    if len(fleet):
        pv = fleet.pivot_table(index="year", columns="vintage",
                               values="units", aggfunc="sum").fillna(0)
        for yr in pv.index:
            rows.append((f"fleet {int(yr)}  (existing / new)",
                         f"{pv.loc[yr].get('existing', 0.0):,.1f}  /  "
                         f"{pv.loc[yr].get('new', 0.0):,.1f}"))
    if len(prod):
        for yr in _capture_share(prod).columns:
            w = prod[prod.year == yr]
            tot = w["output"].sum()
            cc = w[w.cc]["output"].sum()
            rows.append((f"industrial output w/ capture {int(yr)}",
                         f"{(100*cc/tot if tot else 0):.1f}%"))
    if len(co2store):
        g = co2store.groupby("year")["co2"].sum()
        for yr, val in g.items():
            rows.append((f"CO2 injected to geological storage {int(yr)}",
                         f"{val:,.1f}"))
    y = block(y, "Headline results", rows)

    if len(obj):
        s = obj[obj.abs() > 0]
        tot = s.sum()
        y = block(y, "Cost composition",
                  [(k, f"{v:,.0f}   ({100*v/tot:.1f}%)") for k, v in s.items()])

    fig.text(.5, .030,
             "Figures follow on the next pages. Values are per 24 h representative day\n"
             "unless stated otherwise; see docs/TIME_REPRESENTATION.md for scaling.",
             ha="center", fontsize=7.5, color="#666")
    return fig


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("db", nargs="?", default=DEFAULT_DB)
    ap.add_argument("-o", "--outdir", default="reports")
    ap.add_argument("-m", "--model", default=MODEL_DB,
                    help="model DB used for temporal / CO2 metadata on the cover, "
                         "and for the representative-period weights")
    ap.add_argument("--raw", action="store_true",
                    help="do NOT scale flows by representative-period weight; "
                         "report raw sums over modelled hours (debugging only)")
    a = ap.parse_args()

    os.makedirs(a.outdir, exist_ok=True)
    tag = os.path.splitext(os.path.basename(a.db))[0]

    wmap = None if a.raw else load_weights(a.model)
    if a.raw:
        print("  --raw: representative-period weighting DISABLED "
              "(flows are per-modelled-hour sums, NOT annual)", flush=True)
    elif wmap:
        days = len(wmap) // max(1, len(MILESTONES))
        print(f"  representative-period weighting ON: {len(wmap)} modelled days "
              f"(~{days}/milestone), weights sum to "
              f"{sum(set(wmap.values())) if len(set(wmap.values()))==days else '?'}"
              " per year", flush=True)
    else:
        print("  WARNING: no representative-period weights found -> flows are "
              "RAW sums over modelled hours, not annual totals. Pass -m <model.sqlite>.",
              flush=True)

    print(f"reading {a.db} ...", flush=True)
    d = load(a.db, wmap)
    inv, fleet, decom = d["inv"], d["fleet"], d["decom"]
    emis, prod, sto, atm, obj = d["emis"], d["prod"], d["sto"], d["atm"], d["obj"]
    co2store, co2net, co2pipe = d["co2store"], d["co2net"], d["co2pipe"]
    supply = d["supply"]
    print(f"  fleet={len(fleet)} new={len(inv)} decom={len(decom)} "
          f"emis={len(emis)} industry={len(prod)} storage={len(sto)} "
          f"co2net={len(co2net)} co2stored={len(co2store)} pipes={len(co2pipe)} "
          f"supply={len(supply)}",
          flush=True)

    for nm, df in (("fleet", fleet), ("investments", inv),
                   ("decommissioned", decom), ("emissions", emis),
                   ("industry_output", prod), ("storage", sto),
                   ("energy_supply", supply),
                   ("atmosphere", atm), ("co2_network", co2net),
                   ("co2_geological_storage", co2store),
                   ("co2_pipelines", co2pipe)):
        if len(df):
            df.to_csv(os.path.join(a.outdir, f"{tag}_{nm}.csv"), index=False)
    obj.to_csv(os.path.join(a.outdir, f"{tag}_objective.csv"), header=["value"])

    meta = load_meta(a.db, a.model)
    if a.raw:
        meta["flow weighting"] = ("DISABLED (--raw): flows are raw sums over "
                                  "modelled hours, NOT annual totals")
    elif wmap:
        meta["flow weighting"] = (
            f"representative-period weights applied to all flows "
            f"({len(wmap)} modelled days -> annual totals)")
    else:
        meta["flow weighting"] = ("NONE FOUND: flows are raw sums over modelled "
                                  "hours, NOT annual totals")
    if _UNWEIGHTED:
        meta["flow weighting warning"] = (
            f"{len(_UNWEIGHTED)} non-zero flow values fell outside every "
            f"representative period and were DROPPED "
            f"(first: {_UNWEIGHTED[0][0]} = {_UNWEIGHTED[0][1]:.6g})")
        print("  " + meta["flow weighting warning"], flush=True)
    pd.Series({k: str(v) for k, v in meta.items()}).to_csv(
        os.path.join(a.outdir, f"{tag}_run_metadata.csv"), header=["value"])

    figs = [
        ("cover", fig_cover(meta, obj, fleet, inv, prod, co2store, tag)),
        ("costs", fig_costs(obj)),
        ("fleet_vs_new", fig_fleet_vs_new(fleet, inv, decom)),
        ("fleet_vintage", fig_fleet_vintage(fleet)),
        ("supply_mix", fig_supply_mix(supply)),
        ("capacity_vs_energy", fig_capacity_vs_energy(fleet, supply)),
        ("retained_vs_retired", fig_retained_vs_retired(fleet, inv, decom)),
        ("top_tech", fig_top_tech(fleet, inv)),
        ("emissions", fig_emissions(emis)),
        ("co2_budget", fig_atm(atm)),
        ("co2_fate", fig_co2_fate(co2net, co2store, emis)),
        ("co2_storage", fig_co2_storage(co2store)),
        ("co2_sankey", fig_co2_sankey(co2net, co2store, emis)),
        ("industry_routes", fig_industry_routes(prod)),
        ("industry_capture", fig_industry_capture_by_sector(prod)),
        ("industry_heatmap", fig_sector_heatmap(prod)),
        ("industry_fuel", fig_industry_fuel(prod)),
        ("industry_top_routes", fig_industry_top_routes(prod)),
    ]

    gdf = load_geo()
    if gdf is None:
        print("  (geopandas / IC1.geojson unavailable -> skipping maps)")
    else:
        if len(co2net):
            figs.append(("map_co2_chain",
                         map_co2_chain(gdf, co2net, co2pipe, co2store)))
        if len(fleet):
            figs.append(("map_fleet", map_panels(
                gdf, fleet.dropna(subset=["region"]), "units",
                "TOTAL installed fleet by region (existing + new)", "YlGnBu")))
        if len(inv):
            t = inv.dropna(subset=["region"])
            figs.append(("map_new", map_panels(
                gdf, t, "units", "NEW investment by region", "BuPu")))
            for cat, cmap in (("industry: CCS-equipped", "Purples"),
                              ("CO2 removal (DAC)", "Greens"),
                              ("wind onshore", "Blues"),
                              ("electrolysis", "Oranges")):
                sub = t[t["category"] == cat]
                if len(sub):
                    figs.append((f"map_{_slug(cat)}", map_panels(
                        gdf, sub, "units", f"New investment - {cat}", cmap)))
        if len(emis):
            figs.append(("map_co2", map_panels(
                gdf, emis.dropna(subset=["region"]), "co2",
                "Net CO2 to atmosphere by region", "Reds")))
        if len(prod):
            cc = prod[prod["cc"]].dropna(subset=["region"])
            if len(cc):
                figs.append(("map_capture", map_panels(
                    gdf, cc, "output",
                    "Industrial output from CC-equipped routes by region",
                    "Purples")))

    pdf_path = os.path.join(a.outdir, f"{tag}_report.pdf")
    with PdfPages(pdf_path) as pdf:
        for i, (nm, f) in enumerate(figs):
            # The cover is laid out in figure coordinates on a full A4 page:
            # 'tight' would crop the margins away and wreck the spacing.
            bbox = None if nm == "cover" else "tight"
            pdf.savefig(f, bbox_inches=bbox)
            f.savefig(os.path.join(a.outdir, f"{tag}_{i:02d}_{_slug(nm)}.png"),
                      dpi=140, bbox_inches=bbox)
            plt.close(f)
    print(f"wrote {pdf_path} ({len(figs)} pages: 1 cover + {len(figs)-1} figures)",
          flush=True)


if __name__ == "__main__":
    main()
