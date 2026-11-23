import pickle
b=pickle.load(open(r"run_logs\routeemis.pkl","rb"))
p=b["prod"]; e=b["emis"]; cn=b["co2net"]
print("=== CEMENT: gross emissions, capture, NET ===")
for y in (2030,2040,2050):
    q=p[(p["year"]==y)&(p["sector"]=="cement")]
    techs=set(q["tech"])
    out=q["output"].sum()
    gross=e[(e["year"]==y)&(e["tech"].isin(techs))]["co2"].sum()
    cap=cn[(cn["year"]==y)&(cn["role"]=="captured")&(cn["tech"].isin(techs))]["co2"].sum()
    print(" %d out=%7.0f gross=%8.1f captured=%8.1f net=%8.1f  net_int=%.4f"%(
        y,out,gross,cap,gross,gross/out))
    for t,v in q.groupby("tech")["output"].sum().sort_values(ascending=False).items():
        if v<1: continue
        g=e[(e["year"]==y)&(e["tech"]==t)]["co2"].sum()
        c=cn[(cn["year"]==y)&(cn["role"]=="captured")&(cn["tech"]==t)]["co2"].sum()
        print("     %-18s out=%6.0f gross=%7.1f cap=%7.1f int=%.4f"%(str(t)[:18],v,g,c,g/v))
