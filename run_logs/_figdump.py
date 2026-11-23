import pandas as pd, glob, os
for f in sorted(glob.glob(r"results_2050_analysis\data\[AB][1-4]_*.csv")):
    d=pd.read_csv(f); n=os.path.basename(f)
    cols=[c for c in d.columns if c in("run","country","year","item")]
    v=[c for c in d.columns if c not in cols+["label"]][0]
    t=d.pivot_table(index="item",columns=["run","year"] if n[0]=="A" else ["run"],values=v,aggfunc="sum").round(0)
    t=t[(t.abs()>0.5).any(axis=1)]
    print("=====",n,list(d.columns)); print(t.to_string())
