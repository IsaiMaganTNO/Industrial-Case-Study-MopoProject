import pickle, pandas as pd
pd.set_option("display.width",95)
B=pickle.load(open("run_logs/hcco2.pkl","rb"))
p=B["prod"]
g=p.groupby(["sector","year","fuel"]).output.sum().reset_index()
tot=g.groupby(["sector","year"]).output.transform("sum")
g["pct"]=(100*g.output/tot).round(1)
for s in sorted(g.sector.unique()):
    sub=g[(g.sector==s)&(g.year.isin([2030,2050]))].pivot_table(index="fuel",columns="year",values="pct").fillna(0)
    print("###",s); print(sub.round(1).to_string()); print()
