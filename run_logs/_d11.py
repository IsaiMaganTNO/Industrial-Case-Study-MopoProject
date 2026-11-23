import pandas as pd, os, re, csv
B=r"verification\Data - IC1 and PECD1"
def rep(tag,cols):
    ic1=[c for c in cols if re.fullmatch(r"(BE|NL)C\d",str(c))]
    p1=[c for c in cols if re.fullmatch(r"[A-Z]{2}",str(c))]
    off=[c for c in cols if re.fullmatch(r"(NS|EM|AS|AT|BL|BS|MS)[A-Z]{2}[A-Z0-9]*",str(c))]
    p2=[c for c in cols if re.fullmatch(r"[A-Z]{2}\d{2}",str(c))]
    print(f"{tag}: ncols={len(cols)} IC1={len(ic1)} PECD1={len(p1)} PECD2={len(p2)} OFF={len(off)} bareBENL={sorted(set(p1)&{'BE','NL'})}")
    return ic1,p1,p2,off
for f,sep in [("Transport/fleets_per_scenario.csv",","),
              ("Biomass/db_biomass_ener_mopo.csv",None),
              ("Buildings/heat_technology_params.csv",None)]:
    p=os.path.join(B,*f.split("/"))
    with open(p,encoding="utf8",errors="replace") as fh: head=fh.readline()
    s=";" if head.count(";")>head.count(",") else ","
    d=pd.read_csv(p,sep=s,nrows=3)
    rep(f+f" [sep='{s}']",d.columns)
    print("   first cols:",list(d.columns)[:8])
print()
for f in ["wind-on-SP277-HH100.csv","wind-off-FB-SP370-HH155.csv","solar-PV-no-tracking.csv"]:
    p=os.path.join(B,"VRE","VRE_time_series",f)
    with open(p,encoding="utf8",errors="replace") as fh: head=fh.readline()
    s=";" if head.count(";")>head.count(",") else ","
    d=pd.read_csv(p,sep=s,nrows=2)
    ic1,p1,p2,off=rep("VRE/"+f,d.columns)
    print("   sample PECD2:",sorted(p2)[:8],"OFF:",sorted(off)[:6])
