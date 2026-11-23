import pickle, pandas as pd
pd.set_option("display.width",250)
for n in ["mr_ccslow_dac0","mr_ccslow_ccu_cap16_dac0"]:
    F=pickle.load(open(rf"run_logs\{n}.pkl","rb")); D=pickle.load(open(rf"run_logs\{n}_NLBE.pkl","rb")); X=pd.read_pickle(rf"run_logs\{n}_xbbio.pkl")
    print("=====",n,"obj",round(F["obj"].sum()))
    p=F["co2pipe"]; print(" co2pipe cols",list(p.columns))
    p=p[p.year==2050]; nb=lambda s:s.str[:2].isin(["NL","BE"])
    print(" CO2 export NL+BE->other 2050 (Mt)", round((p[nb(p.origin)&~nb(p.dest)].co2.sum()-p[~nb(p.origin)&nb(p.dest)].co2.sum())/1e3,2))
    print(" by dest", (p[nb(p.origin)&~nb(p.dest)].groupby("dest").co2.sum()/1e3).round(2).to_dict())
    x=X["xb"].query("year==2050 and car=='CO2'"); print(" xb CO2", (x.groupby(["o","d"]).v.sum()/1e3).round(2).to_dict())
    print(" NL+BE stored", round(D["co2store"].query("year==2050").co2.sum()/1e3,2), "captured", round(D["co2net"].query("year==2050 and role=='captured'").co2.sum()/1e3,2))
    print(" net NL+BE emis", round(D["emis"].query("year==2050").co2.sum()/1e3,2))
    s=D["supply"].query("year==2050 and energy>0")
    for lbl,q in [("offwind",s.category=="wind offshore"),("elys",(s.carrier=="hydrogen")&(s.category=="electrolysis")),("methane",s.carrier=="methane"),("HP",(s.carrier=="heat")&(s.category=="electrification (heat pumps)"))]:
        print(" ",lbl, round(s[q].energy.sum()/1e3,1))
