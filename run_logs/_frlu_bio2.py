import pandas as pd
d = pd.read_csv(r"data/Biomass/db_biomass_ener_mopo_mixedres.csv")
print(d.columns.tolist())
cc = [c for c in d.columns if c.lower() in ("nuts0","country","cntr_code")]
print("country col", cc)
k = cc[0]
for c in ("DE","NO","FR","LU"):
    s = d[d[k]==c]; print(c, len(s), "nuts3 sample", s["nuts3"].unique()[:5].tolist())
m = pd.read_excel(r"data-pipelines/europe/region_transformation_IC1.xlsx", sheet_name="NUTS3_IC1")
print(m.shape, m.columns.tolist()); print(m.target.value_counts().to_string())
