import sqlite3, collections
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
def pairs(cls):
    out=collections.defaultdict(list)
    for conn,node in c.execute("""
      select e2.name, e3.name from entity e
      join entity_class ec on ec.id=e.class_id
      join entity_element el on el.entity_id=e.id
      join entity e2 on e2.id=el.element_id
      join entity_element el2 on el2.entity_id=e.id
      join entity e3 on e3.id=el2.element_id
      where ec.name=? and el.position=0 and el2.position=1
    """,(cls,)):
        out[conn].append(node)
    return out
fr=pairs('connection__from_node'); to=pairs('connection__to_node')
co2=[r[0] for r in c.execute("""select e.name from entity e join entity_class ec on ec.id=e.class_id
 where ec.name='connection' and e.name like '%CO2%'""")]
edges=[]
for k in co2:
    edges.append((fr.get(k),to.get(k)))
for k in co2[:6]:
    print(k,"FROM",fr.get(k),"TO",to.get(k))
