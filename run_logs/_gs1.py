import pickle, pandas as pd
new=pickle.load(open(r"run_logs\gascap.pkl","rb"))
old=pickle.load(open(r"run_logs\co2bidir.pkl","rb"))
def meth(d):
    s=d["supply"]; m=s[s.carrier=="methane"]
    return m.groupby(["tech","year"])["energy"].sum().unstack().fillna(0)/1000
print("=== P1 methane supply TWh (baseline -> gascap) ===")
print("BASELINE:"); print(meth(old).round(1).to_string())
print("GASCAP:");   print(meth(new).round(1).to_string())
print()
for y in [2030,2040,2050]:
    a=old["supply"].query("carrier=='methane' and year==@y")["energy"].sum()/1000
    b=new["supply"].query("carrier=='methane' and year==@y")["energy"].sum()/1000
    print(f"  {y}: {a:7.1f} -> {b:7.1f} TWh  ({b/a-1:+.1%})")
