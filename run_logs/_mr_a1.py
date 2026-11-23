import pickle, pandas as pd
pd.set_option("display.width",250)
M=pickle.load(open(r"run_logs\mixedres.pkl","rb")); V=pickle.load(open(r"run_logs\vre15.pkl","rb"))
def ctry(r): r=str(r); return r[:2] if len(r)>2 and r[2]=="C" else r
def cat(t):
    t=str(t)
    for k,v in [("wind-off","Wind off"),("wind-on","Wind on"),("solar","Solar"),("nuclear","Nuclear"),("battery","Storage"),("-DR","Storage"),
                ("SCPC","Coal"),("coal","Coal"),("lignite","Coal"),("CCGT-H2","H2 turbine"),("OCGT-H2","H2 turbine"),("CCGT","Gas"),("OCGT","Gas"),("gas","Gas"),
                ("RoR","Hydro"),("hydro","Hydro"),("reservoir","Hydro"),("PHS","Hydro"),("waste","Waste/bio"),("bio","Waste/bio"),("oil","Oil")]:
        if k in t: return v
    return "Other:"+t
def mix(F):
    s=F["supply"]; s=s[s.carrier.astype(str).str.contains("electric",case=False,na=False)].copy()
    s["c"]=s.region.map(ctry); s["cat"]=s.tech.map(cat)
    return s
m=mix(M); v=mix(V)
print("carriers in supply:", sorted(M["supply"].carrier.astype(str).unique()))
print("\n=== ELECTRICITY SUPPLY by country (TWh) ===")
print((m.groupby(["c","year"]).energy.sum().unstack()/1e3).round(1).to_string())
print("\n=== 2050 electricity mix by country (TWh) ===")
print((m[m.year==2050].groupby(["cat","c"]).energy.sum().unstack(fill_value=0)/1e3).round(1).to_string())
print("\n=== NL+BE: vre15 vs mixedres (TWh) ===")
for y in [2030,2040,2050]:
    a=v[(v.year==y)&v.c.isin(["BE","NL"])].groupby("cat").energy.sum()/1e3
    b=m[(m.year==y)&m.c.isin(["BE","NL"])].groupby("cat").energy.sum()/1e3
    t=pd.concat([a.rename("vre15"),b.rename("mixed")],axis=1).fillna(0); t["delta"]=t.mixed-t.vre15
    t.loc["TOTAL"]=t.sum()
    print(f"-- {y}\n", t.round(1).to_string())
