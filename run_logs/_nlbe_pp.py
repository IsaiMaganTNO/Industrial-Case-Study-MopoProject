import pandas as pd
df=pd.read_csv(r"data\Energy_Conversion\powerplants.csv", low_memory=False)
q=df[df.Country.isin(["Belgium","Netherlands"])&df.Fueltype.str.contains("uclear|Hard Coal|Natural Gas|Waste",case=False,na=False)&df.DateOut.isna()]
print(q.groupby(["Country","Fueltype"]).agg(MW=("Capacity","sum"),n=("Capacity","size"),din_min=("DateIn","min"),din_max=("DateIn","max"),din_nan=("DateIn",lambda s:s.isna().sum())).round(0).to_string())
n=df[(df.Country=="Belgium")&df.Fueltype.str.contains("uclear",na=False)][["Name","Capacity","DateIn","DateOut"]]; print(n.to_string())
