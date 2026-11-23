import pandas as pd,glob,os,re
A=r"reports_v2_biocap365\Investment_Results.3day_biocap365_industry_%s.csv"
B=r"reports_v2_retireall\Investment_Results.3day_retireall_industry_%s.csv"
secs=sorted(os.path.basename(f).split("_industry_")[1][:-4] for f in glob.glob(B%"*"))
for s in secs:
    try: b=pd.read_csv(B%s,index_col=0)
    except: continue
    try: a=pd.read_csv(A%s,index_col=0)
    except: a=None
    r2050=b.loc[2050] if 2050 in b.index else None
    if r2050 is None: continue
    nz=r2050[r2050>0.05].sort_values(ascending=False)
    prev=""
    if a is not None and 2050 in a.index:
        pa=a.loc[2050]; pnz=pa[pa>0.05].sort_values(ascending=False)
        prev="  | before: "+", ".join("%s %.0f%%"%(k,v) for k,v in pnz.items())
    print("%-20s %s%s"%(s,", ".join("%s %.0f%%"%(k,v) for k,v in nz.items()),prev))
