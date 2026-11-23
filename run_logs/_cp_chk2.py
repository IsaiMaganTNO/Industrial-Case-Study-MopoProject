import sqlite3
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.nb_cp.sqlite")
names=("connection_monitored","connection_contingency","has_pressure","has_voltage_angle","connection_type","binary_gas_flow_active","connection_min_factor","connection_emergency_capacity","connection_capacity","physics_type","is_reserve_node","fixed_pressure_constant_1","connection_flow_delay","fix_connection_flow","connection_flow_lower_limit")
for n in names:
    r=c.execute("select ec.name,count(*) from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id join entity_class ec on ec.id=pd.entity_class_id where pd.name=? group by ec.name",(n,)).fetchall()
    if r: print(n,r)
print("user_constraint/investment_group refs to intra conns:",c.execute("""select count(*) from entity e join entity_class ec on ec.id=e.class_id join entity_element ee on ee.entity_id=e.id join entity x on x.id=ee.element_id
 where (ec.name like 'connection%user_constraint' or ec.name like 'connection%investment_group') and x.name glob '[BN][EL]C[0-9]_*_[BN][EL]C[0-9]' and substr(x.name,1,2)=substr(x.name,-4,2)""").fetchone())
