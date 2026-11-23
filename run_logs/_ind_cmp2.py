import pandas as pd
A = r"EU_case\data\Industry\technology_catalogue_ind_nuts0_nuts3.xlsx"; B = r"data\Industry\technology_catalogue_ind_nuts0_nuts3.xlsx"
for f in (A, B):
    d = pd.read_excel(f, "ind_process_routes_sec"); print(f, d.shape, d.columns.tolist()[:6])
a = pd.read_excel(A, "ind_process_routes_sec"); b = pd.read_excel(B, "ind_process_routes_sec")
k = a.columns[0]; print("key", k)
sa, sb = set(a[k].astype(str)), set(b[k].astype(str))
print("only IC:", sorted(sb - sa)); print("only EU:", sorted(sa - sb)); print("common", len(sa & sb))
for f in (A, B):
    d = pd.read_excel(f, "ind_production_30_50_nuts0"); print(f, d[d.country_code.isin(["NL","BE"])].groupby("sector_id")["2050"].sum().round(1).to_dict())
