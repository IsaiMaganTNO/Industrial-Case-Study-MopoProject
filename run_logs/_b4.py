import pickle, pandas as pd
pd.set_option("display.width",95)
d=pickle.load(open("run_logs/retireall.pkl","rb"))
em=d["emis"]
print("== oil-eng / CCGT emissions by year ==")
m=em[em.tech.isin(["oil-eng","CCGT","CCGT+CC"])]
print(m.groupby(["tech","year"]).co2.sum().unstack().round(1).to_string())
print()
print("== emissions by category ==")
print(em.groupby(["category","year"]).co2.sum().unstack().round(0).to_string())
