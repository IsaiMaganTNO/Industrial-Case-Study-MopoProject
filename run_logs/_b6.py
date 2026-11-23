import pickle, pandas as pd
pd.set_option("display.width",95)
d=pickle.load(open("run_logs/retireall.pkl","rb"))
fl,inv,sup=d["fleet"],d["inv"],d["supply"]
print("== SMR/PEM/LH2 fleet ==")
m=fl[fl.tech.str.contains("SMR|PEM|LH2",case=False,na=False)]
print(m.groupby(["tech","year"]).units.sum().unstack().round(3).to_string())
print()
print("== SMR/PEM/LH2 new investment ==")
mi=inv[inv.tech.str.contains("SMR|PEM|LH2",case=False,na=False)]
print(mi.groupby(["tech","year"]).units.sum().unstack().round(3).to_string()
      if not mi.empty else "  none")
print()
print("== H2 supply TWh ==")
h2=sup[sup.carrier.str.contains("hydrogen",case=False,na=False)]
print(h2.groupby(["tech","year"]).energy.sum().unstack().round(1).to_string())
