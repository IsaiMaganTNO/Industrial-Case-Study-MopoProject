import pickle
b=pickle.load(open(r"run_logs\routeemis.pkl","rb"))
p=b["prod"]; e=b["emis"]; cn=b["co2net"]
print("%-6s %8s %9s %9s %9s %9s"%("year","output","gross","captured","NET","net_int"))
for y in (2030,2040,2050):
    q=p[(p["year"]==y)&(p["sector"]=="cement")]
    techs=set(q["tech"]); out=q["output"].sum()
    gross=e[(e["year"]==y)&(e["tech"].isin(techs))]["co2"].sum()
    cap=cn[(cn["year"]==y)&(cn["role"]=="captured")&(cn["tech"].isin(techs))]["co2"].sum()
    net=gross-cap
    print("%-6d %8.0f %9.1f %9.1f %9.1f %9.4f"%(y,out,gross,cap,net,net/out))
print("\nref 2018 EU-mix intensity = 0.4980 (gross)")
