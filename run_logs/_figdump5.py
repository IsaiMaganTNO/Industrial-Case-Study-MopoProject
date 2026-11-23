import pandas as pd
pd.set_option("display.width",250)
for n,f in (("A5","A5_industry_routes"),("B5","B5_industry_routes")):
    d=pd.read_csv(rf"results_2050_analysis\data\{f}.csv"); d=d[d.share_pct>=5]
    cols=["run","year"] if n=="A5" else ["run"]
    t=d.pivot_table(index=["sector","route_type"],columns=cols,values="share_pct",aggfunc="sum").round(0).fillna(0)
    print("=====",n); print(t.to_string())
