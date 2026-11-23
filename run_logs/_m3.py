import pandas as pd, os
B=r"verification\Data - IC1 and PECD1"
T={"NO","DE","DK","UK"}
d=pd.read_csv(os.path.join(B,"Buildings","simplified_capacities_with_decommissioning_MW.csv"))
have=set(d.country.astype(str).str.strip())
print("Buildings capacities: countries",len(have),"| target present:",sorted(T&have),"missing:",sorted(T-have))
print("  IC1 present?",sorted([x for x in have if x.startswith(("BEC","NLC"))])[:6],"...")
d2=pd.read_csv(os.path.join(B,"Buildings","peak_to_yearly_demand_ratios_MW_GWh.csv"))
have2=set(str(c).strip() for c in d2.columns)
print("Buildings peak ratios: target present:",sorted(T&have2),"missing:",sorted(T-have2))
