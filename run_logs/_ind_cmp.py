import pandas as pd, glob
for f in [r"EU_case\data\Industry\technology_catalogue_ind_nuts0_nuts3.xlsx", *glob.glob(r"data\Industry\**\technology_catalogue_ind_nuts0_nuts3.xlsx", recursive=True)]:
    x = pd.ExcelFile(f); print(f, x.sheet_names)
    for sh in x.sheet_names[:3]:
        d = x.parse(sh); print(sh, d.shape); print(d.columns.tolist()[:12])
        for c in d.columns:
            if "sector" in str(c).lower(): print(sorted(d[c].dropna().astype(str).unique()))
