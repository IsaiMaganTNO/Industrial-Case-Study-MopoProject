import pickle,pandas as pd
A=pickle.load(open(r"run_logs\nb_v2_NLBE.pkl","rb")); B=pickle.load(open(r"run_logs\nb_ctry_NLBE.pkl","rb"))
def t(d):
  r={}
  s=d["supply"]
  for c in ["electricity","hydrogen","methane"]:
    for y in [2030,2040,2050]: r[(c,y)]=s[(s.carrier==c)&(s.year==y)].energy.sum()/1e3
  for y in [2030,2040,2050]:
    r[("emis Mt",y)]=d["emis"][d["emis"].year==y].co2.sum()/1e3
    r[("stored Mt",y)]=d["co2store"][d["co2store"].year==y].co2.sum()/1e3
    r[("ind output",y)]=d["prod"][d["prod"].year==y].output.sum()/1e3
  return pd.Series(r)
df=pd.DataFrame({"Standalone":t(A),"Country":t(B)}); df["diff%"]=(df.Country/df.Standalone-1)*100
print(df.round(1).to_string())
print(sorted(A["supply"].carrier.unique()))
