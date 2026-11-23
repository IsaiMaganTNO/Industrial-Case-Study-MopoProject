import sqlite3,re
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
def base(n): return re.sub(r'_(NL|BE)C\d+$','',n)
regs={}
for (n,) in c.execute("""SELECT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id
  WHERE ec.name='unit' AND (e.name LIKE 'CEM2-%' OR e.name LIKE 'LC3-%' OR e.name LIKE 'EU-mix%')"""):
    m=re.search(r'_((?:NL|BE)C\d+)$',n)
    if m: regs.setdefault(m.group(1),set()).add(base(n))
for r in sorted(regs):
    print("%-6s %d routes: %s"%(r,len(regs[r]),sorted(regs[r])[:5]))
print("\nCO2 node present in cement regions?")
for r in ("BEC6","BEC7","NLC5","NLC6"):
    n=c.execute("SELECT COUNT(*) FROM entity WHERE name=?",("CO2_"+r,)).fetchone()[0]
    print("   CO2_%s exists: %s"%(r,bool(n)))
