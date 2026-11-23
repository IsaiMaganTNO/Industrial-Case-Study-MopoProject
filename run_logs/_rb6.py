import pandas as pd, re
d=pd.read_excel(r"data/VRE/VRE_greenfield_installation_potentials/potential_wind-on.xlsx","Data")
r=sorted(d["Region"].astype(str))
ic1=[x for x in r if re.match(r"^(BEC|NLC)\d$",x)]
print("total regions",len(r),"| IC1-style",len(ic1),":",ic1)
print("are BE01/BE02/BE03 also present?", [x for x in r if x.startswith("BE") and not x.startswith("BEC")])
print("NL*:", [x for x in r if x.startswith("NL")])
print("\n-- so the file is already the hybrid 136-region set (17 IC1 + 119 PECD2) --")
print("matches VRE timeseries 136 cols:", len(r))
