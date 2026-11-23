import pandas as pd
for k in ['nb_v2','mr_fix']:
 b=pd.read_pickle(rf'run_logs\{k}_xbbio.pkl')['bio'];b=b[b.c.isin(['NL','BE'])];print(k,(b.groupby(['c','year']).v.sum()/1e3).round(0).to_dict())
