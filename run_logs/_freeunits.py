import sqlite3,sys,collections
c=sqlite3.connect(sys.argv[1])
cls={n:i for i,n in c.execute("select id,name from entity_class")}
pd={n:i for i,n in c.execute("select id,name from parameter_definition where entity_class_id=?",(cls["unit"],))}
def ents(p): return set(r[0] for r in c.execute("select entity_id from parameter_value where parameter_definition_id=?",(pd[p],)))
units=dict(c.execute("select id,name from entity where class_id=?",(cls["unit"],)))
has_ex=ents("existing_units"); has_inv=ents("investment_count_max_cumulative")|ents("unit_investment_cost")
free=[units[u] for u in units if u not in has_ex]
fam=collections.Counter(n.rsplit("_",1)[0] for n in free)
print("units total",len(units),"without existing_units:",len(free))
for k,v in sorted(fam.items()): print(f"  {k:50s} {v}")
