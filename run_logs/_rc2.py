import pandas as pd, os, glob
vc=pd.read_csv(r"data/VRE/VRE_costs_EUR2025/VRE_costs.csv",index_col=0)
print("techs in VRE_costs:", [t for t in vc.index if pd.notna(t)])
print()
tot=0
for p in sorted(glob.glob(r"data/VRE/VRE_time_series/*.csv")):
    s=os.path.getsize(p); tot+=s
    print("  %-40s %8.1f MB" % (os.path.basename(p), s/1e6))
print("TOTAL %.1f GB" % (tot/1e9))
print()
for p in [r"data/VRE/VRE_greenfield_installation_potentials/potential_wind-off-FB.xlsx",
          r"data/VRE/VRE_greenfield_installation_potentials/potential_wind-off-FO.xlsx"]:
    xl=pd.ExcelFile(p); sh=xl.sheet_names[0]
    d=pd.read_excel(p,sh)
    r=[str(x) for x in d.iloc[:,0]]
    print(os.path.basename(p),"sheet",sh,"n",len(r),"sample",r[:8])
