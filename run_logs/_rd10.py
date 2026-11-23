import sqlite3,collections,re
c=sqlite3.connect(r"file:.spinetoolbox/items/ines_db/ines_db.sqlite?mode=ro",uri=True)
rows=list(c.execute("SELECT ec.name,e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id"))
# CO2 nodes
co2=[e for k,e in rows if k=='node' and (e=="CO2" or e.startswith("CO2_"))]
print("CO2 nodes:",len(co2),sorted(co2)[:30])
# node__to_unit / unit__to_node referencing CO2_DE etc
for reg in ["DE","UK","NLC1"]:
    n=[e for k,e in rows if k in ("node__to_unit","unit__to_node") and ("CO2_%s"%reg) in e]
    print("CO2_%s flows: %d"%(reg,len(n)), sorted(n)[:4])
