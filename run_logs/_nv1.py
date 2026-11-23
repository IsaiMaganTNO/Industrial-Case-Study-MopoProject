import pickle,pandas as pd
pd.set_option("display.width",250)
N=pickle.load(open(r"run_logs\nodac_nuc.pkl","rb"));O=pickle.load(open(r"run_logs\vre15.pkl","rb"))
NB=r"^(BE|NL)C\d"; nb=lambda df:df[df.region.astype(str).str.match(NB)]
for n,d in [("vre15",O),("nuc",N)]:
  s=d["co2store"];print(n,"STORE Mt by site\n",(s.groupby(["reservoir","year"]).co2.sum().unstack().fillna(0)/1e3).round(2).to_string())
e=N["emis"]; e=nb(e)
cat=e.groupby(["category","year"]).co2.sum().unstack().fillna(0)/1e3
print("\nEMIS by category Mt\n",cat[(cat.abs()>.05).any(axis=1)].round(2).to_string())
neg=e[e.co2<0].groupby(["tech","year"]).co2.sum().unstack().fillna(0)/1e3;print("\nNEG emis\n",neg.round(2).to_string())
p=nb(N["prod"]).drop_duplicates()
print("\nPROD sector x fuel/cc share\n",(p.groupby(["sector","year","cc"]).output.sum().unstack().fillna(0)).round(0).to_string())
print("\natm",N["atm"].to_string())
