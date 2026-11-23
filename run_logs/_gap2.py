import sqlite3,re
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
fams=["aluminium-primary-production-alternative","alumina-production-alternative",
"other-chemicals-production-alternative","pharmaceuticals-production-alternative",
"other-non-ferrous-metals-production-alternative",
"ceramics-and-other-non-metalic-minerals-production-alternative",
"machinery-equipment-production-alternative","transport-equipment-production-alternative"]
q="""SELECT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id
WHERE ec.name='unit__to_node'"""
all_=[x[0] for x in c.execute(q)]
for f in fams:
    us=[n for n in all_ if n.startswith(f+"_")]
    atm=[n for n in us if n.endswith("__atmosphere")]
    print("%-58s links=%3d atmosphere=%d"%(f[:58],len(us),len(atm)))
