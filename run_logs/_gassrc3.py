import pandas as pd
d=pd.read_excel(r"data\Gas\Gas_Sectors_Dataset_IC1_placeholder.xlsx","CH4_Production")
col="Capacity 2030 (GWh/d) "
print(d.groupby(["technology","To Country"])[col].first().to_string())
print()
for tech,reg,v in [("LNG-terminal","BEC1",83.625),("LNG-terminal","NLC1",None),("gas-extraction","NLC1",None)]:
    sub=d[(d.technology==tech)&(d["To Country"]==reg)]
    if len(sub):
        g=sub[col].iloc[0]
        print(f"{tech:16s} {reg} {g:9.4f} GWh/d  /24 = {g/24:8.4f} GW")
