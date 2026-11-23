import sqlite3,re
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
def base(n): return re.sub(r'_(NL|BE)C\d+$','',n)
fams={}
for (n,) in c.execute("""SELECT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id
  WHERE ec.name='unit'"""):
    f=base(n)
    if any(k in f.lower() for k in ("nuclear","smr-","u-92","uranium","fission")):
        fams[f]=fams.get(f,0)+1
print("nuclear-ish unit families:")
for k,v in sorted(fams.items()): print("   %-24s %d units"%(k,v))
print("\nnodes containing U-92/uranium:")
for (n,) in c.execute("""SELECT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id
  WHERE ec.name='node' AND (lower(e.name) LIKE '%u-92%' OR lower(e.name) LIKE '%uran%')"""):
    print("   ",n)
