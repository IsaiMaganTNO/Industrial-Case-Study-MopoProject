import pickle,re,sys,pandas as pd
src,dst,cs=sys.argv[1],sys.argv[2],sys.argv[3].split(",")
d=pickle.load(open(src,"rb")); out={}
def ctry(df):
    r=df.region.astype(str).str.extract(r"^([A-Z]{2})")[0]
    off=df.tech.astype(str).str.extract(r"_(?:NS|AS|AT|BS)([A-Z]{2})")[0] if "tech" in df.columns else None
    return r.where(df.region.notna(), off)
for k,v in d.items():
    if hasattr(v,"columns") and "region" in v.columns:
        c=ctry(v); keep=c.isin(cs)
        if "tech" not in v.columns: keep=keep|v.region.isna()
        out[k]=v[keep]
        print(k,len(v),"->",int(keep.sum()), "unassigned NaN:",int((v.region.isna()&c.isna()).sum()))
    else: out[k]=v
pickle.dump(out,open(dst,"wb"))
