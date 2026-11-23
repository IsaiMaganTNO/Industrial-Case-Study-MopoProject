import pickle, pandas as pd
pd.set_option("display.width",110)
A=pickle.load(open(r"run_logs\routeemis.pkl","rb"))   # baseline
B=pickle.load(open(r"run_logs\co2bidir.pkl","rb"))    # new
oa,ob=A["obj"].sum(),B["obj"].sum()
print(f"P2 objective  baseline={oa:,.0f}  bidir={ob:,.0f}  delta={ob-oa:+,.0f} ({(ob/oa-1)*100:+.3f}%)")
print()
for tag,D in [("BASE ",A),("BIDIR",B)]:
    p=D["prod"]
    cem=p[p["unit"].astype(str).str.contains("CEM2|LC3",regex=True,na=False)]
    cem=cem[cem["period"].astype(str).str.contains("2050")]
    g=cem.groupby(cem["unit"].astype(str).str.extract(r"^([^_]+)")[0])["value"].sum().sort_values(ascending=False)
    print(f"--- {tag} 2050 cement by route"); print(g.to_string())
    print()
