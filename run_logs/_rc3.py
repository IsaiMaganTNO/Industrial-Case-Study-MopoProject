import pandas as pd
# which timeseries does VRE_DB actually read? techs in VRE_costs except solar-PV-existing
vc=pd.read_csv(r"data/VRE/VRE_costs_EUR2025/VRE_costs.csv",index_col=0)
techs=[t for t in vc.index if pd.notna(t) and t!="solar-PV-existing"]
on=[t for t in techs if "wind-on" in t or "solar-PV" in t]
off=[t for t in techs if "wind-off" in t]
print("ONSHORE techs needing aggregation (%d):"%len(on)); [print("   ",t) for t in on]
print("OFFSHORE techs (no aggregation; OFF3 sea zones) (%d):"%len(off)); [print("   ",t) for t in off]
