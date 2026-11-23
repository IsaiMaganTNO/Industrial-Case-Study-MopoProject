import sqlite3,re
m=sqlite3.connect("file:%s?mode=ro"%r"checkpoints\Final_SpineOpt_Model.tiny.3day.group1.biocap365.retireall.hcco2.sqlite",uri=True)
# what does a route-based unit look like? cement uses tco2_t and lands as-is.
for u in ["CEM2-(Afm)_BEC6","aluminium-primary-production-reference_NLC1",
          "paper-production-reference_NLC1","leather-and-textile-production-reference_NLC1"]:
    outs=m.execute("""SELECT DISTINCT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id
      WHERE ec.name='unit__to_node' AND e.name LIKE ?""",(u+"__%",)).fetchall()
    print("%-46s outputs=%s"%(u[:46],[n.split("__",1)[1] for (n,) in outs]))
m.close()
