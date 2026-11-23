import pickle,re,pandas as pd
pd.set_option("display.width",250)
D=pickle.load(open(r"run_logs\_bal_sa_cl.pkl","rb"))
I=re.compile(r"^((BE|NL)C\d+)_(\w+)_((BE|NL)C\d+)$")
for k,d in D.items():
  x=d[d.obj.str.contains("salt-cavern")]
  print(k,"cavern flows by year (TWh, to H2 node):",(x[x.dir=="to_node"].groupby("year").v.sum()/1e3).round(1).to_dict())
sa=D["SA"]; m=sa.obj.str.match(I)
x=sa[m & (sa.dir=="to_node")].copy()
x["intra"]=x.obj.map(lambda o:I.match(o).group(2)==I.match(o).group(5))
x=x[x.intra]
print("SA intra-country flows (TWh/Mt) by carrier/year:"); print((x.groupby(["car","year"]).v.sum()/1e3).round(1).unstack())
# PEA by zone 2050
for k,d in D.items():
  y=d[(d.year==2050)&d.obj.str.contains(r"PEA_")&(d.dir=="from_node")]
  print(k,"PEA inputs by route/zone 2050:",(y.groupby("obj").v.sum()/1e3).round(1).to_dict())
