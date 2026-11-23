import pandas as pd, numpy as np, os, shutil

CSV_IN  = r"data\Biomass\db_biomass_ener_mopo.csv"
CSV_OUT = r"data\Biomass\db_biomass_ener_mopo_mixedres.csv"
XLS     = r"data-pipelines\europe\region_transformation_IC1.xlsx"
BAK     = r"backups\region_transformation_IC1.xlsx.pre-biomassfix"
COUNTRIES = ["DE","DK","NO","UK"]

if not os.path.exists(BAK):
    shutil.copy2(XLS,BAK); print("backup written",os.path.getsize(BAK))

df = pd.read_csv(CSV_IN, low_memory=False)
sheets = pd.read_excel(XLS, sheet_name=None)
n3 = sheets["NUTS3_IC1"].copy()
print("orig NUTS3_IC1 rows:", len(n3))

# existing BE/NL nuts3 -> IC1
n3["source"]=n3["source"].astype(str).str.strip()
n3["target"]=n3["target"].astype(str).str.strip()
be_nl_map = n3[["source","target"]].copy()
# derive parent(NUTS2) -> IC1 children for BE/NL
be_nl_map["n2"]=be_nl_map["source"].str[:4]
be_nl_map["n0"]=be_nl_map["source"].str[:2]

new_rows=[]
# 1) real NUTS3 for the 4 countries -> country itself
for c in COUNTRIES:
    codes=sorted(set(df.loc[df["nuts0"]==c,"nuts3"].astype(str)) - {"-","nan"})
    for code in codes:
        new_rows.append((code,c))
    print("%s real nuts3 rows added: %d"%(c,len(codes)))

# 2) synthetic codes for dash rows
#    nuts2-level dash -> "<nuts2>~2" ; nuts0-only dash -> "<nuts0>~0"
def synth(r):
    if str(r["nuts3"]).strip()!="-":
        return str(r["nuts3"]).strip()
    n2=str(r["nuts2"]).strip()
    if n2!="-":
        return n2+"~2"
    return str(r["nuts0"]).strip()+"~0"
df["nuts3_fix"]=df.apply(synth,axis=1)

dash=df[df["nuts3"].astype(str).str.strip()=="-"]
syn_codes=sorted(set(dash["nuts3_fix"]))
print("synthetic codes:",len(syn_codes))

added_syn=0
for code in syn_codes:
    base=code.split("~")[0]; kind=code.split("~")[1]
    cc=base[:2]
    if cc in COUNTRIES:
        new_rows.append((code,cc)); added_syn+=1
    elif cc in ("BE","NL"):
        if kind=="2":
            tg=sorted(set(be_nl_map.loc[be_nl_map["n2"]==base,"target"]))
        else:
            tg=sorted(set(be_nl_map.loc[be_nl_map["n0"]==base,"target"]))
        if not tg:
            print("  WARN no IC1 children for",code); continue
        for t in tg:
            new_rows.append((code,t)); added_syn+=1
print("synthetic mapping rows added:",added_syn)

add=pd.DataFrame(new_rows,columns=["source","target"])
add["area"]=1; add["population"]=1
out=pd.concat([n3[["source","target","area","population"]],add],ignore_index=True).drop_duplicates(subset=["source","target"])
print("new NUTS3_IC1 rows:",len(out))

df_out=df.drop(columns=["nuts3"]).rename(columns={"nuts3_fix":"nuts3"})
df_out=df_out[list(df.columns[:len(df.columns)-1])]
df_out.to_csv(CSV_OUT,index=False)
print("csv written",os.path.getsize(CSV_OUT),"cols",list(df_out.columns))

sheets["NUTS3_IC1"]=out
with pd.ExcelWriter(XLS,engine="openpyxl") as w:
    for name,d in sheets.items():
        d.to_excel(w,sheet_name=name,index=False)
print("workbook written",os.path.getsize(XLS))
