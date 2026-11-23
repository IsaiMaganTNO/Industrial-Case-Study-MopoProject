import pickle, pandas as pd
pd.set_option("display.width",220); pd.set_option("display.max_rows",200)
d=pickle.load(open(r"run_logs\mr_ccslow_ccu_cap16_dac0_NLBE.pkl","rb"))
s=d["supply"]; s=s[(s.year==2050)&(s.carrier=="hydrogen")]
print(s.groupby(["tech"]).energy.sum().div(1e3).round(1).sort_values())
