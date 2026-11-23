import sqlite3,pandas as pd
c=sqlite3.connect(r"file:.spinetoolbox/items/biomass_db/biomass_db.sqlite?mode=ro",uri=True)
q="""SELECT e.name,a.name,pv.value FROM parameter_value pv
 JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
 JOIN entity e ON e.id=pv.entity_id JOIN alternative a ON a.id=pv.alternative_id
 WHERE pd.name='annual_production'"""
tot={}
for en,alt,v in c.execute(q):
    tot.setdefault(alt,{})[en.split("__")[-1]]=float(v)
regs=sorted(tot["medium_bio"])
print("regions in DB:",len(regs)); print(regs)
csv=pd.read_csv(r"data\Biomass\db_biomass_ener_mopo_mixedres.csv",low_memory=False)
GW=277777.77
print("\n%-6s %-10s %10s %10s %8s"%("ctry","alt","CSV_PJ","DB_PJ","diff%"))
for alt,sc in [("medium_bio","medium"),("high_bio","high"),("low_bio","low")]:
    for ctry,pref in [("BE","BEC"),("NL","NLC"),("DE","DE"),("DK","DK"),("NO","NO"),("UK","UK")]:
        dbv=sum(v for k,v in tot[alt].items() if (k.startswith(pref) if len(pref)>2 else k==pref))/GW
        cv=csv[(csv.scenario==sc)&(csv.nuts0==ctry)]["quantity"].sum()
        print("%-6s %-10s %10.1f %10.1f %8.2f"%(ctry,alt,cv,dbv,(dbv-cv)/cv*100 if cv else 0))
