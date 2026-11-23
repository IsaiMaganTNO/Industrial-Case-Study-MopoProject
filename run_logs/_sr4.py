import sqlite3, re
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.gascap.vre15.sqlite"
c=sqlite3.connect(db)
units=[r[0] for r in c.execute("select e.name from entity e join entity_class k on k.id=e.class_id where k.name=\"unit\"")]
for cc in ["DE","FR","UK","LU","NO","DK"]:
    print(cc,"units:",len([u for u in units if u.endswith("_"+cc)]))
print("total units:",len(units))
print("IC1 units:",len([u for u in units if re.search(r"_(BE|NL)C\d$",u)]))
# demand params on stub nodes
q="""select e.name,pd.name from parameter_value pv
 join entity e on e.id=pv.entity_id
 join parameter_definition pd on pd.id=pv.parameter_definition_id
 where e.name in ('elec_DE','CH4_DE','elec_FR')"""
for n,p in c.execute(q): print(" ",n,p)
