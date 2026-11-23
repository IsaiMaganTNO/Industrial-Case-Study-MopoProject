import pandas as pd, os, re
B=r"verification\Data - IC1 and PECD1"
d=pd.read_csv(os.path.join(B,"VRE","VRE_time_series","wind-on-SP277-HH100.csv"),nrows=2)
p2=[c for c in d.columns if re.fullmatch(r"[A-Z]{2}\d{2}",str(c))]
benl=[c for c in p2 if c[:2] in ("BE","NL")]
print("VRE wind-on: PECD2 regions in BE/NL:",benl," <- must be empty to avoid double-count")
print("total cols",len(d.columns),"IC1 17 + PECD2",len(p2),"+ time =",17+len(p2)+1)
# transport & biomass country coverage
t=pd.read_csv(os.path.join(B,"Transport","fleets_per_scenario.csv"))
cc=sorted(t["Country code"].astype(str).unique())
print("\nTransport country codes (",len(cc),"):",cc)
b=pd.read_csv(os.path.join(B,"Biomass","db_biomass_ener_mopo.csv"),usecols=["nuts0","nuts3"])
n0=sorted(b.nuts0.astype(str).unique())
print("\nBiomass nuts0 (",len(n0),"):",n0)
print("Biomass nuts3 count:",b.nuts3.nunique())
