import sys; sys.argv=["x","_"]; sys.path.insert(0,"tools")
import warnings; warnings.filterwarnings("ignore")
import make_deck_final3 as T, pandas as pd
K=T.K
for k in K:
    print("=====",k, T.SH[k])
    print(" offwind",T.sup(k,lambda s:s.category=="wind offshore")," nuc",T.sup(k,lambda s:s.tech.str.startswith("nuclear")))
    print(" ely",T.sup(k,lambda s:(s.carrier=="hydrogen")&(s.category=="electrolysis"))," LH2",T.sup(k,lambda s:s.tech=="LH2-terminal"))
    print(" LNG",T.sup(k,lambda s:s.tech=="LNG-terminal")," biomethane",T.sup(k,lambda s:(s.carrier=="methane")&s.tech.str.startswith("bio")))
    print(" gas sup/imp/exp/use",[round(x,1) for x in T.gas_use(k)])
    s=T.sel(k,"supply"); s=s[(s.carrier=="heat")&(s.energy>0)]; print(" heat",(s.groupby(["cn","tech"]).energy.sum()/1e3).round(1).loc[lambda z:z>0.5].to_dict())
    b=T.X[k]["bio"].query("year==2050"); print(" bio",(b.groupby(["c","unit"]).v.sum()/1e3).round(1).loc[lambda z:z>0.5].to_dict())
    p=T.sel(k,"prod"); print(" prod",(p[p.sector.isin(["steel (primary)","olefins","cement","ammonia","glass (container)"])].groupby(["sector","cn","tech"]).output.sum()/1e3).round(2).loc[lambda z:z>0.01].to_dict())
    c=T.sel(k,"co2net"); c=c[c.role=="captured"]; print(" cap",(c.groupby(["source","cn"]).co2.sum()/1e3).round(1).to_dict())
    print(" co2dest st/u/ex/em",[round(x,1) for x in T.co2dest(k)])
    print(" renew",{l:T.fleet(k,p) for l,p in T.RF})
    x=T.X[k]["xb"].query("year==2050"); CN=T.CN
    for car in ["elec","CH4","H2","CO2"]:
        y=x[x.car==car]; print(" trade",car,"imp",round(y[~y.o.isin(CN)&y.d.isin(CN)].v.sum()/1e3,1),"exp",round(y[y.o.isin(CN)&~y.d.isin(CN)].v.sum()/1e3,1))
