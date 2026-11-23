import sqlite3
m=sqlite3.connect("file:%s?mode=ro"%r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.co2div365.sqlite",uri=True)
for u in ["Scraps_EAF_BEC3","Diaphragm_BEC1","aluminium-primary-production-reference_NLC1"]:
    ins=m.execute("""SELECT DISTINCT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id
      WHERE ec.name='node__to_unit' AND e.name LIKE ?""",("%__"+u,)).fetchall()
    rat=m.execute("""SELECT e.name,cast(pv.value as text) FROM parameter_value pv
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      JOIN entity e ON e.id=pv.entity_id
      WHERE pd.name='flow_ratio_equality_coefficient' AND e.name LIKE ? AND e.name LIKE '%atmosphere%'""",(u+"%",)).fetchall()
    print("==",u)
    print("   inputs:",[n.split("__")[0] for (n,) in ins])
    for n,v in rat: print("   ATM:",n[:72],"=",v[:10])
m.close()
