import pandas as pd
m=pd.read_excel(r"data-pipelines\europe\region_transformation_IC1.xlsx",sheet_name="NUTS3_IC1")
m["source"]=m["source"].astype(str).str.strip()
orig=m[m["source"].str[:2].isin(["BE","NL"]) & ~m["source"].str.contains("~")]
for p in ["BE22","BE32","NL12","NL32","NL33"]:
    sib=sorted(set(orig.loc[orig["source"].str[:4]==p,"source"]))
    tg=sorted(set(orig.loc[orig["source"].str[:4]==p,"target"]))
    print("%s siblings=%s targets=%s"%(p,sib,tg))
