import pickle, pandas as pd
pd.set_option("display.width",92)
A=pickle.load(open(r"run_logs\vre15.pkl","rb"))
B=pickle.load(open(r"run_logs\gascap.pkl","rb"))
def el(F):
    s=F["supply"]; s=s[s.carrier.astype(str).str.contains("electric",case=False,na=False)]
    return s.groupby(["tech","year"]).energy.sum().unstack(fill_value=0)
a,b=el(A),el(B)
idx=sorted(set(a.index)|set(b.index)); a=a.reindex(idx,fill_value=0); b=b.reindex(idx,fill_value=0)
for y in [2030,2040,2050]:
    t=pd.DataFrame({"gascap":b.get(y,0),"vre15":a.get(y,0)})
    t["d"]=t.vre15-t.gascap
    t=t[t.abs().sum(axis=1)>500].sort_values("vre15",ascending=False)
    print(f"\n===== {y} (GWh) =====")
    print(t.round(0).to_string())
    print("TOTAL", round(b.get(y,0).sum()), "->", round(a.get(y,0).sum()))
