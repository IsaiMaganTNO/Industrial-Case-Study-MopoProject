import pickle,re,pandas as pd
pd.set_option("display.width",250); pd.set_option("display.max_rows",300)
D=pickle.load(open(r"run_logs\_bal_sa_cl.pkl","rb"))
I=re.compile(r"^((BE|NL)C\d+)_\w+_((BE|NL)C\d+)$")
def grp(o):
  if I.match(o) and I.match(o).group(2)==I.match(o).group(4): return "CONN intra-country"
  if re.match(r"^[A-Z]{2}",o) and "_" in o and o.count("_")==2 and not o.startswith(("PEM","LH2","CCGT")): return "CONN cross-border:"+o.split("_")[0][:2]+">"+o.split("_")[2][:2]
  return re.sub(r"_(BE|NL)C\d+$|_NS\w+$","",o)
for car in ["H2","elec","CH4","CO2"]:
  for y in [2050]:
    rs=[]
    for k,d in D.items():
      x=d[(d.car==car)&(d.year==y)].copy(); x["s"]=x.v.where(x.dir=="to_node",-x.v); x["g"]=x.obj.map(grp)
      rs.append(x.groupby("g").s.sum().rename(k)/1e3)
    df=pd.concat(rs,axis=1).fillna(0); df["d"]=df.CL-df.SA
    df=df[(df.SA.abs()>0.5)|(df.CL.abs()>0.5)]
    print(f"===== {car} {y} net into node (TWh or Mt) ====="); print(df.sort_values("d").round(1).to_string())
