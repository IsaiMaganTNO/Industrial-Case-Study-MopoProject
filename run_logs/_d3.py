import pandas as pd, os, re
B=r"verification\Data - IC1 and PECD1"
NB={"BE","NL"}
def cls(vals):
    v=[str(x).strip() for x in vals if str(x).strip() not in ("nan","None","")]
    ic1={x for x in v if re.fullmatch(r"(BE|NL)C\d",x)}
    p1 ={x for x in v if re.fullmatch(r"[A-Z]{2}",x)}
    p2 ={x for x in v if re.fullmatch(r"[A-Z]{2}\d{2}",x)}
    n3 ={x for x in v if re.fullmatch(r"[A-Z]{2}\d{3}",x)}
    off={x for x in v if re.fullmatch(r"(NS|EM|AS|AT|BL|BS|MS)[A-Z]{2}[A-Z0-9]*",x)}
    return ic1,p1,p2,n3,off
def show(tag,vals):
    ic1,p1,p2,n3,off=cls(vals)
    nonbe_p1=sorted(p1-NB); nonbe_p2=sorted({x for x in p2 if x[:2] not in NB})
    nonbe_n3=sorted({x for x in n3 if x[:2] not in NB})
    print(f"  {tag}")
    print(f"     IC1={len(ic1)}  PECD1={len(p1)} (non-BE/NL {len(nonbe_p1)}: {nonbe_p1[:16]})")
    print(f"     PECD2={len(p2)} (non-BE/NL {len(nonbe_p2)})  NUTS3={len(n3)} (non-BE/NL {len(nonbe_n3)})  OFF={len(off)}")

print("=== VRE greenfield potentials ===")
for f in ["potential_wind-on.xlsx","potential_solar-PV.xlsx","potential_wind-off-FB.xlsx","potential_wind-off-FO.xlsx"]:
    p=os.path.join(B,"VRE","VRE_greenfield_installation_potentials",f)
    d=pd.read_excel(p,usecols=[0])
    show(f,d.iloc[:,0])
print("\n=== VRE installed capacities ===")
for f in os.listdir(os.path.join(B,"VRE","VRE_installed_capacities_2020_and_2025")):
    if f.startswith("~"): continue
    d=pd.read_excel(os.path.join(B,"VRE","VRE_installed_capacities_2020_and_2025",f),usecols=[0])
    show(f,d.iloc[:,0])
