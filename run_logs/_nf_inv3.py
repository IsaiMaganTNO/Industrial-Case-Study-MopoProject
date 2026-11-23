import pickle,pandas as pd
B=pickle.load(open(r"runs\3day_nn_fix\logs\nn_fix.pkl","rb"))
s=B["supply"];s=s[(s.carrier=="electricity")]
print(s.groupby(["region"],dropna=False).energy.sum().div(1e3).round(1).sort_values().tail(25).to_string())
o=s[s.category=="wind offshore"];print(o.groupby(["region","year"],dropna=False).energy.sum().unstack().div(1e3).round(1).to_string())
print(o.tech.unique()[:10])
