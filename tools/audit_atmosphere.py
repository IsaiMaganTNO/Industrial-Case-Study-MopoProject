import sqlite3, collections, re, pandas as pd
from spinedb_api.parameter_value import from_database

xl=pd.ExcelFile(r"data\Industry\technology_catalogue_ind_nuts0_nuts3.xlsx")
sec=xl.parse("ind_process_routes_sec")
cap=xl.parse("ind_process_routes_co2_capture")
emi=xl.parse("ind_process_routes_co2_emission")

# source: per route -> fuel intensities, capture, emission (+units)
SEC=collections.defaultdict(dict); SECU={}
for _,r in sec.iterrows():
    SEC[str(r["Industry"])][str(r["from_node"])]=float(r["2050"])
    SECU.setdefault(str(r["Industry"]),set()).add(str(r["unit"]))
CAP={}; EMI={}; UNITS={}
for _,r in cap.iterrows(): CAP[str(r["Industry"])]=float(r["2050"]); UNITS[str(r["Industry"])]=str(r["unit"])
for _,r in emi.iterrows(): EMI[str(r["Industry"])]=float(r["2050"]); UNITS.setdefault(str(r["Industry"]),str(r["unit"]))

# commodity CO2 content (authoritative gateway values)
com=pd.read_csv(r"data\Commodities\commodity_data.csv")
out=["commodity_data.csv cols: {}".format(com.columns.tolist()), com.to_string()[:1800], ""]

DB=r"checkpoints\Final_SpineOpt_Model.tiny.1rep.gwfix.sqlite"
con=sqlite3.connect(DB); con.execute("PRAGMA foreign_keys = OFF")
rows=con.execute("""SELECT e.name, pv.value, pv.type FROM parameter_value pv
  JOIN parameter_definition pd ON pv.parameter_definition_id=pd.id
  JOIN entity e ON pv.entity_id=e.id
  WHERE pd.name='flow_ratio_equality_coefficient'""").fetchall()
def num(val,typ):
    try:
        v=from_database(val,typ)
        try: return float(v)
        except Exception: return float([x for x in v.values][-1])
    except Exception: return None
MODEL=collections.defaultdict(dict)
for en,val,typ in rows:
    p=en.split("__")
    if len(p)!=4: continue
    u,o,i,_=p
    fam=re.sub(r"_(NL|BE)C\d+$","",u)
    MODEL[fam][(re.sub(r"_(NL|BE)C\d+$","",o),re.sub(r"_(NL|BE)C\d+$","",i))]=num(val,typ)

out.append("="*110)
out.append("ATMOSPHERE (GATEWAY) AUDIT: is the carbon charge consistent across routes of the same sector?")
out.append("For each route: model atmosphere coeff, the fuel it is charged on, that fuel's intensity,")
out.append("implied charge per unit product, vs source route-level emission.")
out.append("="*110)
hdr="{:<24}{:<16}{:>9}{:>9}{:>9}{:>10}{:>10}{:>9}".format("route","charged_on","atm_c","fuel_int","implied","src_emi","src_cap","unit")
out.append(hdr); out.append("-"*len(hdr))
recs=[]
for fam in sorted(set(list(CAP)+list(EMI))):
    if fam not in MODEL: continue
    kv=MODEL[fam]
    atm=[(i,v) for (o,i),v in kv.items() if o=="atmosphere"]
    co2=[v for (o,i),v in kv.items() if o.startswith("CO2")]
    se=EMI.get(fam); sc=CAP.get(fam,0.0); un=UNITS.get(fam,"?")
    if atm:
        fuel,ac=atm[0]
        fi=SEC.get(fam,{}).get(fuel)
        imp = ac*fi if (fi is not None and ac is not None) else None
        out.append("{:<24}{:<16}{:>9}{:>9}{:>9}{:>10}{:>10}{:>9}".format(
            fam[:23],fuel[:15],
            "{:.4f}".format(ac) if ac is not None else "None",
            "{:.4f}".format(fi) if fi is not None else "None",
            "{:.4f}".format(imp) if imp is not None else "None",
            "{:.4f}".format(se) if se is not None else "None",
            "{:.4f}".format(sc), un))
        recs.append((fam,fuel,ac,fi,imp,se,sc,un,bool(co2)))
    else:
        out.append("{:<24}{:<16}{:>9}{:>9}{:>9}{:>10}{:>10}{:>9}".format(
            fam[:23],"-- none --","","","",
            "{:.4f}".format(se) if se is not None else "None","{:.4f}".format(sc),un))
        recs.append((fam,None,None,None,None,se,sc,un,bool(co2)))

out.append("")
out.append("="*110)
out.append("KEY TEST: routes WITH capture that have NO atmosphere row  -> capture is free (unpriced)")
out.append("="*110)
free=[r for r in recs if r[6]>1e-9 and r[1] is None]
for r in free: out.append("   {:<26} capture={:.4f} emission={:<9} unit={}".format(r[0],r[6],r[5],r[7]))
out.append("   COUNT = {} of {} capture routes".format(len(free), sum(1 for r in recs if r[6]>1e-9)))
out.append("")
out.append("="*110)
out.append("KEY TEST 2: CCS vs non-CCS sibling pairs - is the CCS variant charged LESS at the gateway?")
out.append("="*110)
base={}
for r in recs:
    if r[6]<=1e-9: base[r[0]]=r
for r in recs:
    if r[6]<=1e-9: continue
    for b in base:
        if r[0].startswith(b) and r[0]!=b:
            out.append("   {:<26} atm_implied={:<10} vs base {:<22} atm_implied={}".format(
                r[0], "{:.4f}".format(r[4]) if r[4] is not None else "NONE",
                b, "{:.4f}".format(base[b][4]) if base[b][4] is not None else "NONE"))
open("logs/atmosphere_audit.txt","w",encoding="utf-8").write("\n".join(out))
