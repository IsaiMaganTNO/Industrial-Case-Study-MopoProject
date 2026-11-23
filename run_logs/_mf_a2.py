import pickle,pandas as pd
pd.set_option("display.width",250); pd.set_option("display.max_rows",400); pd.set_option("display.max_columns",30)
M=pickle.load(open(r"run_logs\mr_fix.pkl","rb")); B=pickle.load(open(r"run_logs\nb_v2.pkl","rb"))
def cty(df):
    r=df.region.astype(str); return r.str.extract(r"^([A-Z]{2})")[0].where(df.region.notna(),"OFF")
for nm,D in [("MR",M),("NB",B)]:
    S=D["supply"].copy(); S["c"]=cty(S); S=S[S.energy>0]
    x=S[S.carrier=="methane"].groupby(["c","tech","year"]).energy.sum().unstack().fillna(0)/1e3
    print("=====",nm,"methane TWh\n",x[(x>2).any(axis=1)].round(1).to_string())
    x=S[S.carrier=="electricity"].groupby(["c","year"]).energy.sum().unstack().fillna(0)/1e3
    print("elec TWh\n",x.round(0).to_string())
    e=D["emis"].copy(); e["c"]=cty(e); e=e[e.c.isin(["NL","BE"])]
    print("NLBE emis by category\n",(e.groupby(["category","year"]).co2.sum().unstack().fillna(0)/1e3).round(1).to_string())
    o=e.groupby(["tech","year"]).co2.sum().unstack().fillna(0)/1e3; print(o[(o.abs()>2).any(axis=1)].round(1).to_string())
