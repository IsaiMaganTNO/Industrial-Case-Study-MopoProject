import pandas as pd
p="reports_1rep_gwfix/Investment_Results.1rep_gwfix_"
fleet=pd.read_csv(p+"fleet.csv")

ENERGY = {"solar PV","wind onshore","wind offshore","nuclear","hydro","gas turbine",
          "electrolysis","CO2 removal (DAC)","e-fuels / green chemicals","other",
          "electrification (heat pumps)","battery / storage","coal","biomass"}
out=[]
out.append("ALL CATEGORIES PRESENT IN fleet.csv:")
for c in sorted(fleet.category.unique()): out.append("   - {}".format(c))

piv = fleet.pivot_table(index=["category","tech","vintage"], columns="year",
                        values="units", aggfunc="sum", fill_value=0.0)
for y in (2030,2040,2050):
    if y not in piv.columns: piv[y]=0.0
piv=piv[[2030,2040,2050]].round(2)
piv=piv[(piv.T!=0).any()]

lines=["","="*96,"ENERGY SUPPLY TECHNOLOGIES - CAPACITY (GW; capacity_per_unit=1.0)",
       "existing = pre-existing fleet, new = model-built. total = sum.","="*96]
lines.append("{:<34}{:<10}{:>12}{:>12}{:>12}".format("tech","vintage",2030,2040,2050))
lines.append("-"*96)
cur=None
for (cat,tech,vint),row in piv.iterrows():
    if cat!=cur:
        lines.append(""); lines.append("### {} ###".format(cat)); cur=cat
    lines.append("{:<34}{:<10}{:>12.2f}{:>12.2f}{:>12.2f}".format(tech[:33],vint,row[2030],row[2040],row[2050]))

tot = fleet.pivot_table(index=["tech"],columns=["year","vintage"],values="units",aggfunc="sum",fill_value=0.0)
lines.append("")
lines.append("="*96)
lines.append("TOTALS BY TECH: existing / new / TOTAL per year")
lines.append("="*96)
lines.append("{:<34}{:>30}{:>30}".format("tech","2030 ex/new/tot","2050 ex/new/tot"))
lines.append("-"*96)
agg=fleet.pivot_table(index="tech",columns=["year","vintage"],values="units",aggfunc="sum",fill_value=0.0)
rows=[]
for tech in agg.index:
    def gv(y,v):
        try: return float(agg.loc[tech,(y,v)])
        except Exception: return 0.0
    e30,n30=gv(2030,"existing"),gv(2030,"new")
    e50,n50=gv(2050,"existing"),gv(2050,"new")
    rows.append((e50+n50,tech,e30,n30,e50,n50))
rows.sort(reverse=True)
for t,tech,e30,n30,e50,n50 in rows:
    if e30+n30+e50+n50 < 0.005: continue
    lines.append("{:<34}{:>30}{:>30}".format(tech[:33],
        "{:.2f}/{:.2f}/{:.2f}".format(e30,n30,e30+n30),
        "{:.2f}/{:.2f}/{:.2f}".format(e50,n50,e50+n50)))
open("logs/supply_capacity_table.txt","w",encoding="utf-8").write("\n".join(out+lines))
