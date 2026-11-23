import sqlite3
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
# does LNG-terminal / gas-extraction have ANY availability/profile limit?
for u in ["LNG-terminal_NLC3","gas-extraction_NLC3"]:
    rows=c.execute("select pd.name from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id join entity e on e.id=pv.entity_id where e.name like ?",(u+"%",)).fetchall()
    print(u,"->",sorted({r[0] for r in rows}))
# any unit_capacity / availability on the unit__to_node?
for (n,) in c.execute("select e.name from entity e join entity_class ec on ec.id=e.class_id where ec.name=\"unit__to_node\" and e.name like \"LNG-terminal_NLC3%\""):
    ps=[p for (p,) in c.execute("select pd.name from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id join entity e on e.id=pv.entity_id where e.name=?",(n,))]
    print("  rel",n,ps)
print()
# is fossil-CH4 itself bounded in Base? balance_type 1 = ?
print("fossil-CH4 balance_type Base =1 (none/leak?) vs limited alt =2")
