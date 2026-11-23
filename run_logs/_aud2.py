import sqlite3,re
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
def base(n): return re.sub(r'_(NL|BE)C\d+$','',n)
# what do these 3 consume?
for fam in ["paper-production-alternative","(BM)NH3","pulp-production-alternative"]:
    ins=set()
    for (n,) in c.execute("""SELECT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id
      WHERE ec.name='node__to_unit' AND e.name LIKE ?""",("%__"+fam+"_%",)):
        ins.add(base(n.split("__")[0]))
    print("%-30s inputs: %s"%(fam[:30],sorted(ins)))
