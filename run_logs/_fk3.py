import sqlite3
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
v={r[1] for r in c.execute("pragma foreign_key_check")}
# rowids of entity_element rows belonging to entities I created (id>25000)
mine={r[0] for r in c.execute("select rowid from entity_element where entity_id>=25000")}
print("my entity_element rows:",len(mine))
print("my rows that violate FK:",len(mine & v))
# verify the FK semantics: fkid=1 is (element_id->entity.id, dimension_id->entity.class_id)
# i.e. it requires element's CLASS == dimension_id. Check mine:
bad=c.execute("""select count(*) from entity_element el join entity e on e.id=el.element_id
  where el.entity_id>=25000 and e.class_id<>el.dimension_id""").fetchone()[0]
print("my rows where element.class_id != dimension_id:",bad)
# same check across whole DB for context
allbad=c.execute("""select count(*) from entity_element el join entity e on e.id=el.element_id
  where e.class_id<>el.dimension_id""").fetchone()[0]
print("whole-DB rows where element.class_id != dimension_id:",allbad)
