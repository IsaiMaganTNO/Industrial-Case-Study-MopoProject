import pandas as pd, os, re, glob
T={"DE","DK","NO","UK"}
def cols_of(p, delim=None):
    with open(p, encoding="utf-8", errors="replace") as f: h=f.readline().rstrip("\n")
    d = delim or (";" if h.count(";")>h.count(",") else ",")
    return h.split(d), d
# Buildings / heat
for f in ["scenario_total_yearly_demands_GWh.csv","simplified_capacities_with_decommissioning_MW.csv","peak_to_yearly_demand_ratios_MW_GWh.csv"]:
    p=os.path.join("data/Buildings",f)
    if os.path.exists(p):
        c,d=cols_of(p)
        print("\n%-50s delim=%r ncols=%d" % (f,d,len(c)))
        print("   cols:", [x.strip()[:14] for x in c[:12]])
        df=pd.read_csv(p,sep=d,nrows=3000)
        hits=set()
        for cc in df.columns[:5]:
            hits |= set(str(v).strip() for v in df[cc].dropna().unique()[:3000]) & T
        print("   target COLS:", [x for x in c if x.strip() in T] or "-", "| target VALUES:", sorted(hits) or "-")
# cop timeseries
p=glob.glob("data/Buildings/cop-timeseries/COP_A2AHP-air_wy2009.csv")[0]
c,d=cols_of(p); print("\nCOP wy2009 ncols",len(c),"targets:",[x for x in c if x.strip() in T], "sample",[x.strip()[:8] for x in c[:10]])
# transport
c,d=cols_of("data/Transport/fleet.csv"); print("\nfleet.csv ncols",len(c),"cols",[x.strip()[:14] for x in c[:10]])
df=pd.read_csv("data/Transport/fleet.csv",sep=d)
for cc in df.columns[:4]:
    v=set(str(x).strip() for x in df[cc].dropna().unique())
    if v & T: print("   col",cc,"has targets:",sorted(v&T))
print("   non-road region files:", sorted({os.path.basename(x).split("_")[0] for x in glob.glob("data/Transport/non-road/*.csv")}))
