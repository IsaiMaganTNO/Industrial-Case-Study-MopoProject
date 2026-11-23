import pandas as pd
pp = pd.read_csv(r"data\Energy_Conversion\powerplants.csv", low_memory=False)
x = pp[(pp.Country=="France") & (pp.Fueltype.str.contains("Nuclear", na=False))]
print("FR nuclear plants:", len(x), "total GW:", round(x.Capacity.sum()/1000, 1))
cols = [c for c in pp.columns if "Date" in c or "Year" in c or "Commission" in c or "Retro" in c]
print(cols)
print(x[["Name","Capacity"]+cols].head(8).to_string())
