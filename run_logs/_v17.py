import pickle, pandas as pd
pd.set_option("display.width",92)
A=pickle.load(open(r"run_logs\vre15.pkl","rb"))
B=pickle.load(open(r"run_logs\gascap.pkl","rb"))
for y in [2030,2040,2050]:
    rows=[]
    for tag,F in [("gascap",B),("vre15",A)]:
        p=F["prod"]; p=p[p.year==y]
        g=p.groupby(["sector","fuel"]).output.sum()
        rows.append(g.rename(tag))
    t=pd.concat(rows,axis=1).fillna(0)
    t["d"]=t.vre15-t.gascap
    t=t[t.d.abs()>50].sort_values("d")
    if len(t): print(f"\n=== {y} industry fuel shifts ==="); print(t.round(0).to_string())
