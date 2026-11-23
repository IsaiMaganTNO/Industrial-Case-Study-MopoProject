import collections, pandas as pd
xl=pd.ExcelFile(r"data\Industry\technology_catalogue_ind_nuts0_nuts3.xlsx")
sec=xl.parse("ind_process_routes_sec")
cap=xl.parse("ind_process_routes_co2_capture"); emi=xl.parse("ind_process_routes_co2_emission")
SEC=collections.defaultdict(dict)
for _,r in sec.iterrows(): SEC[str(r["Industry"])][str(r["from_node"])]=float(r["2050"])
CAP={str(r["Industry"]):float(r["2050"]) for _,r in cap.iterrows()}
EMI={str(r["Industry"]):float(r["2050"]) for _,r in emi.iterrows()}

# from the prior audit: which routes have an atmosphere row in the model
import sqlite3,re
from spinedb_api.parameter_value import from_database
con=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.1rep.gwfix.sqlite")
con.execute("PRAGMA foreign_keys=OFF")
has_atm=set()
for (en,) in con.execute("""SELECT e.name FROM entity e JOIN entity_class c ON e.class_id=c.id
      WHERE c.name='unit_flow__unit_flow'"""):
    p=en.split("__")
    if len(p)==4 and p[1]=="atmosphere":
        has_atm.add(re.sub(r"_(NL|BE)C\d+$","",p[0]))

GLOBAL={"coal","crude","waste","fossil-CH4","U-92","global-H2"}
CARBON={"coal","crude","waste","CH4","HC","MeOH","bio"}
out=[]
out.append("HYPOTHESIS: a route gets an atmosphere row ONLY if its carbon-bearing fuel")
out.append("is a GLOBAL node (coal/crude/waste). Routes burning REGIONALISED carriers")
out.append("(CH4, HC, MeOH) silently get none -> this is the SAME commodity->node defect.")
out.append("")
hdr="{:<26}{:>8}{:>8}{:<22}{:>9}{:>9}".format("route","src_emi","src_cap","carbon_fuels","global?","atm_row")
out.append(hdr); out.append("-"*len(hdr))
tab=collections.Counter()
for fam in sorted(set(list(CAP)+list(EMI))):
    fuels=[f for f in SEC.get(fam,{}) if f in CARBON]
    if not fuels: continue
    isglob=any(f in GLOBAL for f in fuels)
    atm = fam in has_atm
    se=EMI.get(fam,0.0); sc=CAP.get(fam,0.0)
    tab[(isglob,atm)]+=1
    if sc>1e-9 or se>1e-9:
        out.append("{:<26}{:>8.4f}{:>8.4f}{:<22}{:>9}{:>9}".format(
            fam[:25],se,sc,",".join(fuels)[:21],"YES" if isglob else "no","YES" if atm else "NO"))
out.append("")
out.append("=== CONTINGENCY TABLE (carbon-fuel routes) ===")
out.append("   global-fuel & atm_row  : {}".format(tab[(True,True)]))
out.append("   global-fuel & NO atm   : {}".format(tab[(True,False)]))
out.append("   regional-fuel & atm_row: {}".format(tab[(False,True)]))
out.append("   regional-fuel & NO atm : {}".format(tab[(False,False)]))
open("logs/hypothesis_test.txt","w",encoding="utf-8").write("\n".join(out))
