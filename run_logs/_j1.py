import pickle, pandas as pd
pd.set_option("display.width",95)
B=pickle.load(open("run_logs/hcco2.pkl","rb"))
s=B["supply"]; e=s[(s.carrier=="electricity")&(s.year==2050)]
g=e.groupby("tech").energy.sum().sort_values(ascending=False)
g=g[g.abs()>1]
tot=g.sum()
df=pd.DataFrame({"GWh":g.round(1),"pct":(100*g/tot).round(1)})
print("== 2050 electricity supply, hcco2 ==")
print(df.to_string())
print("TOTAL", round(tot,1))
print()
f=B["fleet"]; m=f[(f.year==2050)&(f.tech.str.contains("wind|solar",case=False))]
print("== VRE fleet 2050 (units) ==")
print(m.groupby("tech").units.sum().round(3).to_string())
print()
print("== VRE by region 2050 ==")
print(m.groupby(["tech","region"]).units.sum().round(2).unstack(0).fillna(0).to_string())
