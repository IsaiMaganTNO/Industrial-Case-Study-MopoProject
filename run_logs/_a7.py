import pickle, pandas as pd
pd.set_option("display.width",95); pd.set_option("display.max_rows",500)
d = pickle.load(open("run_logs/retireall.pkl","rb"))
p = d["prod"]
g = p.groupby(["sector","year","fuel"]).output.sum().reset_index()
tot = g.groupby(["sector","year"]).output.transform("sum")
g["pct"] = (100*g.output/tot).round(1)
for s in sorted(g.sector.unique()):
    sub = g[g.sector==s].pivot_table(index="fuel",columns="year",values="pct")
    print("### "+str(s))
    print(sub.fillna(0).round(1).to_string())
    print()
