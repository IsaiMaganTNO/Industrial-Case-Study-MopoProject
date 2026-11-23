import pickle,pandas as pd
pd.set_option("display.width",250)
R={"IC1":"nb_ccslow_ccu_cap16_dac0","MR":"mr_ccslow_ccu_cap16_dac0"}
D={k:pickle.load(open(rf"run_logs\{v}_NLBE.pkl","rb")) for k,v in R.items()}
X={k:pd.read_pickle(rf"run_logs\{v}_xbbio.pkl") for k,v in R.items()}
def grp(t):
    for a,b in [("wind-off","offshore"),("wind-on","onshore"),("solar","solar"),("nuclear","nuclear"),("CCGT-H2","H2 turbine"),("battery","battery"),("RoR","hydro"),("PEM","PEM"),("LH2","LH2"),("LNG","LNG"),("bio-diges","biomethane"),("ground-heat","ground HP"),("air-heat","air HP"),("electric-heat","el heating"),("bio-boiler","bio boiler"),("gas-boiler","gas boiler"),("H2-boiler","H2 boiler")]:
        if t.startswith(a): return b
    return t
for car in ["electricity","hydrogen","heat","methane"]:
    t=pd.DataFrame({k:D[k]["supply"].query("year==2050 and carrier==@car and energy>0").pipe(lambda s:s.groupby(s.tech.map(grp)).energy.sum()/1e3) for k in R}).fillna(0)
    t["d"]=t.MR-t.IC1; print("==",car); print(t.round(1).to_string()); print(t.sum().round(1).to_dict())
for k in R:
    x=X[k]["xb"].query("year==2050"); CN=["NL","BE"]
    for car in ["elec","CH4","H2","CO2"]:
        q=x[x.car==car]; im=q[~q.o.isin(CN)&q.d.isin(CN)].v.sum()/1e3; ex=q[q.o.isin(CN)&~q.d.isin(CN)].v.sum()/1e3
        print(k,car,"imp",round(im,1),"exp",round(ex,1),"net",round(im-ex,1))
    print(k,"emis",round(D[k]["emis"].query("year==2050").co2.sum()/1e3,1),"captured",round(D[k]["co2net"].query("year==2050 and role=='captured'").co2.sum()/1e3,1))
    b=X[k]["bio"].query("year==2050"); print(k,"bio by use",b.groupby(b.unit.str[:10]).v.sum().div(1e3).round(1).to_dict())
for sec in sorted(D["IC1"]["prod"].sector.unique()):
    rows={k:(lambda p:p.groupby("tech").output.sum()/p.output.sum()*100)(D[k]["prod"].query("year==2050 and sector==@sec")) for k in R}
    t=pd.DataFrame(rows).fillna(0)
    if (t.IC1-t.MR).abs().max()>0.5: print("==",sec); print(t.round(1).to_string())
