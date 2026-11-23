import sqlite3
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
cls=c.execute("select id from entity_class where name='unit'").fetchone()[0]
print("unit class id:",cls)
pdid=c.execute("select id,entity_class_id from parameter_definition where name='availability_factor' and entity_class_id=?",(cls,)).fetchone()
print("availability_factor pd:",pdid)
for pat in ["LNG-terminal_%","gas-extraction_%"]:
    rows=list(c.execute("select id,name from entity where class_id=? and name like ? order by name",(cls,pat)))
    print(f"{pat}: {len(rows)} units")
    ex=list(c.execute("""select e.name,al.name from parameter_value pv join entity e on e.id=pv.entity_id
      join alternative al on al.id=pv.alternative_id
      where pv.parameter_definition_id=? and e.class_id=? and e.name like ?""",(pdid[0],cls,pat)))
    print("   existing availability_factor rows:",ex if ex else "NONE")
print()
print("alt Base id:",c.execute("select id from alternative where name='Base'").fetchone())
print("max commit_id:",c.execute("select max(commit_id) from entity").fetchone())
