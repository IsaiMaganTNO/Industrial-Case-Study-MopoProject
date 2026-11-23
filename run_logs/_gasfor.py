import sqlite3,json
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
for n in ["CH4_DE","CH4_FR","CH4_UK","CH4_LU"]:
    print("===",n)
    ps=list(c.execute("select pd.name,pv.value,al.name from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id join entity e on e.id=pv.entity_id join alternative al on al.id=pv.alternative_id where e.name=?",(n,)))
    if not ps: print("   (no parameters at all)")
    for p,v,a in ps: print(f"   {p:38s} [{a:12s}] {bytes(v).decode()[:80]}")
    # who feeds it
    src=[x for (x,) in c.execute("select e.name from entity e join entity_class ec on ec.id=e.class_id where ec.name in (\"unit__to_node\",\"node__to_unit\") and e.name like ?",("%"+n+"%",))]
    print("   feeders:",src if src else "NONE")
