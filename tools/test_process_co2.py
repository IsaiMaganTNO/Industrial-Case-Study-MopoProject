import pandas as pd, collections
xl=pd.ExcelFile(r"data\Industry\technology_catalogue_ind_nuts0_nuts3.xlsx")
sec=xl.parse("ind_process_routes_sec")
emi=xl.parse("ind_process_routes_co2_emission")
cap=xl.parse("ind_process_routes_co2_capture")
out=[]
out.append("TEST: for CEMENT, does source emission reflect PROCESS CO2 (limestone calcination)")
out.append("on top of fuel combustion? If so, 'capture > fuel debit' is PHYSICALLY CORRECT,")
out.append("not a free negative -- cement CO2 comes mostly from CaCO3 -> CaO + CO2.")
out.append("")
CO2C={"CH4":0.20,"HC":0.24,"MeOH":0.20,"coal":0.35,"waste":0.30,"crude":0.26,"bio":0.0,"H2":0.0,"elec":0.0,"CO2":0.0}
SEC=collections.defaultdict(dict)
for _,r in sec.iterrows(): SEC[str(r["Industry"])][str(r["from_node"])]=float(r["2050"])
EMI={str(r["Industry"]):float(r["2050"]) for _,r in emi.iterrows()}
CAP={str(r["Industry"]):float(r["2050"]) for _,r in cap.iterrows()}
hdr="{:<26}{:>9}{:>9}{:>9}{:>12}".format("cement route","fuel_deb","emission","capture","total_C_out")
out.append(hdr); out.append("-"*len(hdr))
for fam in sorted(SEC):
    if not (fam.startswith("CEM2") or fam.startswith("LC3") or fam=="EU-mix-2018"): continue
    d=sum(v*CO2C.get(f,0.0) for f,v in SEC[fam].items())
    e=EMI.get(fam,0.0); c=CAP.get(fam,0.0)
    out.append("{:<26}{:>9.4f}{:>9.4f}{:>9.4f}{:>12.4f}".format(fam[:25],d,e,c,e+c))
out.append("")
out.append("If 'total_C_out' is ~constant across a family regardless of fuel, the extra")
out.append("carbon is PROCESS emission (clinker), which is real and must be captured.")
out.append("")
out.append("=== unabated baselines for reference ===")
for fam in ["EU-mix-2018","CEM2-(Coal)","CEM2-(Afm)","CEM2-(BMW)"]:
    d=sum(v*CO2C.get(f,0.0) for f,v in SEC.get(fam,{}).items())
    out.append("   {:<16} fuel_debit={:.4f} emission={:.4f} -> process_CO2 approx {:.4f}".format(
        fam,d,EMI.get(fam,0.0),EMI.get(fam,0.0)-d))
open("logs/process_co2_test.txt","w",encoding="utf-8").write("\n".join(out))
