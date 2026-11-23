import pickle, pandas as pd
pd.set_option("display.width",250); pd.set_option("display.max_rows",400)
R={"old_IC1":"nb_ccslow","new_IC1":"nb_ccslow_ccu_cap16_dac0","old_CTRY":"nb_ctry_ccslow","new_CTRY":"nb_ctry_ccslow_ccu_cap16_dac0"}
D={k:pickle.load(open(rf"run_logs\{v}.pkl","rb")) for k,v in R.items()}
print("== OBJ (M)"); print((pd.DataFrame({k:d["obj"] for k,d in D.items()})/1e6).round(3).to_string())
def piv(key,idx,val,yr=2050,flt=None):
    out={}
    for k,d in D.items():
        x=d[key]; x=x[x.year==yr]
        if flt is not None: x=flt(x)
        out[k]=x.groupby(idx)[val].sum()
    return pd.DataFrame(out).fillna(0)
print("== SUPPLY 2050 by carrier/category (TWh?)")
s=piv("supply",["carrier","category"],"energy"); print((s/1e3).round(1)[(s.abs()>1e3).any(axis=1)].to_string())
print("== SUPPLY 2050 top techs per carrier")
for c in ["electricity","heat","hydrogen","methane","natural gas"]:
    t=piv("supply","tech","energy",flt=lambda x,c=c:x[x.carrier==c])
    if len(t): print("--",c); print((t/1e3).round(1).loc[t.abs().max(axis=1).sort_values(ascending=False).index[:12]].to_string())
print("== CARRIERS", sorted(D["new_IC1"]["supply"].carrier.unique()))
print("== PROD 2050 by sector/tech")
p=piv("prod",["sector","tech"],"output"); print(p.round(1)[(p.abs()>1).any(axis=1)].to_string())
print("== CO2 2050 by role (kt)")
print(piv("co2net",["role"],"co2").round(0).to_string())
print(piv("co2net",["role","source"],"co2").round(0).to_string())
print("== CO2 stored by year (kt)")
print(pd.DataFrame({k:d["co2store"].groupby("year").co2.sum() for k,d in D.items()}).round(0).to_string())
print("== ATM"); print(pd.DataFrame({k:d["atm"].groupby("year").level.sum() for k,d in D.items()}).round(0).to_string())
print("== FLEET 2050 by category")
f=piv("fleet","category","units"); print(f.round(2).to_string())
print("== FLEET 2050 key techs")
f=piv("fleet","tech","units"); m=f.index.str.contains("wind-off|PEM|nucl|SMR|LH2|LNG|boil|HP|DAC|DC",case=False)
print(f[m].round(2)[(f[m].abs()>0.01).any(axis=1)].to_string())
