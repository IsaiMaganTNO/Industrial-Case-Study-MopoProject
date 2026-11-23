import pickle,pandas as pd
out={}
for tag,f in [("3day",r"run_logs\hcco2.pkl"),("7day",r"run_logs\hcco2_7day.pkl")]:
    d=pickle.load(open(f,"rb")); s=d["supply"]
    e=s[(s["carrier"]=="electricity")]
    out[tag]=e
def fam(e,y):
    g=e[e["year"]==y].groupby("tech")["energy"].sum()
    agg={"wind-off":0.0,"wind-on":0.0,"solar":0.0,"CCGT+CC":0.0,
         "CCGT unabated":0.0,"OCGT":0.0,"oil-eng":0.0,"battery":0.0,
         "nuclear":0.0,"coal":0.0,"other":0.0}
    for k,v in g.items():
        if k.startswith("wind-off"): agg["wind-off"]+=v
        elif k.startswith("wind-on"): agg["wind-on"]+=v
        elif k.startswith("solar"): agg["solar"]+=v
        elif "CCGT+CC" in k: agg["CCGT+CC"]+=v
        elif k.startswith("CCGT"): agg["CCGT unabated"]+=v
        elif k.startswith("OCGT"): agg["OCGT"]+=v
        elif "oil-eng" in k: agg["oil-eng"]+=v
        elif "battery" in k: agg["battery"]+=v
        elif "nuclear" in k: agg["nuclear"]+=v
        elif "SCPC" in k: agg["coal"]+=v
        else: agg["other"]+=v
    return agg,g.sum()
for y in (2030,2040,2050):
    a,sa=fam(out["3day"],y); b,sb=fam(out["7day"],y)
    print("=== %d   3day %.0f GWh | 7day %.0f GWh ==="%(y,sa,sb))
    print("%-16s %10s %7s %10s %7s"%("family","3day","%","7day","%"))
    for k in a:
        if max(a[k],b[k])<1: continue
        print("%-16s %10.0f %6.2f%% %10.0f %6.2f%%"%(k,a[k],100*a[k]/sa,b[k],100*b[k]/sb))
    print()
