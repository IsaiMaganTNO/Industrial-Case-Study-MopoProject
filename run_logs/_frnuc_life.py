import pandas as pd
df=pd.read_csv(r"data\Energy_Conversion\powerplants.csv", low_memory=False)
n=df[(df.Fueltype.str.contains("uclear",case=False,na=False))&(df.Country=="France")&(df.DateOut.isna())]
for L in (40,50,60):
    print("lifetime",L, {y: round(n[n.DateIn+L>y].Capacity.sum()/1000,2) for y in (2030,2040,2050)})
