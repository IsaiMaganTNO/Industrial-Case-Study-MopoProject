import pickle, pandas as pd
pd.set_option("display.width",95)
A=pickle.load(open("run_logs/retireall.pkl","rb"))
B=pickle.load(open("run_logs/hcco2.pkl","rb"))
print("== fleet by category 2050 ==")
for lbl,d in (("retireall",A),("hcco2",B)):
    f=d["fleet"]; g=f[f.year==2050].groupby("category").units.sum()
    print(f"-- {lbl} --"); print(g.round(3).to_string())
print()
print("== electrolysis + e-fuel techs, hcco2 ==")
f=B["fleet"]
print(f[f.category.isin(["electrolysis","e-fuels / green chemicals"])].groupby(["tech","year"]).units.sum().round(3).to_string())
