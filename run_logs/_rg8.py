import pandas as pd
n=pd.read_csv(r"data\Biomass\db_biomass_ener_mopo_mixedres.csv",low_memory=False)
m=pd.read_excel(r"data-pipelines\europe\region_transformation_IC1.xlsx",sheet_name="NUTS3_IC1")
m["source"]=m["source"].astype(str).str.strip()
mapped=set(m["source"])
six=n[n.nuts0.isin(["BE","NL"])]
un=sorted(set(six["nuts3"].astype(str))-mapped)
print("unmapped BE/NL nuts3:",un)
med=six[six.scenario=="medium"]
print("\nPJ at these codes (medium):")
print(med[med["nuts3"].astype(str).isin(un)].groupby("nuts3")["quantity"].sum().to_string())
print("total lost PJ:",med[med["nuts3"].astype(str).isin(un)]["quantity"].sum())
print("\nare their NUTS2 parents in the map?")
for u in un:
    print("  ",u,"parent",u[:4],"mapped:",u[:4] in mapped, "| targets for parent:",sorted(set(m.loc[m.source==u[:4],"target"])))
