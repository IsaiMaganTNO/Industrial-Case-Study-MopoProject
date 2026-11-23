import pandas as pd
for f in [r"data-pipelines\europe\region_transformation_IC1.xlsx",r"data-pipelines\europe\region_transformation.xlsx"]:
    x=pd.ExcelFile(f); print("=====",f,x.sheet_names)
    for s in x.sheet_names:
        d=x.parse(s); print("--",s,d.shape); print(d.head(6).to_string()[:900])
