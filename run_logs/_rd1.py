import sqlite3,collections,re
def regions(p,label):
    c=sqlite3.connect("file:%s?mode=ro"%p.replace("\\","/"),uri=True)
    try:
        rs=[r[0] for r in c.execute("SELECT e.name FROM entity e JOIN entity_class ec ON ec.id=e.entity_class_id WHERE ec.name='region'")]
    except Exception as ex:
        print(label,"ERR",ex); c.close(); return
    ic1=[r for r in rs if re.match(r"^(BEC|NLC)\d",r)]
    other=[r for r in rs if r not in ic1]
    print("%-14s total=%-5d IC1=%-3d other=%s"%(label,len(rs),len(ic1),sorted(other)[:14]))
    c.close()
for it in ["biomass_db","power_db","vre_db","rdemand_db","gas_db","hydro_db","transmission_db","heat_db","industry_db","transport_db","commodity_db","cargo_db","other_industry_db"]:
    regions(r".spinetoolbox\items\%s\%s.sqlite"%(it,it),it)
