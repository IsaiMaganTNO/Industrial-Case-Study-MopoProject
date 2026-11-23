import pickle,sys,pandas as pd
sys.path.insert(0,"tools"); import plot_run_summary as S
pd.set_option("display.width",250); pd.set_option("display.max_rows",500)
A=pickle.load(open(r"run_logs\nb_v2_NLBE.pkl","rb")); B=pickle.load(open(r"run_logs\nb_ctry_NLBE.pkl","rb"))
for y in [2030,2040,2050]:
  f=lambda d:d["prod"].query("year==@y").assign(r=lambda z:z.tech.map(S.route_label)).groupby(["sector","r"]).output.sum()/1e3
  df=pd.concat({"SA":f(A),"CL":f(B)},axis=1).fillna(0); df["d"]=df.CL-df.SA
  print("== industry",y,"max|d|",df.d.abs().max().round(3)); print(df[df.d.abs()>0.01].round(2).to_string())
print("== CC share by sector 2050")
for n,d in (("SA",A),("CL",B)):
  p=d["prod"].query("year==2050"); print(n,(p[p.cc].groupby("sector").output.sum()/p.groupby("sector").output.sum()).round(3).to_dict())
print("== industry fuel 2050")
f=lambda d:d["prod"].query("year==2050").groupby("fuel").output.sum()/1e3
print(pd.concat({"SA":f(A),"CL":f(B)},axis=1).round(2))
print("== hydrogen production units fleet 2050")
for n,d in (("SA",A),("CL",B)):
  x=d["fleet"].query("year==2050 and category in ['hydrogen production','electrolysis']"); print(n,x.groupby(["tech","region"]).units.sum().round(2).to_dict())
