import pickle, pandas as pd
pd.set_option("display.width",95)
d=pickle.load(open("run_logs/retireall.pkl","rb"))
sup=d["supply"]; emis=d["emis"]
el=sup[sup.carrier=="electricity"]
print("== electricity supply by category (TWh-equiv) ==")
print(el.groupby(["category","year"]).energy.sum().unstack().round(1).to_string())
print()
print("== electricity by tech 2050 top 15 ==")
t=el[el.year==2050].groupby("tech").energy.sum().sort_values(ascending=False)
print(t.head(15).round(1).to_string())
print()
print("== total CO2 by category ==")
print(emis.groupby(["category","year"]).co2.sum().unstack().round(0).to_string())
print()
print("== net CO2 total ==")
print(emis.groupby("year").co2.sum().round(0).to_string())
