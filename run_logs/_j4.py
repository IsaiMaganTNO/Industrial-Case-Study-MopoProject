import pickle, pandas as pd
B=pickle.load(open("run_logs/hcco2.pkl","rb"))
cn=B["co2net"]; f=B["fleet"]; s=B["supply"]
print("== DAC 2050 ==")
d=cn[(cn.tech=="DAC")&(cn.year==2050)]
print("  captured:", round(d.co2.sum(),1))
print("  fleet units:", round(f[(f.tech=='DAC')&(f.year==2050)].units.sum(),3))
print()
print("== captured by tech 2050 (top) ==")
m=cn[(cn.year==2050)&(cn.role=='captured')]
print(m.groupby("tech").co2.sum().sort_values(ascending=False).head(10).round(1).to_string())
print()
print("== CCGT vs CCGT+CC fleet 2050 ==")
print(f[(f.year==2050)&(f.tech.isin(['CCGT','CCGT+CC','OCGT','CCGT-H2']))].groupby("tech").units.sum().round(3).to_string())
print()
print("== DAC elec consumption? check supply/prod for DAC ==")
print("atm rows:", B["atm"].to_dict())
