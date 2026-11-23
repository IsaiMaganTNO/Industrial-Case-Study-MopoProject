import pickle, pandas as pd
x=pickle.load(open(r"run_logs\mr_ccslow_dac0_xbbio.pkl","rb"))["xb"]
y=x.query("year==2050 and car=='CH4'").groupby(["o","d"]).v.sum()/1e3; print(y.round(1).to_string())
nb=["NL","BE"]; g=x.query("year==2050 and car=='CH4'")
print("out",g[g.o.isin(nb)&~g.d.isin(nb)].v.sum()/1e3,"in",g[~g.o.isin(nb)&g.d.isin(nb)].v.sum()/1e3)
