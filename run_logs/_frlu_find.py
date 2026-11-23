import pandas as pd
e=pd.read_csv("2_elecmix_B_2050.csv"); print(e.pivot_table(index=["source"],columns=["run","country"],values="twh").round(0).loc[:,["MR","FRLU"]])
b=pd.read_csv("4_h2_elec_balance_B_2050.csv"); print(b.pivot_table(index=["carrier","side","item"],columns="run",values="twh",aggfunc="sum").round(1)[["MR","FRLU"]])
c=pd.read_csv("5_co2_capture_dest_B_2050.csv"); print(c.pivot_table(index=["kind","item"],columns="run",values="mt",aggfunc="sum").round(1)[["MR","FRLU"]])
r=pd.read_csv("1_industry_routes_B_2050.csv"); r=r[r.share_pct>0]; print(r[r.run.isin(["MR","FRLU"])].pivot_table(index=["sector","route_type"],columns="run",values="share_pct").round(0).fillna(0).query("MR!=FRLU"))
