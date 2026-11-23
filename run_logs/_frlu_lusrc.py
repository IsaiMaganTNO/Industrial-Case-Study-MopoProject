import sqlite3, os
base = r"EU_case\.spinetoolbox\items"
d = sqlite3.connect(os.path.join(base, "industry_db", "industry_db.sqlite"))
names = [n for (n,) in d.execute("select name from entity")]
for cc in ("DE","FR","LU","BE"):
    s = sorted({n.split("__")[0] for n in names if n.endswith("__"+cc)})
    print(cc, len(s), s)
p = r"data\Energy_Conversion\powerplants.csv"
import pandas as pd
pp = pd.read_csv(p, low_memory=False)
cols = [c for c in pp.columns if c.lower() in ("country","fueltype","technology","capacity","capacity_mw")]
print(cols)
lu = pp[pp[[c for c in pp.columns if c.lower()=="country"][0]].astype(str).str.contains("Luxembourg|^LU$")]
print("LU plants:", len(lu)); print(lu[cols].groupby(cols[1:3] if len(cols)>2 else cols[1]).sum(numeric_only=True).to_string()[:1500])
