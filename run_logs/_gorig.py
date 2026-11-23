import pandas as pd
pd.set_option("display.width",200)
for f in [r"data\Gas\Gas_Sectors_Dataset.xlsx", r"data\Gas\Gas_Sectors_Dataset_IC1_placeholder.xlsx.bak"]:
    print("#"*100); print(f)
    try:
        d=pd.read_excel(f,"CH4_Production")
    except Exception as e:
        print("  err",e); continue
    print(d.shape, list(d.columns))
    c=[x for x in d.columns if "apacity" in str(x)][0]
    print(d.groupby(["technology","To Country"])[c].first().to_string())
