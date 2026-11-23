import pickle, pandas as pd
pd.set_option("display.width",250)
df=pickle.load(open(r"run_logs\mixedres_connflow.pkl","rb"))
ends=df.groupby("conn").c.agg(lambda s: tuple(sorted(set(s.dropna()))))
x=df[df.conn.map(lambda c: len(ends[c])==2)]
inn=x[x.dir=="to_node"].groupby(["car","c","year"]).val.sum()
out=x[x.dir=="from_node"].groupby(["car","c","year"]).val.sum()
imp=inn.sub(out,fill_value=0)
t=(imp.unstack()/1e3).round(1)
print("=== NET CROSS-BORDER IMPORT (TWh, + import) - corrected")
print(t[t.abs().max(axis=1)>0.05].to_string())
print("\n=== elec interconnector flows 2050 involving BE/NL (TWh)")
e=x[(x.car=="elec")&(x.year==2050)&(x.dir=="to_node")]
e=e.assign(frm=e.conn.str.split("_elec_").str[0])
print((e.groupby(["conn","c"]).val.sum()/1e3).round(1).to_string())
