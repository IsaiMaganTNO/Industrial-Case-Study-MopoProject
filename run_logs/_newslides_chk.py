import pickle, pandas as pd, numpy as np
pd.set_option("display.width",250)
R={"IC1":"nb_ccslow_ccu_cap16_dac0","CTRY":"nb_ctry_ccslow_ccu_cap16_dac0"}
D={k:pickle.load(open(rf"run_logs\{v}_NLBE.pkl","rb")) for k,v in R.items()}
X={k:pd.read_pickle(rf"run_logs\{v}_xbbio.pkl") for k,v in R.items()}
def cc(df):
    r=df.region.astype(str).str[:2]; off=df.tech.astype(str).str.extract(r"_NS(NL|BE)")[0]; return r.where(df.region.notna(),off)
for k in D:
    d=D[k]; print("=====",k)
    s=d["supply"].query("year==2050 and energy>0"); s=s.assign(cn=cc(s))
    for lbl,q in [("offwind",s.category=="wind offshore"),("elys",(s.carrier=="hydrogen")&(s.category=="electrolysis")),("nuc",s.tech.str.startswith("nuclear")),
                  ("HP",(s.carrier=="heat")&(s.category=="electrification (heat pumps)")),("LNG",s.tech=="LNG-terminal"),("biomethane",(s.carrier=="methane")&s.tech.str.startswith("bio"))]:
        print(lbl,(s[q].groupby("cn").energy.sum()/1e3).round(1).to_dict())
    p=d["prod"].query("year==2050"); p=p.assign(cn=cc(p))
    for sec in ["steel (primary)","olefins"]: print(sec,(p[p.sector==sec].groupby(["cn","tech"]).output.sum()/1e3).round(2).to_dict())
    c=d["co2net"].query("year==2050 and role=='captured'"); c=c.assign(cn=cc(c)); print("co2",(c.groupby(["source","cn"]).co2.sum()/1e3).round(2).to_dict())
    f=d["fleet"].query("year==2050"); f=f.assign(cn=cc(f)); print("renew",(f[f.tech.str.contains(r"^(?:PEM|\(H2\)MeOH|bio-diges|\(H2\)NH3|\(BM\)NH3|methanation)")].groupby(["cn","tech"]).units.sum()).round(2).to_dict())
    print("bio",(X[k]["bio"].groupby(["c","year"]).v.sum()/1e3).round(1).to_dict())
    print("bio units 2050",(X[k]["bio"].query("year==2050").groupby("unit").v.sum()/1e3).round(1).loc[lambda z:z>0].to_dict())
    x=X[k]["xb"].query("year==2050"); nb=["NL","BE"]
    for car in ["elec","CH4","H2","CO2"]:
        y=x[x.car==car]; print(car,"imp",round(y[~y.o.isin(nb)&y.d.isin(nb)].v.sum()/1e3,1),"exp",round(y[y.o.isin(nb)&~y.d.isin(nb)].v.sum()/1e3,1),"NL<->BE",round(y[y.o.isin(nb)&y.d.isin(nb)].v.sum()/1e3,1))
