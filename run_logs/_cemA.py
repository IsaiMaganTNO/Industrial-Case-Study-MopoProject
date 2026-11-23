import sqlite3
db=r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.co2div365.sqlite"
c=sqlite3.connect("file:%s?mode=ro"%db,uri=True)
for fam in ["CEM2-(Afm)","CEM2-(Afm)MEA","LC3-(Afm)MEA","EU-mix-2018"]:
    print("==",fam)
    ins=c.execute("""SELECT DISTINCT e.name FROM entity e
      JOIN entity_class ec ON ec.id=e.class_id
      WHERE ec.name='node__to_unit' AND e.name GLOB ?""",("*__"+fam+"_BEC6",)).fetchall()
    print("   inputs:",[n.split("__")[0] for (n,) in ins])
    outs=c.execute("""SELECT DISTINCT e.name FROM entity e
      JOIN entity_class ec ON ec.id=e.class_id
      WHERE ec.name='unit__to_node' AND e.name GLOB ?""",(fam+"_BEC6__*",)).fetchall()
    print("   outputs:",[n.split("__",1)[1] for (n,) in outs])
    rat=c.execute("""SELECT e.name,cast(pv.value as text) FROM parameter_value pv
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      JOIN entity e ON e.id=pv.entity_id
      WHERE pd.name='flow_ratio_equality_coefficient' AND e.name GLOB ?""",
      (fam+"_BEC6__*",)).fetchall()
    for n,v in rat: print("      RATIO",n[:66],"=",v[:14])
c.close()
