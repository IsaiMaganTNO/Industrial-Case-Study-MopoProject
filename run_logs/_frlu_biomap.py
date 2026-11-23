import pandas as pd, openpyxl
P = r"data-pipelines/europe/region_transformation_IC1.xlsx"
d = pd.read_csv(r"data/Biomass/db_biomass_ener_mopo_mixedres.csv", usecols=["nuts3","nuts0","quantity","scenario"])
m = pd.read_excel(P, sheet_name="NUTS3_IC1")
print("DE sample rows:"); print(m[m.target=="DE"].head(3).to_string())
codes = {c: sorted(d[d.nuts0==c].nuts3.unique()) for c in ("FR","LU")}
have = set(m.source)
wb = openpyxl.load_workbook(P); ws = wb["NUTS3_IC1"]
h = [c.value for c in ws[1]]
tmpl = m[m.target=="DE"].iloc[0]
n = 0
for c, lst in codes.items():
    for code in lst:
        if code in have: continue
        row = {"source": code, "target": c, "area": tmpl["area"], "population": tmpl["population"]}
        ws.append([row[k] for k in h]); n += 1
wb.save(P)
m2 = pd.read_excel(P, sheet_name="NUTS3_IC1")
print("added", n, "rows; sheet now", m2.shape, "FR", (m2.target=="FR").sum(), "LU", (m2.target=="LU").sum())
print("dup sources:", m2.source.duplicated().sum())
q = d[d.nuts0.isin(["FR","LU"])].groupby(["nuts0","scenario"]).quantity.sum()
print("raw CSV quantity (for later DB check):"); print(q.to_string())
