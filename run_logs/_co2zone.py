import pickle, pandas as pd
pd.set_option("display.width",250)
for k,v in {"IC1":"nb_ccslow_ccu_cap16_dac0","CTRY":"nb_ctry_ccslow_ccu_cap16_dac0"}.items():
    d=pickle.load(open(rf"run_logs\{v}_NLBE.pkl","rb"))
    c=d["co2net"].query("year==2050")
    print("==",k); print((c.pivot_table(index="region",columns="role",values="co2",aggfunc="sum")/1e3).round(2).fillna(0).to_string())
    x=pd.read_pickle(rf"run_logs\{v}_xbbio.pkl"); print(type(x), getattr(x,"columns",None))
