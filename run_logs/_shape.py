import sqlite3
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
def shape(nm):
    """Return the structural signature of a connection: classes, element names/positions, params."""
    cid=c.execute("select id from entity where name=?",(nm,)).fetchone()
    if not cid: return None
    cid=cid[0]; out=[]
    for eid,cls in c.execute("""select e.id,ec.name from entity e join entity_class ec on ec.id=e.class_id
        join entity_element el on el.entity_id=e.id and el.position=0 where el.element_id=? order by ec.name""",(cid,)):
        els=[(p,n) for p,n in c.execute("""select el.position,e2.name from entity_element el
             join entity e2 on e2.id=el.element_id where el.entity_id=? order by el.position""",(eid,))]
        ps=sorted((pd,bytes(v).decode()) for pd,v in c.execute("""select pd.name,pv.value from parameter_value pv
             join parameter_definition pd on pd.id=pv.parameter_definition_id where pv.entity_id=?""",(eid,)))
        out.append((cls,els,ps))
    return sorted(out)
import pprint
for nm in ["BEC3_CO2_BEC6","BEC6_CO2_BEC3"]:
    print("="*70); print(nm)
    for cls,els,ps in shape(nm):
        print(f"  {cls}")
        print(f"    elements: {els}")
        print(f"    params  : {ps}")
