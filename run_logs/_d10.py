import pandas as pd, os, re
B=r"verification\Data - IC1 and PECD1"
def rep(tag,cols):
    ic1=[c for c in cols if re.fullmatch(r"(BE|NL)C\d",str(c))]
    p1=[c for c in cols if re.fullmatch(r"[A-Z]{2}",str(c))]
    print(f"{tag}: ncols={len(cols)} IC1={len(ic1)} PECD1={len(p1)}")
    print(f"   IC1: {sorted(ic1)}")
    print(f"   PECD1: {sorted(p1)}")
    print(f"   bare BE/NL present? {sorted(set(p1)&{'BE','NL'})}")
d=pd.read_csv(os.path.join(B,"Rdemand","other_electricity_demand.csv"),sep=";",nrows=3)
rep("Rdemand",d.columns)
print(" sample:",d.iloc[:2,:4].to_string()[:200])
d2=pd.read_csv(os.path.join(B,"Buildings","scenario_total_yearly_demands_GWh.csv"),sep=";",nrows=3)
rep("Buildings",d2.columns)
d3=pd.read_csv(os.path.join(B,"Transport","fleets_per_scenario.csv"),sep=";",nrows=3)
rep("Transport",d3.columns)
