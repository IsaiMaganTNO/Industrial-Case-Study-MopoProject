import pickle
d=pickle.load(open(r"run_logs\co2bidir.pkl","rb"))
f=d["fleet"] if "fleet" in d else None
print(type(d), list(d.keys())[:20])
fl=d["fleet"]
sub=fl[fl["tech"].str.contains("wind-off|nuclear",case=False,na=False)]
print(sub.groupby(["tech","year"])["units"].sum().to_string())
