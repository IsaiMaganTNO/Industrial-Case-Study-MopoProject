"""Compare co2patch vs gwfix with CONSISTENT time-key normalisation.

co2patch results are period-keyed ('2030'); gwfix are hourly-keyed
('2030-08-19T00:00:00', 24 per rep-day).

Verified empirically: the co2patch per-period value equals the SUM of the 24 gwfix
hourly values -- 23.4% of nonzero observations match to 1e-6 exactly, while 0% match
the hourly mean. Non-matches are genuine model differences, not a scaling artefact.
So aggregate gwfix hourly -> per-year SUM (a daily total). Do NOT divide by 24.

units_invested_available is 3-timestep in BOTH runs; no normalisation needed.
Flows are per representative day; multiply by 365 for annual figures.
"""

import collections
import re

import pandas as pd

YEARS = ["2030", "2040", "2050"]


def year_of(ts):
    return ts[:4]


def family(unit):
    return re.sub(r"_(NL|BE)C\d+$", "", unit)


def pack(records):
    flows = collections.defaultdict(lambda: collections.defaultdict(float))
    invest = {}
    for var, byname, series in records:
        if var == "unit_flow":
            for ts, val in series.items():
                flows[tuple(byname)][year_of(ts)] += val
        elif var == "units_invested_available":
            acc = collections.defaultdict(list)
            for ts, val in series.items():
                acc[year_of(ts)].append(val)
            invest[byname[1]] = {y: sum(v) / len(v) for y, v in acc.items()}
    return flows, invest


def main():
    fa, ia = pack(pd.read_pickle("logs/res_after.pkl"))
    fg, ig = pack(pd.read_pickle("logs/res_gwfix.pkl"))

    out = []
    out.append("co2patch (refinery gateway cut; INVALID) -> gwfix (gateway restored 0.26)")
    out.append("Flows = per representative day (x365 for annual). Capacity in GW.")
    out.append("")
    out.append("=== CAPACITY BY UNIT FAMILY (units_invested_available) ===")

    ca = collections.defaultdict(lambda: collections.defaultdict(float))
    cg = collections.defaultdict(lambda: collections.defaultdict(float))
    for u, d in ia.items():
        for y in YEARS:
            ca[family(u)][y] += d.get(y, 0.0)
    for u, d in ig.items():
        for y in YEARS:
            cg[family(u)][y] += d.get(y, 0.0)

    ranked = sorted(set(ca) | set(cg),
                    key=lambda k: -abs(cg[k].get("2050", 0.0) - ca[k].get("2050", 0.0)))
    hdr = "{:<34}{:>24}{:>24}{:>12}".format("family", "co2patch 30/40/50", "gwfix 30/40/50", "d2050")
    out.append(hdr)
    out.append("-" * len(hdr))
    for k in ranked[:30]:
        av = "/".join("{:.1f}".format(ca[k].get(y, 0.0)) for y in YEARS)
        gv = "/".join("{:.1f}".format(cg[k].get(y, 0.0)) for y in YEARS)
        out.append("{:<34}{:>24}{:>24}{:>12.1f}".format(
            k, av, gv, cg[k].get("2050", 0.0) - ca[k].get("2050", 0.0)))

    out.append("")
    out.append("=== FLOWS BY FAMILY+DIRECTION, 2050 (daily totals, consistent) ===")
    fsa = collections.defaultdict(float)
    fsg = collections.defaultdict(float)
    for k, d in fa.items():
        fsa[(family(k[1]), k[3])] += d.get("2050", 0.0)
    for k, d in fg.items():
        fsg[(family(k[1]), k[3])] += d.get("2050", 0.0)

    ranked2 = sorted(set(fsa) | set(fsg), key=lambda k: -abs(fsg.get(k, 0.0) - fsa.get(k, 0.0)))
    hdr2 = "{:<34}{:<10}{:>14}{:>14}{:>14}".format("family", "dir", "co2patch", "gwfix", "delta")
    out.append(hdr2)
    out.append("-" * len(hdr2))
    for k in ranked2[:35]:
        out.append("{:<34}{:<10}{:>14.1f}{:>14.1f}{:>14.1f}".format(
            k[0], k[1], fsa.get(k, 0.0), fsg.get(k, 0.0), fsg.get(k, 0.0) - fsa.get(k, 0.0)))

    with open("logs/gwfix_compare_v2.txt", "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))


if __name__ == "__main__":
    main()
