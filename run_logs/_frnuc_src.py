import pandas as pd
df = pd.read_csv(r"data\Energy_Conversion\powerplants.csv", low_memory=False)
print(df.columns.tolist())
fc = [c for c in df.columns if c.lower() in ("fueltype","fuel","technology")]
cc = [c for c in df.columns if c.lower() in ("country",)][0]
nuc = df[df[fc[0]].astype(str).str.contains("uclear", case=False)]
fr = nuc[nuc[cc].astype(str).isin(["France","FR"])]
print("FR nuclear units:", len(fr), " total MW:", round(fr["Capacity"].sum(),1))
cols = [c for c in ["Name","Capacity","DateIn","DateRetrofit","DateOut","Status","lat","lon"] if c in fr.columns]
print(fr[cols].sort_values("DateIn").to_string())
for yr in (2030, 2040, 2050):
    if "DateOut" in fr.columns:
        alive = fr[(fr["DateOut"].isna()) | (fr["DateOut"] > yr)]
        print(yr, "alive by DateOut:", round(alive["Capacity"].sum(),1), "MW")
print("by country nuclear MW:", nuc.groupby(cc)["Capacity"].sum().round(0).to_dict())
