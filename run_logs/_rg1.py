import pandas as pd
df=pd.read_csv(r"data\Biomass\db_biomass_ener_mopo.csv",low_memory=False)
print("rows",len(df))
sub=df[df["nuts0"].isin(["DE","DK","NO","UK"])]
print("rows for 4 countries:",len(sub))
for c in ["DE","DK","NO","UK"]:
    d=df[df["nuts0"]==c]
    n3=sorted(set(d["nuts3"].astype(str)))
    print("%s rows=%-7d nuts3 n=%-4d sample=%s"%(c,len(d),len(n3),n3[:5]))
    print("     dash-nuts3 rows:",(d["nuts3"].astype(str)=="-").sum(),"scenarios:",sorted(set(d["scenario"])))
# totals PJ by scenario
print("\nPJ totals by country/scenario:")
t=sub.groupby(["nuts0","scenario"])["quantity"].sum()
print(t.to_string())
print("\nBE/NL for reference:")
print(df[df["nuts0"].isin(["BE","NL"])].groupby(["nuts0","scenario"])["quantity"].sum().to_string())
