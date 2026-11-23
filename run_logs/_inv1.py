import pickle,sys,pandas as pd
sys.path.insert(0,"tools"); import plot_run_summary as S
pd.set_option("display.width",250); pd.set_option("display.max_rows",400)
A=pickle.load(open(r"run_logs\nb_v2_NLBE.pkl","rb")); B=pickle.load(open(r"run_logs\nb_ctry_NLBE.pkl","rb"))
def cmp(fa,fb,thr):
  df=pd.concat({"SA":fa,"CL":fb},axis=1).fillna(0); df["d"]=df.CL-df.SA
  return df[(df.SA.abs()>thr)|(df.CL.abs()>thr)].round(1)
print("== supply TWh by carrier/tech (2030,2050)")
for c in ["electricity","hydrogen","methane","heat"]:
  for y in [2030,2040,2050]:
    f=lambda d:d["supply"].query("carrier==@c and year==@y").groupby("tech").energy.sum()/1e3
    x=cmp(f(A),f(B),1); x=x[x.d.abs()>1]
    if len(x): print("--",c,y); print(x.sort_values("d").to_string())
print("== fleet units by category")
f=lambda d:d["fleet"].groupby(["category","year"]).units.sum().unstack()
print(pd.concat({"SA":f(A),"CL":f(B)},axis=1).round(1).to_string())
