import pandas as pd
for p,lbl in [(r"data\VRE\VRE_greenfield_installation_potentials\potential_solar-PV.xlsx","solar-PV"),
              (r"data\VRE\VRE_greenfield_installation_potentials\potential_wind-on.xlsx","wind-on")]:
    xl=pd.ExcelFile(p)
    print(f"=== {lbl}  sheets={xl.sheet_names}")
    d=xl.parse(xl.sheet_names[0])
    print("cols:",list(d.columns)[:10],"shape",d.shape)
    c0=d.columns[0]
    sel=d[d[c0].astype(str).str.match(r'^(BE|NL)C\d+$',na=False)]
    print(sel.to_string()[:1500]); print()
