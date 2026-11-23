import pickle, pandas as pd, re, csv
pd.set_option("display.width",95); pd.set_option("display.max_rows",400)
d = pickle.load(open("run_logs/retireall.pkl","rb"))
fl = d["fleet"]
fams = ["ceramics-and-other-non-metalic-minerals","food-beverages-tobacco",
 "leather-and-textile","machinery-equipment","other-chemicals",
 "other-industrial-sectors","other-non-ferrous-metals","pharmaceuticals",
 "printing-and-media","transport-equipment","wood-and-wood-products",
 "aluminium-primary","pulp","paper"]
for f in fams:
    sub = fl[fl.tech.str.startswith(f)]
    if sub.empty:
        print("### "+f+"  -- NO FLEET ROWS"); continue
    t = sub.groupby(["tech","year"]).units.sum().unstack().round(3)
    print("### "+f)
    print(t.fillna(0).to_string())
    print()
