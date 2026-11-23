import pandas as pd, os
B=r"verification\Data - IC1 and PECD1"
for f in ["simplified_capacities_with_decommissioning_MW.csv","peak_to_yearly_demand_ratios_MW_GWh.csv"]:
    p=os.path.join(B,"Buildings",f)
    with open(p,encoding="utf8",errors="replace") as fh:
        h=fh.readline().strip(); r=fh.readline().strip()
    print(f"\n=== {f}")
    print("  header:",h[:300])
    print("  row1  :",r[:200])
