"""Domain logic for the IC1 summer CO2-rebuild run.

Everything here is derived from the two SQLite databases; nothing about the
scenario is hard-coded except the node that represents the atmosphere.
"""
from __future__ import annotations

import os
import re

import numpy as np
import pandas as pd

import spine_io as sio

ATMOSPHERE = "atmosphere"
CO2_NODE_RE = r"CO2_[A-Z0-9]+"
CO2_STORE_RE = r"CO2-storage-.*"

# Carrier buckets used to decide whether a removal credit is legitimate.
# Edit these two lists if the scenario's carrier naming changes.
FOSSIL_CARRIERS = ("CH4", "fossil-CH4", "coal", "crude", "HC", "bunker-HC",
                   "U-92", "MeOH", "global-H2", "LNG", "waste")
BIOGENIC_CARRIERS = ("bio", "biomass-stock")


# --------------------------------------------------------------------------
# temporal structure
# --------------------------------------------------------------------------
def temporal_structure(input_con):
    """Milestone label per calendar year, plus the representative-period weights.

    The 2040 milestone is modelled on calendar 2041 in this database, so a
    plain `ts.year` is not a usable period key.

    Returns `(year_to_milestone, rep_weight)` where `rep_weight` is a **dict**
    mapping the date of each representative day to its own weight. A run with
    several representative days gives each a different weight (they must sum to
    365 per milestone year), so a single scalar would silently mis-scale every
    day but the first. `annual_weight()` collapses it when a scalar is needed.
    """
    df, _ = sio.parameter_frame(input_con, ["block_start", "block_end", "weight", "resolution"])
    blocks = {}
    for row in df.itertuples(index=False):
        d = row._asdict()
        blocks.setdefault(d["entity_name"], {})[d["param"]] = d["value"]

    rep_weight = {}
    year_to_milestone = {}
    for name, p in blocks.items():
        m = re.search(r"(\d{4})", name)
        if not m:
            continue
        milestone = int(m.group(1))
        if name.startswith("representative_period"):
            start = _dt(p.get("block_start"))
            w = _num(p.get("weight"))
            if start is not None:
                year_to_milestone[start.year] = milestone
                if w is not None:
                    rep_weight[start.normalize()] = w
        elif name.startswith("operations_"):
            start, end = _dt(p.get("block_start")), _dt(p.get("block_end"))
            if start is not None and end is not None:
                for y in range(start.year, end.year + 1):
                    year_to_milestone.setdefault(y, milestone)
    return year_to_milestone, (rep_weight or {None: 1.0})


def annual_weight(rep_weight, year_to_milestone=None):
    """Total weight covering one milestone year - normally 365.

    Accepts either the dict returned by `temporal_structure` or a bare scalar
    from older callers.
    """
    if not isinstance(rep_weight, dict):
        return float(rep_weight)
    if year_to_milestone:
        per = {}
        for ts, w in rep_weight.items():
            if ts is None:
                continue
            per.setdefault(year_to_milestone.get(ts.year, ts.year), 0.0)
            per[year_to_milestone.get(ts.year, ts.year)] += w
        if per:
            # every milestone should carry the same total; take the common value
            return float(max(per.values()))
    vals = [w for k, w in rep_weight.items() if k is not None]
    return float(sum(vals)) if vals else 1.0


def _dt(raw):
    if raw is None:
        return None
    import json
    try:
        obj = json.loads(raw)
    except (TypeError, ValueError):
        return pd.to_datetime(raw, errors="coerce")
    return pd.to_datetime(obj.get("data", obj) if isinstance(obj, dict) else obj, errors="coerce")


def _num(raw):
    if raw is None:
        return None
    try:
        return float(raw)
    except (TypeError, ValueError):
        pass
    import json
    try:
        obj = json.loads(raw)
    except (TypeError, ValueError):
        return None
    try:
        return float(obj.get("data", obj) if isinstance(obj, dict) else obj)
    except (TypeError, ValueError):
        return None


# --------------------------------------------------------------------------
# flows
# --------------------------------------------------------------------------
def unit_flows(results_con, year_to_milestone, rep_weight):
    """Hourly unit flows restricted to the representative days, annualised.

    `value_hourly` is the raw solver value; `value_annual` is that value times
    the representative-period weight. Summing `value_annual` over the 24 hours
    of a representative day gives the annual total for the milestone year.
    """
    df = sio.timeseries(results_con, ["unit_flow"],
                        {"dim1": "unit", "dim2": "node", "dim3": "direction"})
    return _finish(df, year_to_milestone, rep_weight)


def connection_flows(results_con, year_to_milestone, rep_weight):
    df = sio.timeseries(results_con, ["connection_flow"],
                        {"dim1": "connection", "dim2": "node", "dim3": "direction"})
    return _finish(df, year_to_milestone, rep_weight)


def _finish(df, year_to_milestone, rep_weight):
    df = df.dropna(subset=["ts"]).copy()
    df["period"] = df["ts"].dt.year.map(year_to_milestone)
    df = df.dropna(subset=["period"])
    df["period"] = df["period"].astype(int)
    # Representative days carry 24 hourly stamps; investment-block boundaries are
    # lone midnight stamps standing for a whole year and must not be summed in.
    stamps_per_day = df.groupby(df["ts"].dt.normalize())["ts"].transform("nunique")
    df = df[stamps_per_day > 1].copy()
    df["hour"] = df["ts"].dt.hour
    df = df.rename(columns={"value": "value_hourly"})
    # Each representative day carries its own weight. Using a single scalar would
    # mis-scale every day but the first whenever a run has more than one.
    if isinstance(rep_weight, dict):
        day = df["ts"].dt.normalize()
        w = day.map(rep_weight)
        if w.isna().any():
            missing = sorted(day[w.isna()].unique())[:3]
            raise ValueError(
                f"no representative-period weight for {missing} - "
                "temporal_structure did not see these days")
        df["weight"] = w.astype(float)
    else:
        df["weight"] = float(rep_weight)
    df["value_annual"] = df["value_hourly"] * df["weight"]
    return df.drop(columns=["param"], errors="ignore")


def region_of(name):
    m = re.search(r"_((?:NL|BE)C\d+)$", str(name))
    if m:
        return m.group(1)
    m = re.search(r"((?:NL|BE)C\d+)", str(name))
    return m.group(1) if m else "—"


def tech_of(unit):
    return re.sub(r"_(?:NL|BE)C\d+$", "", str(unit))


# --------------------------------------------------------------------------
# emission-accounting classification (read from the INPUT database)
# --------------------------------------------------------------------------
def atmosphere_coefficients(input_con):
    """flow_ratio_equality_coefficient rows that reference the atmosphere node.

    A unit that appears here books a residual emission at the stack, i.e. its
    capture is ALREADY netted out of its atmospheric emission.
    """
    df, _ = sio.parameter_frame(input_con, ["flow_ratio_equality_coefficient"])
    df = df[df["entity_name"].astype(str).str.contains("atmosphere", na=False)].copy()
    df["coefficient"] = pd.to_numeric(df["value"], errors="coerce")
    df["unit"] = df["entity_name"].astype(str).str.split("__").str[0]
    return df[["unit", "entity_name", "coefficient"]].dropna(subset=["coefficient"])


def classify_co2_producers(uf, atm_coef, factor):
    """Classify units that push CO2 into the CO2 network by accounting treatment.

    netted_at_source
        The unit also reports a residual flow to `atmosphere`, so its capture is
        already subtracted from its own stack emission. Crediting it again at the
        injector is a straight duplicate.
    no_emission_booked
        The unit has no `atmosphere` relationship at all. Its carbon never enters
        the emission account, so the injector credit is only legitimate for the
        share that genuinely came out of the air (DAC) or out of biomass.

    For `no_emission_booked` units the fossil carbon they consume is converted to
    CO2 with `factor` and treated as carbon that should have been booked as an
    emission; only the unexplained remainder earns a valid removal credit.
    """
    produced = (uf[(uf["node"].astype(str).str.fullmatch(CO2_NODE_RE)) &
                   (uf["direction"] == "to_node")]
                .groupby(["unit", "period"])["value_annual"].sum().rename("co2_to_network"))

    ins = uf[uf["direction"] == "from_node"].copy()
    ins["carrier"] = ins["node"].astype(str).str.rsplit("_", n=1).str[0]
    fossil = (ins[ins["carrier"].isin(FOSSIL_CARRIERS)]
              .groupby(["unit", "period"])["value_annual"].sum().rename("fossil_input"))
    bio = (ins[ins["carrier"].isin(BIOGENIC_CARRIERS)]
           .groupby(["unit", "period"])["value_annual"].sum().rename("biogenic_input"))

    df = pd.DataFrame(produced).join(fossil).join(bio).fillna(0.0).reset_index()
    netted = set(atm_coef["unit"])
    df["treatment"] = np.where(df["unit"].isin(netted), "netted_at_source", "no_emission_booked")
    df["tech"] = df["unit"].map(tech_of)
    df["region"] = df["unit"].map(region_of)
    df["fossil_co2_implied"] = np.where(df["treatment"] == "no_emission_booked",
                                        df["fossil_input"] * factor, 0.0)
    df["credit_eligible"] = np.where(
        df["treatment"] == "no_emission_booked",
        (df["co2_to_network"] - df["fossil_co2_implied"]).clip(lower=0.0),
        0.0)
    df["credit_eligible"] = np.minimum(df["credit_eligible"], df["co2_to_network"])
    df["credit_ineligible"] = df["co2_to_network"] - df["credit_eligible"]
    return df


def co2_balance(uf, classification):
    """Annual CO2 balance per milestone period, reported vs corrected.

    The injector credit is apportioned pro rata over everything that entered the
    CO2 network, because the network is a single pooled commodity.
    """
    atm = uf[uf["node"] == ATMOSPHERE]
    gross = atm[atm["direction"] == "to_node"].groupby("period")["value_annual"].sum()
    credit = atm[atm["direction"] == "from_node"].groupby("period")["value_annual"].sum()

    g = classification.groupby("period")[
        ["co2_to_network", "credit_eligible", "credit_ineligible"]].sum()
    dup = (classification[classification["treatment"] == "netted_at_source"]
           .groupby("period")["co2_to_network"].sum())
    share = (g["credit_eligible"] / g["co2_to_network"].replace(0, np.nan)).fillna(0.0)
    dup_share = (dup.reindex(g.index).fillna(0.0)
                 / g["co2_to_network"].replace(0, np.nan)).fillna(0.0)

    applied = credit.reindex(g.index).fillna(0.0)
    out = pd.DataFrame({
        "gross_emissions_to_atmosphere": gross.reindex(g.index).fillna(0.0),
        "co2_into_network": g["co2_to_network"],
        "injection_credit_applied_by_model": applied,
        "credit_duplicating_stack_netting": applied * dup_share,
        "credit_on_unbooked_fossil_carbon": (applied * (1 - share - dup_share)).clip(lower=0.0),
        "credit_that_is_valid": applied * share,
    })
    out["net_reported_by_model"] = (out["gross_emissions_to_atmosphere"]
                                    - out["injection_credit_applied_by_model"])
    out["net_corrected_core"] = (out["net_reported_by_model"]
                                 + out["credit_duplicating_stack_netting"])
    out["net_corrected_full"] = (out["gross_emissions_to_atmosphere"]
                                 - out["credit_that_is_valid"])
    return out.sort_index()


# --------------------------------------------------------------------------
# missing combustion emissions of units with no atmosphere relationship
# --------------------------------------------------------------------------
CARBON_CARRIERS = FOSSIL_CARRIERS + BIOGENIC_CARRIERS


def implied_ch4_factors(uf, tol=1e-6):
    """Implied CO2 per unit of CH4 for units whose only carbon input is CH4."""
    ins = uf[uf["direction"] == "from_node"].copy()
    ins["carrier"] = ins["node"].astype(str).str.rsplit("_", n=1).str[0]
    fuels = ins[ins["carrier"].isin(CARBON_CARRIERS)]
    piv = (fuels.groupby(["unit", "period", "carrier"])["value_annual"].sum()
           .unstack("carrier").fillna(0.0))
    if "CH4" not in piv.columns:
        return pd.DataFrame(columns=["ch4_in", "atmosphere_out", "co2_captured",
                                     "co2_total_per_ch4", "books_atmosphere"])
    other = piv.drop(columns=["CH4"]).sum(axis=1)
    ch4_only = piv[(piv["CH4"] > tol) & (other <= tol)]

    out = uf[(uf["node"] == ATMOSPHERE) & (uf["direction"] == "to_node")] \
        .groupby(["unit", "period"])["value_annual"].sum()
    cap = uf[(uf["node"].astype(str).str.fullmatch(CO2_NODE_RE)) & (uf["direction"] == "to_node")] \
        .groupby(["unit", "period"])["value_annual"].sum()
    res = (pd.DataFrame({"ch4_in": ch4_only["CH4"]})
           .join(out.rename("atmosphere_out")).join(cap.rename("co2_captured")).fillna(0.0))
    res = res[res["ch4_in"] > 1.0]
    res["co2_total_per_ch4"] = (res["atmosphere_out"] + res["co2_captured"]) / res["ch4_in"]
    res["books_atmosphere"] = res["atmosphere_out"] > 0
    return res


def fuel_carbon_double_booking(uf, atm_coef, carriers=("CH4", "HC")):
    """Fuel carbon booked as an emission at the supply step AND again at the burner.

    This model books the carbon content of imported fossil fuel where it enters
    the system (`LNG-terminal` emits 0.2 per unit of CH4 delivered, the standard
    natural-gas combustion factor). Power units rely on that and book nothing.
    Several industrial units book their own combustion emission on top, so the
    same carbon is charged twice.

    `supply_side_factor` is the emission booked by all suppliers of a carrier
    divided by everything they supplied, so biomethane (which books nothing)
    correctly dilutes it.
    """
    booking = set(atm_coef["unit"])
    emission = (uf[(uf["node"] == ATMOSPHERE) & (uf["direction"] == "to_node")]
                .groupby(["unit", "period"])["value_annual"].sum())
    flows = uf.copy()
    flows["carrier"] = flows["node"].astype(str).str.rsplit("_", n=1).str[0]

    rows = []
    for carrier in carriers:
        f = flows[flows["carrier"] == carrier]
        if f.empty:
            continue
        for period, fp in f.groupby("period"):
            supplied = fp[fp["direction"] == "to_node"].groupby("unit")["value_annual"].sum()
            if supplied.sum() <= 1e-6:
                continue
            booked = sum(emission.get((u, period), 0.0) for u in supplied.index if u in booking)
            factor = booked / supplied.sum()
            consumed = fp[fp["direction"] == "from_node"].groupby("unit")["value_annual"].sum()
            for u, v in consumed.items():
                if u not in booking or v <= 1e-6:
                    continue
                own = emission.get((u, period), 0.0)
                already = v * factor
                rows.append({"carrier": carrier, "unit": u, "tech": tech_of(u),
                             "period": period, "consumed": v,
                             "supply_side_factor": factor,
                             "own_emission": own,
                             "carbon_already_charged_upstream": already,
                             "double_booked": min(own, already)})
    return pd.DataFrame(rows)


def factor_band(factors):
    """Low / median / high implied CO2-per-CH4 from units that DO book emissions."""
    ref = factors[factors["books_atmosphere"]]["co2_total_per_ch4"] if len(factors) else pd.Series(dtype=float)
    if ref.empty:
        return 0.0, 0.0, 0.0
    return float(ref.quantile(0.25)), float(ref.median()), float(ref.quantile(0.75))


def unbooked_fuel_emissions(uf, classification, factor):
    """Fossil fuel burnt by units that book no atmospheric emission at all."""
    sink = classification[classification["treatment"] == "no_emission_booked"]
    res = sink.groupby(["unit", "tech", "region", "period"], as_index=False).agg(
        fossil_input=("fossil_input", "sum"),
        co2_to_network=("co2_to_network", "sum"),
        fossil_co2_implied=("fossil_co2_implied", "sum"),
        credit_eligible=("credit_eligible", "sum"))
    res["factor_used"] = factor
    return res[res["fossil_input"] > 0].sort_values(
        ["period", "fossil_co2_implied"], ascending=[True, False])


# --------------------------------------------------------------------------
# fleet
# --------------------------------------------------------------------------
def fleet(results_con, input_con):
    """Units available per milestone, with capacity and a placeholder flag."""
    inv = sio.timeseries(results_con,
                         ["units_invested_available", "units_invested", "units_mothballed"],
                         {"dim1": "unit"})
    inv = inv.dropna(subset=["ts"]).copy()
    inv["period"] = inv["ts"].dt.year
    wide = inv.pivot_table(index=["unit", "period"], columns="param",
                           values="value", aggfunc="sum").fillna(0.0).reset_index()

    cap, _ = sio.parameter_frame(results_con, ["capacity_per_unit"])
    cap_rows = []
    for row in cap.itertuples(index=False):
        d = row._asdict()
        vals = [v for _, v in sio._unpack(d["vtype"], d["value"])]
        if vals and d.get("dim3") == "to_node":
            cap_rows.append({"unit": d.get("dim1"), "node": d.get("dim2"),
                             "capacity_per_unit": max(vals)})
    capdf = pd.DataFrame(cap_rows).sort_values("capacity_per_unit", ascending=False)
    capdf = capdf.drop_duplicates("unit")

    bound, _ = sio.parameter_frame(input_con, ["investment_count_max_cumulative"])
    bound["bound"] = pd.to_numeric(bound["value"], errors="coerce")
    bound = bound[["entity_name", "bound"]].rename(columns={"entity_name": "unit"})

    out = wide.merge(capdf, on="unit", how="left").merge(bound, on="unit", how="left")
    out["tech"] = out["unit"].map(tech_of)
    out["region"] = out["unit"].map(region_of)
    out["capacity_available"] = out["units_invested_available"] * out["capacity_per_unit"]
    out["at_investment_bound"] = np.isclose(out["units_invested_available"],
                                            out["bound"].fillna(-1), rtol=1e-4)
    # `*-production-reference` entities are generic stand-ins for sectors without an
    # explicit route; their capacity_per_unit is arbitrary so unit counts and capacity
    # are not comparable with real plant.
    out["is_placeholder"] = out["tech"].str.contains("production-reference", na=False)
    return out


def existing_vs_new(fleet_df, input_con):
    """Correct existing/new split: `existing` is the pre-2030 endowment only."""
    init, _ = sio.parameter_frame(input_con, ["investment_count_initial_cumulative"])
    init["initial"] = pd.to_numeric(init["value"], errors="coerce")
    init = init[["entity_name", "initial"]].rename(columns={"entity_name": "unit"})
    df = fleet_df.merge(init, on="unit", how="left")
    df["initial"] = df["initial"].fillna(0.0)
    df["existing_retained"] = np.minimum(df["units_invested_available"], df["initial"])
    df["new_build"] = (df["units_invested_available"] - df["existing_retained"]).clip(lower=0)
    df["existing_retired"] = (df["initial"] - df["existing_retained"]).clip(lower=0)
    return df


# --------------------------------------------------------------------------
# cap
# --------------------------------------------------------------------------
def co2_cap(input_con, rep_weight, year_to_milestone=None):
    """Annual-equivalent CO2 cap implied by the atmosphere storage node.

    The cap is stated per representative day, so it scales by the *total* annual
    weight (365), not by any single day's weight.
    """
    df, _ = sio.parameter_frame(
        input_con, ["storage_investment_count_max_cumulative", "storage_state_max"])
    df = df[df["entity_name"] == ATMOSPHERE]
    smax = None
    counts = {}
    for row in df.itertuples(index=False):
        d = row._asdict()
        pairs = sio._unpack(d["vtype"], d["value"])
        if d["param"] == "storage_state_max":
            smax = pairs[0][1]
        else:
            for ts, v in pairs:
                counts[pd.to_datetime(ts).year] = v
    smax = smax if smax else 1.0
    total_w = annual_weight(rep_weight, year_to_milestone)
    return pd.Series({y: v * smax * total_w for y, v in counts.items()}).sort_index(), smax
