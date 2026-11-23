import pandas as pd, os, glob
T={"DE","DK","NO","UK"}
print("=== HEAT: files already wired ===")
for f,desc in [("scenario_total_yearly_demands_GWh.csv","yearly demands"),
               ("simplified_capacities_with_decommissioning_MW.csv","capacities"),
               ("heat_technology_params.csv","tech params")]:
    p=os.path.join("data/Buildings",f)
    with open(p,encoding="utf-8",errors="replace") as fh: h=fh.readline()
    print("\n%s  rawdelim: %s" % (f, "SEMI" if h.count(";")>h.count(",") else "COMMA"))
    for sep in [",",";"]:
        try:
            d=pd.read_csv(p,sep=sep,nrows=200)
            print("   sep=%r -> %d cols" % (sep,len(d.columns)))
        except Exception as e: print("   sep=%r ERR %s"%(sep,e))
print("\n=== HEAT demand-timeseries dir ===")
dt=sorted(glob.glob("data/Buildings/demand-timeseries/*"))
print("n files",len(dt))
for p in dt[:4]:
    with open(p,encoding="utf-8",errors="replace") as fh: h=fh.readline().rstrip()
    sep=";" if h.count(";")>h.count(",") else ","
    cols=h.split(sep)
    print("  %-48s cols=%d targets=%s" % (os.path.basename(p),len(cols),[c for c in cols if c.strip() in T] or "-"))
print("\n=== COP timeseries ===")
cp=sorted(glob.glob("data/Buildings/cop-timeseries/*wy2009*"))
for p in cp[:3]:
    with open(p,encoding="utf-8",errors="replace") as fh: h=fh.readline().rstrip()
    sep=";" if h.count(";")>h.count(",") else ","
    cols=h.split(sep)
    print("  %-44s cols=%d targets=%s" % (os.path.basename(p),len(cols),[c for c in cols if c.strip() in T] or "-"))
