import pandas as pd, os, re
T=("DE","DK","NO","UK")
for p in [r"data/VRE/VRE_greenfield_installation_potentials/potential_wind-on.xlsx",
          r"data/VRE/VRE_greenfield_installation_potentials/potential_solar-PV.xlsx",
          r"data/VRE/VRE_installed_capacities_2020_and_2025/capacity_wind-on-existing.xlsx"]:
    print("\n####", os.path.basename(p), os.path.getsize(p))
    xl=pd.ExcelFile(p); print("  sheets:", xl.sheet_names[:8])
    d=pd.read_excel(p, xl.sheet_names[0], nrows=5)
    cols=[str(c) for c in d.columns]
    print("  ncols", len(cols), "first:", cols[:12])
    pref=sorted({c[:4] for c in cols if re.match(r"^(DE|DK|NO|UK)\d", c)})
    print("  PECD2-style target cols:", pref)
    print("  exact country cols:", [c for c in cols if c in T])
