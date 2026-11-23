import csv, io, os, collections
p = "data/VRE/VRE_time_series/wind-on-SP199-HH100.csv"
print("%.0f MB" % (os.path.getsize(p)/1e6))
with open(p, encoding="utf-8", errors="replace") as f:
    hdr = next(csv.reader(io.StringIO(f.readline())))
cols = hdr[1:]
ic1 = [c for c in cols if c.startswith(("BEC", "NLC"))]
pre = collections.defaultdict(list)
for c in cols:
    if c not in ic1:
        pre[c[:2]].append(c)
print("regions:", len(cols), "| IC1:", len(ic1), "| PECD2:", len(cols)-len(ic1))
for k in ["DE", "DK", "NO", "UK"]:
    print("  %-3s %d" % (k, len(pre.get(k, []))))
print()
for f in ["data/CO2_network/CO2_data_IC1_low_cost.xlsx",
          "data/Industry/technology_catalogue_ind_nuts0_nuts3_update.xlsx",
          "data/Rdemand/other_electricity_demand.csv",
          "data/Transport/fleets_per_scenario.csv"]:
    print("%-58s %s" % (f[:58], "OK %.1f MB" % (os.path.getsize(f)/1e6)
          if os.path.exists(f) else "MISSING"))
