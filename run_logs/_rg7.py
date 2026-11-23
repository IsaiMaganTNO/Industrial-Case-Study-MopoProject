import pandas as pd
o=pd.read_csv(r"data\Biomass\db_biomass_ener_mopo.csv",low_memory=False)
n=pd.read_csv(r"data\Biomass\db_biomass_ener_mopo_mixedres.csv",low_memory=False)
print("cols identical:",list(o.columns)==list(n.columns))
print("rows:",len(o),len(n))
print("quantity sum identical:",abs(o.quantity.sum()-n.quantity.sum())<1e-6)
print("dash remaining in new nuts3:",(n["nuts3"].astype(str)=="-").sum())
m=pd.read_excel(r"data-pipelines\europe\region_transformation_IC1.xlsx",sheet_name="NUTS3_IC1")
m["source"]=m["source"].astype(str).str.strip()
mapped=set(m["source"])
six=n[n.nuts0.isin(["BE","NL","DE","DK","NO","UK"])]
unmapped=sorted(set(six["nuts3"].astype(str))-mapped)
print("UNMAPPED among 6 countries:",len(unmapped),unmapped[:10])
# expected totals after split
split=m.groupby("source")["target"].nunique()
six=six.copy(); six["sp"]=six["nuts3"].map(split).fillna(0)
print("\nrows with split 0 (dropped):",(six.sp==0).sum())
six["q"]=six["quantity"]/six["sp"].replace(0,np.nan) if False else six["quantity"]
med=six[six.scenario=="medium"]
print("\nexpected medium PJ per country after mapping (sum of quantity, split-preserving):")
print(med.groupby("nuts0")["quantity"].sum().to_string())
