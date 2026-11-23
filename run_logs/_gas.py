import pandas as pd
p=r"data\Gas\Gas_Sectors_Dataset_IC1_placeholder.xlsx"
xl=pd.ExcelFile(p); print("SHEETS:",xl.sheet_names)
for s in xl.sheet_names:
    d=xl.parse(s)
    cols=[str(x).lower() for x in d.columns]
    if any(k in cols for k in ("from","to","node1","node2")):
        fc=d.columns[cols.index("from")] if "from" in cols else d.columns[cols.index("node1")]
        tc=d.columns[cols.index("to")] if "to" in cols else d.columns[cols.index("node2")]
        E=set(zip(d[fc],d[tc]))
        rev=sum(1 for a,b in E if (b,a) in E)
        print(f"  {s:30s} rows={len(d):5d} pairs={len(E):5d} rev_twin={rev}")
