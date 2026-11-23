import sqlite3, collections, re, pandas as pd
from spinedb_api.parameter_value import from_database

xl=pd.ExcelFile(r"data\Industry\technology_catalogue_ind_nuts0_nuts3.xlsx")
cap=xl.parse("ind_process_routes_co2_capture"); emi=xl.parse("ind_process_routes_co2_emission")
src=cap.merge(emi,on=["sector_id","Industry","to_node"],suffixes=("_cap","_emi"))
SRC={}
for _,r in src.iterrows():
    SRC[str(r["Industry"])]={"cap":float(r["2050_cap"]),"emi":float(r["2050_emi"]),"to":str(r["to_node"])}

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
        except Exception:
            vs=[float(x) for x in v.values]; return vs[-1]
    except Exception: return None

# entity name: <unit>__<outnode>__<innode>__<unit>
model=collections.defaultdict(dict)
for en,val,typ in rows:
    parts=en.split("__")
    if len(parts)!=4: continue
    unit,outn,inn,_=parts
    fam=re.sub(r"_(NL|BE)C\d+$","",unit)
    v=num(val,typ)
    key=(re.sub(r"_(NL|BE)C\d+$","",outn), re.sub(r"_(NL|BE)C\d+$","",inn))
    model[fam][key]=v

out=[]
out.append("Compare MODEL flow_ratio coefficients vs SOURCE catalogue (2050).")
out.append("Model CO2 coefficient is keyed (CO2 <- product); source 'cap' is tco2 per t product.")
out.append("Model atmosphere coefficient is the GATEWAY charge on raw fuel (crude/coal/...),")
out.append("which is a DIFFERENT quantity from the route-level 'emi'.")
out.append("")
hdr="{:<24}{:>10}{:>10}{:>12}{:>10}{:>10}{:>10}".format("route","src_cap","mdl_cap","cap_match","src_emi","mdl_atm","atm_on")
out.append(hdr); out.append("-"*len(hdr))
mismatch=[]; missing=[]
for fam,kv in sorted(model.items()):
    if fam not in SRC: continue
    s=SRC[fam]
    mcap=None; matm=None; atmon=""
    for (o,i),v in kv.items():
        if o.startswith("CO2"): mcap=v
        if o=="atmosphere": matm=v; atmon=i
    ok = (mcap is not None and abs(mcap-s["cap"])<=1e-6*max(1,abs(s["cap"])))
    flag = "OK" if ok else ("MISSING" if mcap is None else "DIFF")
    if s["cap"]>1e-9 and flag!="OK": mismatch.append((fam,s["cap"],mcap))
    if s["cap"]>1e-9 and mcap is None: missing.append(fam)
    out.append("{:<24}{:>10.4f}{:>10}{:>12}{:>10.4f}{:>10}{:>10}".format(
        fam[:23], s["cap"], "None" if mcap is None else "{:.4f}".format(mcap), flag,
        s["emi"], "None" if matm is None else "{:.4f}".format(matm), atmon[:9]))

out.append("")
out.append("=== SUMMARY ===")
out.append("routes in source with capture>0 : {}".format(sum(1 for v in SRC.values() if v['cap']>1e-9)))
out.append("routes present in model          : {}".format(len([f for f in model if f in SRC])))
out.append("CAPTURE COEFFICIENT MISMATCHES   : {}".format(len(mismatch)))
for f,s,m in mismatch: out.append("    {:<26} src={:.4f} model={}".format(f,s,m))
open("logs/capture_audit.txt","w",encoding="utf-8").write("\n".join(out))
