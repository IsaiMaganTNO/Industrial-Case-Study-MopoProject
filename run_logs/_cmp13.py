import pickle
a=pickle.load(open(r"run_logs\hcco2.pkl","rb"))
b=pickle.load(open(r"run_logs\routeemis.pkl","rb"))
print("%-26s %9s %9s %9s"%("sector 2050","base int","new int","ratio"))
pa,ea=a["prod"],a["emis"]; pb,eb=b["prod"],b["emis"]
secs=sorted(set(pb[pb["year"]==2050]["sector"].dropna()))
for s in secs:
    qa=pa[(pa["year"]==2050)&(pa["sector"]==s)]
    qb=pb[(pb["year"]==2050)&(pb["sector"]==s)]
    oa,ob=qa["output"].sum(),qb["output"].sum()
    if ob<1: continue
    ta=set(qa["tech"]); tb=set(qb["tech"])
    ca=ea[(ea["year"]==2050)&(ea["tech"].isin(ta))]["co2"].sum()
    cb=eb[(eb["year"]==2050)&(eb["tech"].isin(tb))]["co2"].sum()
    ia=ca/oa if oa else 0; ib=cb/ob if ob else 0
    r=(ib/ia) if ia>1e-9 else float("inf")
    print("%-26s %9.4f %9.4f %9s"%(s[:26],ia,ib,("%.1fx"%r) if r!=float("inf") else "0->+"))
