import pandas as pd
x=pd.read_excel(r"data-pipelines\europe\_power\assumptions.xlsx", sheet_name=None)
for s,df in x.items():
    m=df.astype(str).apply(lambda col: col.str.contains("nuclear",case=False)).any(axis=1)
    if m.any(): print("==",s); print(df[m].to_string()[:3000])
