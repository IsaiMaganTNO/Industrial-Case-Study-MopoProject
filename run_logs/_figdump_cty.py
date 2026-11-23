import pandas as pd, glob, os
pd.set_option("display.width",250)
for f in sorted(glob.glob(r"results_2050_analysis\data\[AB][1-4]_*.csv")):
    d=pd.read_csv(f); n=os.path.basename(f)[:2]
    cols=["run","year"] if n[0]=="A" else ["run"]
    t=d.pivot_table(index=["country","item"],columns=cols,values="twh",aggfunc="sum").round(0)
    t=t[(t.abs()>0.5).any(axis=1)]
    print("=====",n); print(t.to_string())
