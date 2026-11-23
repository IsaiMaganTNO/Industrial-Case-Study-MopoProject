import pickle,pandas as pd
pd.set_option("display.width",250); pd.set_option("display.max_rows",400)
R={"IC1":"nb_ccslow_ccu_cap16_dac0","CTRY":"nb_ctry_ccslow_ccu_cap16_dac0"}
D={k:pickle.load(open(rf"run_logs\{v}_NLBE.pkl","rb")) for k,v in R.items()}
def g(k,car):
    s=D[k]["supply"]; s=s[(s.year==2050)&(s.carrier==car)&(s.energy>0)]
    return s.groupby(s.tech.str.replace(r"_NS.*|-existing","",regex=True)).energy.sum()/1e3
for car in ["electricity","hydrogen","heat","methane"]:
    t=pd.DataFrame({k:g(k,car) for k in R}).fillna(0); t["d"]=t.CTRY-t.IC1; print("==",car); print(t.round(1).to_string()); print(t.sum().round(1).to_dict())
f={k:D[k]["fleet"].query("year==2050").groupby("tech").units.sum() for k in R}
t=pd.DataFrame(f).fillna(0); t["d"]=t.CTRY-t.IC1; print("== fleet diff"); print(t[t.d.abs()>0.05].round(2).to_string())
for sec in sorted(D["IC1"]["prod"].sector.unique()):
    rows={}
    for k in R:
        p=D[k]["prod"].query("year==2050 and sector==@sec"); rows[k]=p.groupby("tech").output.sum()/p.output.sum()*100
    t=pd.DataFrame(rows).fillna(0)
    if (t.IC1-t.CTRY).abs().max()>0.5: print("==",sec); print(t.round(1).to_string())
for k in R: print(k,"obj",D[k]["obj"])
