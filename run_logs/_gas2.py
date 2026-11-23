import sqlite3,json
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
def params(ename):
    return [(pd,bytes(v).decode(),a) for pd,v,a in c.execute(
      "select pd.name,pv.value,al.name from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id "
      "join entity e on e.id=pv.entity_id join alternative al on al.id=pv.alternative_id where e.name=?",(ename,))]
print("=== node fossil-CH4 params ===")
for p,v,a in params("fossil-CH4"): print(f"  {p:40s} [{a:12s}] {v[:120]}")
print()
print("=== CH4-geo-formation_NLC3 params ===")
for p,v,a in params("CH4-geo-formation_NLC3"): print(f"  {p:40s} [{a:12s}] {v[:120]}")
print()
print("=== relationships mentioning fossil-CH4 ===")
for ec,en in c.execute("select ec.name,e.name from entity e join entity_class ec on ec.id=e.class_id where e.name like \"%fossil-CH4%\""):
    print(f"  {ec:30s} {en}")
