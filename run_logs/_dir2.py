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
# 1. does any connection declare >1 from/to (i.e. bidirectional)?
multi=[k for k in co2 if len(fr.get(k,[]))>1 or len(to.get(k,[]))>1]
print("connections with multiple from/to (bidirectional):",len(multi))
# 2. is there a reverse twin edge for each edge?
E=set()
for k in co2:
    for a in fr.get(k,[]):
        for b in to.get(k,[]): E.add((a,b))
rev=[(a,b) for a,b in E if (b,a) in E]
print(f"edges={len(E)}  with reverse twin={len(rev)}")
# 3. params on CO2 connections that could permit reverse flow
print("\nparams on CO2 connections:")
for nm,cnt in c.execute("""
 select pd.name,count(*) from parameter_value pv
 join parameter_definition pd on pd.id=pv.parameter_definition_id
 join entity e on e.id=pv.entity_id
 join entity_class ec on ec.id=e.class_id
 where ec.name in ('connection','connection__from_node','connection__to_node','connection__node__node')
   and e.name like '%CO2%' group by pd.name order by 2 desc"""):
    print(f"   {nm:45s} {cnt}")
# 4. BEC6/BEC7 out-edges
for n in ['CO2_BEC6','CO2_BEC7']:
    print(f"\n{n} OUT ->",sorted(b for a,b in E if a==n))
    print(f"{n} IN  <-",sorted(a for a,b in E if b==n))
