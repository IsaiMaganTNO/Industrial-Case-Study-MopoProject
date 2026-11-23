import sqlite3
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.nb_ccslow_ccu.sqlite")
q="""select e.name,pd.name,substr(pv.value,1,200) from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id where e.name='atmosphere' or e.name like 'atmosphere\\_\\_%' escape '\\'"""
for r in c.execute(q): print(r)
print(c.execute("select count(*),min(cast(pv.value as text)),max(cast(pv.value as text)) from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id where pd.name='node_slack_penalty'").fetchone())
