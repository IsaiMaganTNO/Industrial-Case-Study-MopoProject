import pandas as pd, collections
p = "data/VRE/VRE_installed_capacities_2020_and_2025/capacity_wind-on-existing.xlsx"
d = pd.read_excel(p, sheet_name="Regional_decomm_2025", index_col=0)
print("shape:", d.shape)
print("columns:", list(d.columns)[:8])
idx = [str(x) for x in d.index]
ic1 = [x for x in idx if x.startswith(("BEC", "NLC"))]
print("rows=%d  IC1=%d" % (len(idx), len(ic1)))
pre = collections.Counter(x[:2] for x in idx if x not in ic1)
print("target counts:", {k: pre.get(k, 0) for k in ["DE","DK","NO","UK"]})
for k in ["DE","DK","NO","UK"]:
    rows = [x for x in idx if x.startswith(k)]
    print("  %-3s %s" % (k, rows))
    if rows and 2030 in d.columns:
        print("      2030 GW:", [round(float(d.at[r, 2030]), 3) for r in rows])
