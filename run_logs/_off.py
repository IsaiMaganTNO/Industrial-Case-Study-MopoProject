import sqlite3
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
def units(pat):
    return [n for (n,) in c.execute("select e.name from entity e join entity_class ec on ec.id=e.class_id where ec.name=\"unit\" and e.name like ? order by e.name",(pat,))]
off=units("wind-off%")
print("offshore wind units:",len(off))
for n in off: print("  ",n)
nuc=units("nuclear%")
print("nuclear units:",len(nuc))
for n in nuc: print("  ",n)
