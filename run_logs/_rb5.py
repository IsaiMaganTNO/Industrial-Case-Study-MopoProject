import pandas as pd, re
T={"DE","DK","NO","UK"}
for p,sheet in [(r"data/VRE/VRE_greenfield_installation_potentials/potential_wind-on.xlsx","Data"),
                (r"data/VRE/VRE_greenfield_installation_potentials/potential_solar-PV.xlsx","Data")]:
    d=pd.read_excel(p,sheet)
    r=d["Region"].astype(str)
    print("\n####",p.split("/")[-1],"rows",len(d))
    print("  exact country rows:", sorted(set(r)&T))
    sub=sorted({v for v in set(r) if re.match(r"^(DE|DK|NO|UK)",v)})
    print("  target-prefixed rows (%d):"%len(sub), sub[:30])
    print("  sample all regions:", sorted(set(r))[:12])
    if set(r)&T or sub:
        sel=d[r.isin(T)|r.isin(sub)]
        print(sel.iloc[:,:5].head(25).to_string())
c=pd.read_excel(r"data/VRE/VRE_installed_capacities_2020_and_2025/capacity_wind-on-existing.xlsx","Country_level")
print("\n#### capacity wind-on Country_level rows",len(c))
print(c[c["Code"].astype(str).isin(T)].to_string())
g=pd.read_excel(r"data/VRE/VRE_installed_capacities_2020_and_2025/capacity_wind-on-existing.xlsx","Regional")
print("\nRegional cols",list(g.columns)[:6],"rows",len(g))
print("  regional ids sample:", sorted(set(g.iloc[:,0].astype(str)))[:20])
