import pickle, pandas as pd
pd.set_option("display.width",250); pd.set_option("display.max_rows",400)
R={"old_IC1":"nb_ccslow","new_IC1":"nb_ccslow_ccu_cap16_dac0","old_CTRY":"nb_ctry_ccslow","new_CTRY":"nb_ctry_ccslow_ccu_cap16_dac0"}
D={k:pickle.load(open(rf"run_logs\{v}.pkl","rb")) for k,v in R.items()}
def piv(key,idx,val,yr=2050,flt=None):
    out={}
    for k,d in D.items():
        x=d[key]; x=x[x.year==yr]
        if flt is not None: x=flt(x)
        out[k]=x.groupby(idx)[val].sum()
    return pd.DataFrame(out).fillna(0)
print("== unabated elec 2050"); print((piv("supply","tech","energy",flt=lambda x:x[(x.carrier=="electricity")&(x.category.isin(["unabated fossil","other"]))])/1e3).round(1).to_string())
print("== FLEET 2050 key techs")
f=piv("fleet","tech","units"); m=f.index.str.contains("wind-off|PEM|nucl|SMR|LH2|LNG|boil|heatpump|DAC|MeOH|CCGT|methan|bio",case=False)
print(f[m].round(2)[(f[m].abs()>0.01).any(axis=1)].to_string())
print("== CO2 used by tech 2050"); c=piv("co2net",["role","tech"],"co2"); print(c.loc["used / injected"].round(0)[(c.loc["used / injected"].abs()>50).any(axis=1)].to_string())
print("== OBJ delta"); print(sum(D["new_IC1"]["obj"])-sum(D["old_IC1"]["obj"]), sum(D["new_CTRY"]["obj"])-sum(D["old_CTRY"]["obj"]))
