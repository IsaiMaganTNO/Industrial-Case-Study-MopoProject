import pandas as pd
pd.set_option("display.width",250); pd.set_option("display.max_rows",400)
d=pd.read_pickle(r"run_logs\_use_elec_h2_all.pkl"); d=d[d.year==2050]
t=d.pivot_table(index=["carrier","tech"],columns="run",values="twh",aggfunc="sum").fillna(0)
t=t[(t>1).any(axis=1)].round(1)
print(t[["IC1","CTRY","MR","S1","S2","S3","S4"]].to_string())
