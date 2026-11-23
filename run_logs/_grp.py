import sqlite3,json
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
for (g,) in c.execute("select e.name from entity e join entity_class ec on ec.id=e.class_id where ec.name=\"investment_group\""):
    if "wind-off" in g or "nuclear" in g:
        for pn,v,a in c.execute("select pd.name,pv.value,al.name from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id join entity e on e.id=pv.entity_id join alternative al on al.id=pv.alternative_id where e.name=?",(g,)):
            print(f"{g:40s} {pn:38s} [{a:16s}] {bytes(v).decode()[:70]}")
