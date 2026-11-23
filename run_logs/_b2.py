import pickle, pandas as pd
pd.set_option("display.width",95)
d=pickle.load(open("run_logs/retireall.pkl","rb"))
cn=d["co2net"]; sup=d["supply"]
print("== 2050 elec supply by tech (top) ==")
e=sup[(sup.carrier=="electricity")&(sup.year==2050)]
print(e.groupby("tech").energy.sum().sort_values(ascending=False).head(15).round(1).to_string())
print()
print("== LNG/LH2 terminal energy all years ==")
t=sup[sup.tech.str.contains("terminal",case=False,na=False)]
print(t.groupby(["tech","carrier","year"]).energy.sum().unstack().round(1).to_string())
