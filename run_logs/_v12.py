import pickle, pandas as pd
pd.set_option("display.width",92)
A=pickle.load(open(r"run_logs\vre15.pkl","rb"))
B=pickle.load(open(r"run_logs\gascap.pkl","rb"))
def el(F):
    s=F["supply"]
    s=s[s.carrier.astype(str).str.contains("electric",case=False,na=False)]
    return s.groupby(["tech","year"]).energy.sum().unstack(fill_value=0)
a=el(A); b=el(B)
idx=sorted(set(a.index)|set(b.index))
a=a.reindex(idx,fill_value=0); b=b.reindex(idx,fill_value=0)
out=pd.DataFrame({"gascap_2050":b.get(2050,0),"vre15_2050":a.get(2050,0)})
out["delta"]=out.vre15_2050-out.gascap_2050
out=out[(out.abs().sum(axis=1)>1)].sort_values("vre15_2050",ascending=False)
print(out.round(0).to_string())
print("\nTOTAL 2050:", round(b.get(2050,0).sum()), "->", round(a.get(2050,0).sum()))
