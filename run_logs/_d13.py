import pandas as pd, re, os
B=r"verification\Data - IC1 and PECD1"
d=pd.read_csv(os.path.join(B,"VRE","VRE_time_series","wind-on-SP277-HH100.csv"),nrows=2)
cols=[str(c) for c in d.columns]
ic1=[c for c in cols if re.fullmatch(r"(BE|NL)C\d",c)]
p2=[c for c in cols if re.fullmatch(r"[A-Z]{2}\d{2}",c)]
p3=[c for c in cols if re.fullmatch(r"[A-Z]{2}\d{3}",c)]
other=[c for c in cols if c not in ic1+p2+p3]
print("IC1",len(ic1),"PECD2",len(p2),"len3-digit",len(p3),p3[:10])
print("other:",other[:10])
print("\npowerplants countries:")
pp=pd.read_csv(os.path.join(B,"Energy_Conversion","powerplants.csv"),usecols=["Country","Capacity"])
print(" rows",len(pp),"countries",pp.Country.nunique())
print(sorted(pp.Country.astype(str).unique())[:45])
