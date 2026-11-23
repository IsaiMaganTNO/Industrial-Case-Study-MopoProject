import pandas as pd
df=pd.read_csv(r"data\Biomass\db_biomass_ener_mopo.csv",low_memory=False)
no=df[df["nuts0"]=="NO"]
print("NO unique nuts1/2/3:",sorted(set(no["nuts1"].astype(str))),sorted(set(no["nuts2"].astype(str))),sorted(set(no["nuts3"].astype(str))))
print(no[["type_id","nuts3","nuts2","nuts1","nuts0","quantity","scenario","maincat"]].head(6).to_string())
print("\nNO medium total PJ:",no[no.scenario=="medium"]["quantity"].sum())
# how do the dash rows look for DE
de=df[(df["nuts0"]=="DE")&(df["nuts3"]=="-")]
print("\nDE dash rows: nuts2:",sorted(set(de["nuts2"].astype(str)))[:6]," nuts1:",sorted(set(de["nuts1"].astype(str)))[:6])
print("DE dash medium PJ:",de[de.scenario=="medium"]["quantity"].sum(),"of total",df[(df.nuts0=="DE")&(df.scenario=="medium")]["quantity"].sum())
print("DE dash maincat:",sorted(set(de["maincat"])))
# BE/NL dash?
for c in ["BE","NL"]:
    d=df[(df["nuts0"]==c)&(df["nuts3"]=="-")]
    print(c,"dash rows:",len(d),"medium PJ:",d[d.scenario=="medium"]["quantity"].sum())
