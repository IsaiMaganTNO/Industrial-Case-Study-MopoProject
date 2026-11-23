import pandas as pd
p = r"data-pipelines/europe/_ines-builder/region_transformation.xlsx"
xl = pd.ExcelFile(p)
print("SHEETS:", len(xl.sheet_names))
for s in ["IC1","PECD1"]:
    df = xl.parse(s)
    print("---", s, df.shape, list(df.columns))
    print(df.head(25).to_string(max_colwidth=22))
