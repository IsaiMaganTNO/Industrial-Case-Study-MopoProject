"""
aggregate_vre_to_country.py - collapse PECD2 sub-country VRE regions to single
country regions, for the mixed-resolution (IC1 + country) run.

Why this exists
---------------
The hybrid VRE dataset is keyed by 136 regions: the 17 BE/NL IC1 clusters plus
119 PECD2 zones for the rest of Europe. For the mixed-resolution run we want
DE/DK/NO/UK as ONE region each, but the data gives them as DE01..DE07,
DKE1/DKW1, NOM1/NON1/NOS1-3, UK01..UK05/UKNI.

ines_builder cannot do this collapse: the VRE pipeline runs source==target
(IC1), so it takes the direct-lookup branch and never aggregates. There is also
no PECD2_IC1 transformer sheet. So we pre-aggregate here, before VRE_DB.py runs.

Only ONSHORE needs this. Offshore is keyed by OFF3 sea zones (NSDE011, ...),
which OFF3_map already attaches to the country regions.

Aggregation rules
-----------------
  potentials (GW), existing capacity (GW) : SUM
  availability factors (0-1 hourly)       : capacity-WEIGHTED MEAN

Weights come from the `capacity` column of the PECD2_PECD1 sheet (its `area`
and `population` columns are constant 1.0 and carry no information). Weights
are renormalised over the sub-regions actually present in each file.

Output is a slim tree containing ONLY the 21 target regions, so the
downstream VRE_DB run is also much faster than on the 136-region source.
"""
import os
import sys
import pandas as pd

IC1 = ["BEC%d" % i for i in range(1, 9)] + ["NLC%d" % i for i in range(1, 10)]
COUNTRIES = ["DE", "DK", "NO", "UK", "FR", "LU"]
KEEP = IC1 + COUNTRIES

SRC = "data/VRE"
DST = "data/VRE_NWEU"

ONSHORE_TS = [
    "wind-on-existing", "wind-on-SP335-HH100", "wind-on-SP335-HH150",
    "wind-on-SP277-HH100", "wind-on-SP277-HH150", "wind-on-SP199-HH100",
    "wind-on-SP199-HH150", "solar-PV-no-tracking", "solar-PV-rooftop",
    "solar-PV-tracking",
]


def load_weights(xlsx):
    df = pd.read_excel(xlsx, "PECD2_PECD1")
    df = df[df.target.astype(str).isin(COUNTRIES)]
    return {c: df[df.target == c].set_index("source")["capacity"].to_dict()
            for c in COUNTRIES}


def wmean(frame, members, w):
    """Capacity-weighted mean over the member columns present in `frame`."""
    present = [m for m in members if m in frame.columns]
    if not present:
        return None, []
    tot = sum(w[m] for m in present)
    if tot <= 0:
        return frame[present].mean(axis=1), present
    out = sum(frame[m] * (w[m] / tot) for m in present)
    return out, present

def agg_timeseries(weights, report):
    src = os.path.join(SRC, "VRE_time_series")
    dst = os.path.join(DST, "VRE_time_series")
    os.makedirs(dst, exist_ok=True)
    for tech in ONSHORE_TS:
        fin = os.path.join(src, tech + ".csv")
        fout = os.path.join(dst, tech + ".csv")
        if not os.path.exists(fin):
            report.append((tech, "MISSING SOURCE", ""))
            continue
        # low_memory=False: the junk rows (bare ";") defeat pandas' chunked
        # type inference and raise IndexError in _concatenate_chunks.
        df = pd.read_csv(fin, index_col=0, low_memory=False)
        # drop the all-NaN junk rows seen in 6 of 18 staged files (time == ";")
        before = len(df)
        df = df[~df.index.isna()]
        df = df.dropna(how="all")
        # values can arrive as strings because of those junk rows
        df = df.apply(pd.to_numeric, errors="coerce")
        df = df.dropna(how="all")
        # --- rebuild the time index -------------------------------------
        # The staged files suffered Excel locale damage (see
        # docs/FINDING_vre_excel_date_corruption.md):
        #   days 1-12  -> "MM-DD-YYYY", HOUR LOST (24 identical stamps/day)
        #   days 13-31 -> "M/D/YYYY H:MM", hour present, MONTH-first
        # The hour is unrecoverable from the string for days 1-12, so we
        # reconstruct the index from ROW ORDER, which is chronological.
        #
        # This reconstruction is VERIFIED, not assumed: against the 223,032
        # unambiguous "slash" rows it matches exactly (0 mismatches), and
        # against the 145,152 "dash" rows it matches on date exactly when
        # those are read MONTH-first (0 mismatches; day-first gives 133,056
        # mismatches - i.e. the naive dayfirst=True read would have silently
        # transposed day and month).
        expected = 368184  # 1980-01-01 00:00 .. 2021-12-31 23:00 hourly
        if len(df) != expected:
            report.append((tech, "UNEXPECTED ROW COUNT", str(len(df))))
            continue
        df.index = pd.date_range("1980-01-01 00:00", periods=expected, freq="h")
        df.index.name = "time"
        out = pd.DataFrame(index=df.index)
        miss_ic1 = []
        for r in IC1:
            if r in df.columns:
                out[r] = df[r]
            else:
                miss_ic1.append(r)
        notes = []
        for c in COUNTRIES:
            series, used = wmean(df, list(weights[c]), weights[c])
            if series is None:
                notes.append("%s:NO-MEMBERS" % c)
                continue
            out[c] = series.round(4)
            if len(used) != len(weights[c]):
                notes.append("%s:%d/%d" % (c, len(used), len(weights[c])))
        out.to_csv(fout)
        report.append((tech, "%d->%d cols, %d rows (dropped %d)"
                       % (len(df.columns), len(out.columns), len(out), before - len(df)),
                       ("missing IC1 " + ",".join(miss_ic1) if miss_ic1 else "")
                       + (" | " + ";".join(notes) if notes else "")))


def agg_table(path_in, path_out, sheet, idx_col, weights, how, report, label):
    """how='sum' for GW quantities."""
    df = pd.read_excel(path_in, sheet, index_col=idx_col)
    rows = {}
    miss = []
    for r in IC1:
        if r in df.index:
            rows[r] = df.loc[r]
        else:
            miss.append(r)
    for c in COUNTRIES:
        members = [m for m in weights[c] if m in df.index]
        if not members:
            continue
        sub = df.loc[members]
        rows[c] = sub.sum(numeric_only=True) if how == "sum" else sub.mean(numeric_only=True)
    out = pd.DataFrame(rows).T
    out.index.name = df.index.name
    os.makedirs(os.path.dirname(path_out), exist_ok=True)
    with pd.ExcelWriter(path_out) as w:
        out.to_excel(w, sheet_name=sheet)
    report.append((label, "%d rows -> %d" % (len(df), len(out)),
                   "missing IC1 " + ",".join(miss) if miss else ""))
    return out

def main():
    xlsx = "data-pipelines/europe/_ines-builder/region_transformation.xlsx"
    weights = load_weights(xlsx)
    for c in COUNTRIES:
        print("weights %s: %d members, sum %.3f" % (c, len(weights[c]), sum(weights[c].values())))
    report = []

    # 1. greenfield potentials (SUM of GW)
    gp_in = os.path.join(SRC, "VRE_greenfield_installation_potentials")
    gp_out = os.path.join(DST, "VRE_greenfield_installation_potentials")
    for f, sheet in [("potential_wind-on.xlsx", "Data"),
                     ("potential_solar-PV.xlsx", "Data")]:
        agg_table(os.path.join(gp_in, f), os.path.join(gp_out, f), sheet, 0,
                  weights, "sum", report, "potential " + f)
    # offshore potentials are OFF3 sea zones - copy verbatim
    import shutil
    for f in ("potential_wind-off-FB.xlsx", "potential_wind-off-FO.xlsx"):
        os.makedirs(gp_out, exist_ok=True)
        shutil.copy2(os.path.join(gp_in, f), os.path.join(gp_out, f))
        report.append(("copy " + f, "verbatim (OFF3)", ""))

    # 2. installed capacities (SUM of GW), every sheet of each workbook
    ic_in = os.path.join(SRC, "VRE_installed_capacities_2020_and_2025")
    ic_out = os.path.join(DST, "VRE_installed_capacities_2020_and_2025")
    os.makedirs(ic_out, exist_ok=True)
    for f in ("capacity_wind-on-existing.xlsx", "capacity_solar-PV-existing.xlsx"):
        src_p = os.path.join(ic_in, f)
        xl = pd.ExcelFile(src_p)
        sheets = {}
        for sh in xl.sheet_names:
            df = pd.read_excel(src_p, sh, index_col=0)
            if not any(str(i) in IC1 or str(i) in sum([list(weights[c]) for c in COUNTRIES], [])
                       for i in df.index):
                sheets[sh] = df          # not a regional sheet - pass through
                continue
            rows = {}
            for r in IC1:
                if r in df.index:
                    rows[r] = df.loc[r]
            for c in COUNTRIES:
                members = [m for m in weights[c] if m in df.index]
                if members:
                    rows[c] = df.loc[members].sum(numeric_only=True)
            o = pd.DataFrame(rows).T
            o.index.name = df.index.name
            sheets[sh] = o
        with pd.ExcelWriter(os.path.join(ic_out, f)) as w:
            for sh, o in sheets.items():
                o.to_excel(w, sheet_name=sh)
        report.append(("capacity " + f, "sheets " + ",".join(sheets), ""))
    # offshore existing capacity is OFF3-keyed - copy verbatim
    shutil.copy2(os.path.join(ic_in, "capacity_wind-off-FB-existing.xlsx"),
                 os.path.join(ic_out, "capacity_wind-off-FB-existing.xlsx"))
    report.append(("copy capacity_wind-off-FB-existing.xlsx", "verbatim (OFF3)", ""))

    # 3. costs - region-independent, copy verbatim
    cd = os.path.join(DST, "VRE_costs_EUR2025")
    os.makedirs(cd, exist_ok=True)
    shutil.copy2(os.path.join(SRC, "VRE_costs_EUR2025", "VRE_costs.csv"),
                 os.path.join(cd, "VRE_costs.csv"))

    # 4. offshore timeseries - copy verbatim (OFF3 sea zones)
    ts_out = os.path.join(DST, "VRE_time_series")
    os.makedirs(ts_out, exist_ok=True)
    for t in ("wind-off-FB-existing", "wind-off-FB-SP316-HH155",
              "wind-off-FB-SP370-HH155", "wind-off-FO-SP316-HH155",
              "wind-off-FO-SP370-HH155"):
        s = os.path.join(SRC, "VRE_time_series", t + ".csv")
        if os.path.exists(s):
            shutil.copy2(s, os.path.join(ts_out, t + ".csv"))
            report.append((t, "copied verbatim (OFF3)", ""))

    # 5. onshore timeseries - weighted mean
    agg_timeseries(weights, report)

    print()
    for a, b, c in report:
        print("  %-44s %-34s %s" % (a, b, c))


if __name__ == "__main__":
    sys.exit(main())
