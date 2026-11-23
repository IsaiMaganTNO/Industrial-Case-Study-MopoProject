import pickle, pandas as pd
pd.set_option("display.width",250); pd.set_option("display.max_rows",300)
R={"IC1":"nb_ccslow_ccu_cap16_dac0","CTRY":"nb_ctry_ccslow_ccu_cap16_dac0","MR":"mr_ccslow_ccu_cap16_dac0","S1":"ctryco2B_mr_ccslow_ccu_cap16_dac0","S2":"rp10nb_mr_ccslow_ccu_cap16_dac0","S3":"mr_ccsopt_ccu_dac0","S4":"frlu_mr_ccslow_ccu_cap16_dac0"}
out={}
for k,v in R.items():
    s=pickle.load(open(rf"run_logs\{v}_NLBE.pkl","rb"))["supply"]; s=s[(s.year==2050)&(s.energy>0)&s.carrier.isin(["electricity","hydrogen"])]
    out[k]=s.groupby(["carrier","category","tech"]).energy.sum()/1e3
    x=pd.read_pickle(rf"run_logs\{v}_xbbio.pkl")["xb"]; x=x[x.year==2050]
    nb=lambda s: s.isin(["NL","BE"])
    for car in ["elec","H2"]:
        q=x[x.car==car]; imp=q[~nb(q.o)&nb(q.d)].v.sum()/1e3; exp=q[nb(q.o)&~nb(q.d)].v.sum()/1e3
        print(k,car,"imp",round(imp,1),"exp",round(exp,1))
t=pd.DataFrame(out).fillna(0); print(t[(t>0.5).any(axis=1)].round(1).to_string())
