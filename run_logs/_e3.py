import pickle, pandas as pd
pd.set_option("display.width",200)
new=pickle.load(open(r"run_logs\gascap.pkl","rb"))
old=pickle.load(open(r"run_logs\co2bidir.pkl","rb"))
print("=== INDUSTRIAL PRODUCTION by sector x fuel, 2050 (prod frame) ===")
for lbl,d in [("base",old),("gascap",new)]:
    p=d["prod"]; p=p[p.year==2050]
    g=p.groupby(["sector","fuel"])["output"].sum()
    print(f"--- {lbl}"); print(g[g>1].round(0).to_string())
