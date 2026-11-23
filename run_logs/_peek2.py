import pickle,pandas as pd
u=pd.read_pickle(r"run_logs\_use_elec_h2_all.pkl"); d=pd.read_pickle(r"run_logs\_elec_dem_xb_all.pkl")
print(d.tech.unique()); print(d[(d.year==2050)&(d.tech=="net import")].groupby("run").twh.sum())
x=pd.read_pickle(r"run_logs\mr_ccslow_ccu_cap16_dac0_xbbio.pkl")["xb"]; print(x.head()); x=x.query("year==2050 and car=='elec'")
CN=["NL","BE"]; print("MR xb import",x[~x.o.isin(CN)&x.d.isin(CN)].v.sum()/1e3,"export",x[x.o.isin(CN)&~x.d.isin(CN)].v.sum()/1e3)
print(u.tech.str.replace(r"_[A-Z]{2}C?\d*.*$","",regex=True).unique()[:200])
