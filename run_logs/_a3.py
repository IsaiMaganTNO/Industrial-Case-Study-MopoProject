import pickle, pandas as pd, re
pd.set_option("display.width",95)
d = pickle.load(open("run_logs/retireall.pkl","rb"))
fl, inv, sup = d["fleet"], d["inv"], d["supply"]
pat = re.compile(r"batt|iron-air|pump|phs|hydro-res|storage|sto|elect?roly|pem|aec|soec",re.I)
print("== fleet tech matching storage/electrolyser patterns ==")
m = fl[fl.tech.str.contains(pat)]
print(m.groupby(["tech","category","year"]).units.sum().unstack().round(3).to_string())
print()
print("== all techs in category 'other' (2050) ==")
o = fl[(fl.category=="other")&(fl.year==2050)]
print(o.groupby("tech").units.sum().sort_values(ascending=False).round(2).to_string())
