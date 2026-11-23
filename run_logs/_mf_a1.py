import pickle,pandas as pd
pd.set_option("display.width",250); pd.set_option("display.max_rows",300); pd.set_option("display.max_columns",30)
M=pickle.load(open(r"run_logs\mr_fix.pkl","rb")); B=pickle.load(open(r"run_logs\nb_v2.pkl","rb"))
def cty(df):
    r=df.region.astype(str); return r.str.extract(r"^([A-Z]{2})")[0].where(df.region.notna(),"OFF")
for nm,D in [("MR",M),("NB",B)]:
    e=D["emis"].copy(); e["c"]=cty(e)
    print("=====",nm,"emis by country Mt\n",(e.groupby(["c","year"]).co2.sum().unstack().fillna(0)/1e3).round(2).to_string())
    print("emis total",(e.groupby("year").co2.sum()/1e3).round(2).to_dict())
    print("atm\n",D["atm"].head(20).to_string() if hasattr(D["atm"],"to_string") else D["atm"])
    c=D["co2net"]; print("co2 roles\n",(c.groupby(["role","year"]).co2.sum().unstack()/1e3).round(2).to_string())
    s=D["co2store"]; print("storage\n",(s.groupby(["reservoir","year"]).co2.sum().unstack()/1e3).round(2).to_string())
