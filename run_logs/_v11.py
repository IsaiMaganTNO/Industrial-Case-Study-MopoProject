import pickle, pandas as pd
pd.set_option("display.width",92)
A=pickle.load(open(r"run_logs\vre15.pkl","rb"))
B=pickle.load(open(r"run_logs\gascap.pkl","rb"))
def elec(F,tag):
    p=F["prod"]
    e=p[p.output.astype(str).str.contains("elec",case=False,na=False)]
    g=e.groupby("tech")[ [c for c in e.columns if c not in
        ["tech","region","year","sector","output","cc","fuel"]] ].sum()
    return g
for tag,F in [("gascap",B),("vre15",A)]:
    p=F["prod"]; print("==",tag,"prod cols:",list(p.columns))
    break
p=A["prod"]; print(p.head(3).to_string()[:600])
