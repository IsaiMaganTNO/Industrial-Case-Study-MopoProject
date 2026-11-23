import pandas as pd,os,hashlib
p=r"data-pipelines\europe\region_transformation_IC1.xlsx"
print("exists",os.path.exists(p),os.path.getsize(p))
x=pd.ExcelFile(p); print("sheets:",x.sheet_names)
for s in x.sheet_names:
    if s.lower().startswith("nuts"):
        d=x.parse(s); print("\n--",s,d.shape,list(d.columns)[:4])
        if "source" in [str(c).lower() for c in d.columns]:
            sc=[c for c in d.columns if str(c).lower()=="source"][0]
            tc=[c for c in d.columns if str(c).lower()=="target"][0]
            tg=sorted(set(d[tc].astype(str)))
            print("   targets n=%d: %s"%(len(tg),tg[:25]))
            print("   sample sources:",sorted(set(d[sc].astype(str)))[:8])
