import pandas as pd
XLS=r"data-pipelines\europe\region_transformation_IC1.xlsx"
sheets=pd.read_excel(XLS,sheet_name=None)
m=sheets["NUTS3_IC1"].copy()
m["source"]=m["source"].astype(str).str.strip()
m["target"]=m["target"].astype(str).str.strip()
mapped=set(m["source"])
orig=m[m["source"].str[:2].isin(["BE","NL"]) & ~m["source"].str.contains("~")]
n=pd.read_csv(r"data\Biomass\db_biomass_ener_mopo_mixedres.csv",low_memory=False)
un=sorted(set(n.loc[n.nuts0.isin(["BE","NL"]),"nuts3"].astype(str))-mapped)
rows=[]
for u in un:
    tg=sorted(set(orig.loc[orig["source"].str[:4]==u[:4],"target"]))
    assert tg, u
    for t in tg: rows.append((u,t,1,1))
    print("%s -> %s"%(u,tg))
add=pd.DataFrame(rows,columns=["source","target","area","population"])
out=pd.concat([m[["source","target","area","population"]],add],ignore_index=True).drop_duplicates(subset=["source","target"])
print("rows",len(m),"->",len(out))
sheets["NUTS3_IC1"]=out
with pd.ExcelWriter(XLS,engine="openpyxl") as w:
    for k,d in sheets.items(): d.to_excel(w,sheet_name=k,index=False)
# verify
m2=pd.read_excel(XLS,sheet_name="NUTS3_IC1"); m2["source"]=m2["source"].astype(str).str.strip()
six=n[n.nuts0.isin(["BE","NL","DE","DK","NO","UK"])]
print("UNMAPPED now:",len(set(six["nuts3"].astype(str))-set(m2["source"])))
