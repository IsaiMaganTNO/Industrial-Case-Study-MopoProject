import pandas as pd
SRC=r"data/VRE"; DST=r"data/VRE_NWEU"
print("=== 3. potentials: country == sum of members ===")
for f in ["potential_wind-on.xlsx","potential_solar-PV.xlsx"]:
    a=pd.read_excel(f"{SRC}/VRE_greenfield_installation_potentials/{f}","Data",index_col=0)
    b=pd.read_excel(f"{DST}/VRE_greenfield_installation_potentials/{f}","Data",index_col=0)
    w=pd.read_excel(r"data-pipelines/europe/_ines-builder/region_transformation.xlsx","PECD2_PECD1")
    print("\n%s  new rows=%d" % (f,len(b)))
    col="Greenfield_potential_GW"
    for c in ["DE","DK","NO","UK"]:
        mem=[m for m in w[w.target==c].source if m in a.index]
        exp=a.loc[mem,col].sum(); got=b.at[c,col]
        print("   %-3s members=%d expected=%9.2f got=%9.2f delta=%.2e" % (c,len(mem),exp,got,abs(exp-got)))
    # BE/NL untouched
    d=max(abs(a.loc[r,col]-b.loc[r,col]) for r in b.index if r.startswith(("BEC","NLC")))
    print("   BE/NL max |delta| vs source: %.2e" % d)
print("\n=== 4. existing capacity (Regional_decomm_2025) ===")
for f in ["capacity_wind-on-existing.xlsx","capacity_solar-PV-existing.xlsx"]:
    a=pd.read_excel(f"{SRC}/VRE_installed_capacities_2020_and_2025/{f}","Regional_decomm_2025",index_col=0)
    b=pd.read_excel(f"{DST}/VRE_installed_capacities_2020_and_2025/{f}","Regional_decomm_2025",index_col=0)
    w=pd.read_excel(r"data-pipelines/europe/_ines-builder/region_transformation.xlsx","PECD2_PECD1")
    print("\n%s rows %d -> %d; cols %s" % (f,len(a),len(b),list(b.columns)[:4]))
    for c in ["DE","DK","NO","UK"]:
        mem=[m for m in w[w.target==c].source if m in a.index]
        exp=a.loc[mem,2030].sum(); got=b.at[c,2030]
        print("   %-3s 2030 GW expected=%7.2f got=%7.2f" % (c,exp,got))
    print("   BE+NL 2030 GW: src=%.2f new=%.2f" % (
        a.loc[[i for i in a.index if str(i).startswith(("BEC","NLC"))],2030].sum(),
        b.loc[[i for i in b.index if str(i).startswith(("BEC","NLC"))],2030].sum()))
