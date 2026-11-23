import sqlite3,re,pandas as pd
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
base=lambda n: re.sub(r"_(NL|BE)C\d+$","",n)
atm=set(n.split("__")[0] for (n,) in c.execute(
 """SELECT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id
 WHERE ec.name='unit_flow__unit_flow' AND e.name LIKE '%__atmosphere__%'"""))
units=[n for (n,) in c.execute("""SELECT e.name FROM entity e JOIN entity_class ec
 ON ec.id=e.class_id WHERE ec.name='unit'""")]
df=pd.read_excel(r"data\Industry\technology_catalogue_ind_nuts0_nuts3.xlsx",
 sheet_name="ind_process_routes_co2_emission")
e=df[df["emission"]=="co2_emission"]
f={r["Industry"]:float(r["2050"]) for _,r in e.iterrows()}
tot=0
print("%-62s %4s %9s"%("family (unbooked, nonzero factor)","n","2050 f"))
for fam in sorted(set(base(u) for u in units if u not in atm)):
    if f.get(fam,0)>0:
        n=len([u for u in units if u not in atm and base(u)==fam])
        tot+=n; print("%-62s %4d %9.4f"%(fam[:62],n,f[fam]))
print("TOTAL unbooked units with nonzero factor:",tot)
