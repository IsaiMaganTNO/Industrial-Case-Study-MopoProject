import pandas as pd
df=pd.read_csv(r"data\Biomass\db_biomass_ener_mopo.csv",low_memory=False)
# For dash-nuts3 rows, what is available?
d=df[df["nuts3"].astype(str)=="-"]
print("total dash rows",len(d))
import numpy as np
def lvl(r):
    if str(r["nuts2"])!="-": return "nuts2"
    if str(r["nuts1"])!="-": return "nuts1"
    if str(r["nuts0"])!="-": return "nuts0"
    return "none"
d=d.copy(); d["lvl"]=d.apply(lvl,axis=1)
print(d.groupby("lvl").size())
print("\nmedium PJ by level and country (6 countries):")
sub=d[(d.scenario=="medium")&(d.nuts0.isin(["BE","NL","DE","DK","NO","UK"]))]
print(sub.groupby(["nuts0","lvl"])["quantity"].sum().to_string())
print("\nfull medium totals incl dash:")
print(df[(df.scenario=="medium")&(df.nuts0.isin(["BE","NL","DE","DK","NO","UK"]))].groupby("nuts0")["quantity"].sum().to_string())
