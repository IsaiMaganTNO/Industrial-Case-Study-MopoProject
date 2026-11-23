import sqlite3
db=r"runs\3day_mr_frlu_ccslow_ccu_cap16_dac0_v3\input\Final_SpineOpt_Model.tiny.3day.mr_frlu_ccslow_ccu_cap16_dac0.v3.sqlite"
c=sqlite3.connect(db)
q=lambda s:c.execute(s).fetchall()
print("outputs:",[r[0] for r in q("select e.name from entity e join entity_class ec on e.class_id=ec.id where ec.name='output'")])
print("stages:",q("select e.name from entity e join entity_class ec on e.class_id=ec.id where ec.name='stage'"))
print("models:",q("select e.name from entity e join entity_class ec on e.class_id=ec.id where ec.name='model'"))
print("model params:",q("select pd.name, length(pv.value) from parameter_value pv join parameter_definition pd on pv.parameter_definition_id=pd.id join entity_class ec on pd.entity_class_id=ec.id where ec.name='model'"))
