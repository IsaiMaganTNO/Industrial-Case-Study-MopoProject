import pickle
B=pickle.load(open(r"runs\3day_nn_fix\logs\nn_fix.pkl","rb"))
s=B["supply"];x=s[(s.category=="other")&(s.carrier=="electricity")].groupby(["tech","year"]).energy.sum().unstack().fillna(0).div(1e3);print(x[(x>1).any(axis=1)].round(1).to_string())
for c in ["hydrogen","methane","heat"]:
  x=s[s.carrier==c].groupby(["category","year"]).energy.sum().unstack().fillna(0).div(1e3);print(c);print(x.round(1).to_string())
print(B["prod"].sector.unique())
