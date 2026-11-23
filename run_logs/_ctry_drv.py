import pickle,pandas as pd
A=pickle.load(open(r"run_logs\nb_v2_NLBE.pkl","rb")); B=pickle.load(open(r"run_logs\nb_ctry_NLBE.pkl","rb"))
def g(d,car):
  s=d["supply"]; s=s[(s.carrier==car)&(s.year==2050)]
  return s.groupby(s.tech.str.replace(r"_(BE|NL)C\d+$|_NS\w+$","",regex=True)).energy.sum()/1e3
for car in ["hydrogen","electricity"]:
  df=pd.DataFrame({"Std":g(A,car),"Ctry":g(B,car)}).fillna(0); df["d"]=df.Ctry-df.Std
  print(car); print(df[df.d.abs()>1].sort_values("d").round(1).to_string())
