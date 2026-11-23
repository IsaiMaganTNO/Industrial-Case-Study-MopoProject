import pandas as pd, re, os
base=r"data/VRE/VRE_installed_capacities_2020_and_2025"
for f in ["capacity_wind-on-existing.xlsx","capacity_solar-PV-existing.xlsx","capacity_wind-off-FB-existing.xlsx"]:
    d=pd.read_excel(os.path.join(base,f),"Regional_decomm_2025",index_col=0)
    idx=[str(i) for i in d.index]
    t=[i for i in idx if re.match(r"^(DE|DK|NO|UK)",i)]
    ic=[i for i in idx if re.match(r"^(BEC|NLC)",i)]
    print("%-36s n=%-4d IC1=%-3d targets(%d)=%s" % (f,len(idx),len(ic),len(t),t[:22]))
    print("     cols:", list(d.columns)[:6])
    nz=[i for i in t if float(d.at[i,2030] or 0)>0]
    print("     targets with 2030 capacity>0:", nz[:22])
