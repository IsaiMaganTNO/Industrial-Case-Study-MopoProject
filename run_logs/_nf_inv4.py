import pickle,pandas as pd
B=pickle.load(open(r"runs\3day_nn_fix\logs\nn_fix.pkl","rb"))
s=B["supply"];e=s[s.carrier=="electricity"]
print("pos",e[e.energy>0].groupby("year").energy.sum().div(1e3).round(1).to_dict(),"neg",e[e.energy<0].groupby("year").energy.sum().div(1e3).round(1).to_dict())
print(s.carrier.unique())
n=e[e.energy<0].groupby(["tech","year"]).energy.sum().unstack().fillna(0).div(1e3);print(n[(n.abs()>3).any(axis=1)].round(1).to_string())
