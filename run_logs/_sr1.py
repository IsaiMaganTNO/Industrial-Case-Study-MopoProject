import pandas as pd
p=r"data-pipelines\europe\_ines-builder\region_transformation.xlsx"
xl=pd.ExcelFile(p)
print("SHEETS:", xl.sheet_names)
for s in xl.sheet_names:
    d=xl.parse(s)
    print("---",s,d.shape,list(d.columns))
    print(d.head(3).to_string()[:400])
