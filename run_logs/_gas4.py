import sqlite3,json
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
def params(ename):
    return [(pd,bytes(v).decode(),a) for pd,v,a in c.execute(
      "select pd.name,pv.value,al.name from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id "
      "join entity e on e.id=pv.entity_id join alternative al on al.id=pv.alternative_id where e.name=?",(ename,))]
for u in ["LNG-terminal_BEC1","LNG-terminal_NLC3","gas-extraction_NLC3","CCGT+CC_NLC3"]:
    print("===",u)
    for p,v,a in params(u):
        print(f"   {p:42s} [{a:18s}] {v[:95]}")
    print()
