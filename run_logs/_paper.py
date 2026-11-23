import pickle,pandas as pd
R={"IC1":"nb_ccslow_ccu_cap16_dac0","CTRY":"nb_ctry_ccslow_ccu_cap16_dac0"}
for k,v in R.items():
    p=pickle.load(open(rf"run_logs\{v}_NLBE.pkl","rb"))["prod"].query("sector=='paper'")
    print(k); print(p.groupby(["year","tech"]).output.sum().unstack(0).round(1).to_string())
