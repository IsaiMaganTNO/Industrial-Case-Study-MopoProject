import sqlite3,re,os
def regions(p,label):
    if not os.path.exists(p): print("%-18s MISSING"%label); return
    c=sqlite3.connect("file:%s?mode=ro"%p.replace("\\","/"),uri=True)
    rs=[r[0] for r in c.execute("SELECT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id WHERE ec.name='region'")]
    ic1=sorted(r for r in rs if re.match(r"^(BEC|NLC)\d",r))
    other=sorted(r for r in rs if r not in ic1)
    print("%-18s total=%-4d IC1=%-3d other(%d)=%s"%(label,len(rs),len(ic1),len(other),other[:12]))
    c.close()
for it in ["biomass_db","power_db","vre_db","rdemand_db","gas_db","hydro_db","transmission_db","heat_db","industry_db","transport_db","commodity_db","cargo_db","other_industry_db"]:
    regions(r".spinetoolbox\items\%s\%s.sqlite"%(it,it),it)
