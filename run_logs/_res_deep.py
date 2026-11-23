import pickle, pandas as pd
pd.set_option("display.width",250); pd.set_option("display.max_rows",300)
R={"IC1":"nb_ccslow_ccu_cap16_dac0","CTRY":"nb_ctry_ccslow_ccu_cap16_dac0"}
D={k:pickle.load(open(rf"run_logs\{v}_NLBE.pkl","rb")) for k,v in R.items()}
F={k:pickle.load(open(rf"run_logs\{v}.pkl","rb")) for k,v in R.items()}
def tab(fn):
    return pd.DataFrame({(k,y):fn(k,y) for k in D for y in (2030,2040,2050)}).fillna(0)
print("== supply carrier/category by year (TWh)")
t=tab(lambda k,y:D[k]["supply"].query("year==@y and energy>0").groupby(["carrier","category"]).energy.sum()/1e3); print(t.round(1).to_string())
print("== fleet by category (GW)")
print(tab(lambda k,y:D[k]["fleet"].query("year==@y").groupby("category").units.sum()).round(2).to_string())
print("== fleet key techs by year")
t=tab(lambda k,y:D[k]["fleet"].query("year==@y").groupby("tech").units.sum())
m=t.index.str.contains(r"^(PEM|nuclear|CCGT|gas-boiler|air-heat|ground-heat|REF-SMR|\(H2\)MeOH|bio-diges|battery|electric-heat|LNG|LH2)",regex=True)
print(t[m].round(2).to_string())
print("== prod by sector/tech by year (kt)")
t=tab(lambda k,y:D[k]["prod"].query("year==@y").groupby(["sector","tech"]).output.sum()); print(t[(t.abs()>1).any(axis=1)].round(0).to_string())
print("== co2 captured by source")
print(tab(lambda k,y:D[k]["co2net"].query("year==@y and role=='captured'").groupby("source").co2.sum()/1e3).round(2).to_string())
print("== co2 store by site 2050"); print(pd.DataFrame({k:D[k]["co2store"].query("year==2050").groupby(["reservoir","region"]).co2.sum()/1e3 for k in D}).round(2).to_string())
print("== IC1 PEM / HP / nuclear by region 2050")
f=D["IC1"]["fleet"].query("year==2050"); f=f[f.tech.str.contains(r"^(PEM|nuclear|ground-heat|air-heat|\(H2\)MeOH|CCGT-H2|REF-SMR)",regex=True)]
print(f.pivot_table(index="region",columns="tech",values="units",aggfunc="sum").round(2).fillna(0).to_string())
print("== CTRY same"); f=D["CTRY"]["fleet"].query("year==2050"); f=f[f.tech.str.contains(r"^(PEM|nuclear|ground-heat|air-heat|\(H2\)MeOH|CCGT-H2|REF-SMR)",regex=True)]
print(f.pivot_table(index="region",columns="tech",values="units",aggfunc="sum").round(2).fillna(0).to_string())
print("== OBJ"); print(pd.DataFrame({k:F[k]["obj"]/1e6 for k in F}).assign(d=lambda x:x.CTRY-x.IC1).round(4).to_string())
print("== inv cats summed over years (new units)"); print(pd.DataFrame({k:D[k]["inv"].groupby("category").units.sum() for k in D}).round(2).to_string())
