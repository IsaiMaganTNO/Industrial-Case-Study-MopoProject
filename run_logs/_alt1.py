import sqlite3,re,collections
m=sqlite3.connect("file:%s?mode=ro"%r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.co2div365.sqlite",uri=True)
# which units can produce chlorine / steel-secondary nodes?
for node in ["chemical-chlorine","steel-secondary"]:
    rs=m.execute("""SELECT DISTINCT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id
      WHERE ec.name='unit__to_node' AND e.name LIKE ?""",("%__"+node+"%",)).fetchall()
    fams=collections.Counter(re.sub(r'_(NL|BE)C\d+','',n.split("__")[0]) for (n,) in rs)
    print("== %s producers: %s"%(node,dict(fams)))
m.close()
