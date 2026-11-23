import sqlite3
b=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite")
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
q="""select pv.type,count(*) from parameter_value pv
 join parameter_definition pd on pd.id=pv.parameter_definition_id
 where pd.name in ('connection_flow_cost','fix_ratio_out_in_connection_flow') group by 1"""
print("BASELINE:",b.execute(q).fetchall())
print("PATCHED :",c.execute(q).fetchall())
# specifically the CO2 forward rows in baseline
q2="""select pv.type,count(*) from parameter_value pv
 join parameter_definition pd on pd.id=pv.parameter_definition_id
 join entity e on e.id=pv.entity_id
 join entity_element el on el.entity_id=e.id and el.position=0
 join entity cc on cc.id=el.element_id
 where pd.name in ('connection_flow_cost','fix_ratio_out_in_connection_flow')
   and cc.name like '%!_CO2!_%' escape '!' group by 1"""
print("BASELINE CO2-only:",b.execute(q2).fetchall())
print("PATCHED  CO2-only:",c.execute(q2).fetchall())
