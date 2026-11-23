import sqlite3
for tag,db in [("BASELINE",r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"),
               ("PATCHED ",r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")]:
    c=sqlite3.connect(db)
    n=c.execute("""select count(*) from entity_element el join entity e on e.id=el.element_id
      where e.class_id<>el.dimension_id""").fetchone()[0]
    tot=c.execute("select count(*) from entity_element").fetchone()[0]
    print(f"{tag}: entity_element rows={tot:7d}  class_id!=dimension_id -> {n}")
# what does dimension_id actually mean here? check a known-good CH4 reverse row
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
print("\nCH4 reverse (known good, pre-existing) BEC2_CH4_BEC1__CH4_BEC2:")
for r in c.execute("""select el.*, e2.class_id as elem_class from entity_element el
  join entity e on e.id=el.entity_id join entity e2 on e2.id=el.element_id
  where e.name='BEC2_CH4_BEC1__CH4_BEC2'"""):
    print("   ",r)
print("\nMY CO2 reverse BEC6_CO2_BEC3__CO2_BEC6:")
for r in c.execute("""select el.*, e2.class_id as elem_class from entity_element el
  join entity e on e.id=el.entity_id join entity e2 on e2.id=el.element_id
  where e.name='BEC6_CO2_BEC3__CO2_BEC6'"""):
    print("   ",r)
print("\nFORWARD CO2 BEC3_CO2_BEC6__CO2_BEC3:")
for r in c.execute("""select el.*, e2.class_id as elem_class from entity_element el
  join entity e on e.id=el.entity_id join entity e2 on e2.id=el.element_id
  where e.name='BEC3_CO2_BEC6__CO2_BEC3'"""):
    print("   ",r)
