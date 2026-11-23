import collections, pandas as pd
xl=pd.ExcelFile(r"data\Industry\technology_catalogue_ind_nuts0_nuts3.xlsx")
sec=xl.parse("ind_process_routes_sec")
cap=xl.parse("ind_process_routes_co2_capture"); emi=xl.parse("ind_process_routes_co2_emission")

# authoritative CO2 content (ton/MWh) from commodity_data.csv; bio blank = carbon neutral
CO2C={"CH4":0.20,"HC":0.24,"MeOH":0.20,"coal":0.35,"waste":0.30,"crude":0.26,
      "fossil-CH4":0.20,"fossil-HC":0.24,"bio":0.0,"H2":0.0,"elec":0.0,"CO2":0.0}

SEC=collections.defaultdict(dict); UNIT={}
for _,r in sec.iterrows():
    SEC[str(r["Industry"])][str(r["from_node"])]=float(r["2050"]); UNIT[str(r["Industry"])]=str(r["unit"])
CAP={str(r["Industry"]):float(r["2050"]) for _,r in cap.iterrows()}
EMI={str(r["Industry"]):float(r["2050"]) for _,r in emi.iterrows()}

out=[]
out.append("DECISIVE TEST: is the upstream gateway debit big enough to cover the capture credit?")
out.append("upstream_debit = SUM(fuel_intensity * CO2_content) over carbon-bearing fuels.")
out.append("If capture > debit, the route creates carbon that was never charged -> FREE NEGATIVE.")
out.append("If capture + emission ~= debit, the accounting is CONSISTENT (charge up, credit down).")
out.append("")
hdr="{:<26}{:>9}{:>9}{:>9}{:>10}{:>10}  {}".format("route","debit","capture","emission","cap+emi","balance","verdict")
out.append(hdr); out.append("-"*len(hdr))
bad=[]; good=[]; unkn=[]
for fam in sorted(CAP):
    sc=CAP.get(fam,0.0); se=EMI.get(fam,0.0)
    if sc<=1e-9: continue
    fuels=SEC.get(fam,{})
    if not fuels: unkn.append(fam); continue
    debit=sum(v*CO2C.get(f,0.0) for f,v in fuels.items())
    bal=debit-(sc+se)
    if sc>debit+1e-6:
        verdict="FREE NEGATIVE"; bad.append((fam,debit,sc,se,bal))
    elif abs(bal)<=0.05*max(debit,1e-9)+0.02:
        verdict="consistent"; good.append(fam)
    else:
        verdict="imbalance"; bad.append((fam,debit,sc,se,bal))
    out.append("{:<26}{:>9.4f}{:>9.4f}{:>9.4f}{:>10.4f}{:>10.4f}  {}".format(
        fam[:25],debit,sc,se,sc+se,bal,verdict))

out.append("")
out.append("=== SUMMARY ===")
out.append("consistent routes : {}".format(len(good)))
out.append("problem routes    : {}".format(len(bad)))
out.append("no fuel data      : {} {}".format(len(unkn),unkn))
out.append("")
out.append("=== PROBLEM ROUTES (capture exceeds what was ever charged) ===")
for f,d,c,e,b in sorted(bad,key=lambda x:x[2]-x[1],reverse=True):
    out.append("   {:<26} debit={:<9.4f} capture={:<9.4f} excess={:+.4f}  fuels={}".format(
        f,d,c,c-d,dict((k,round(v,3)) for k,v in SEC.get(f,{}).items())))
open("logs/balance_test.txt","w",encoding="utf-8").write("\n".join(out))
