import sqlite3, json
db=r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.sqlite"
c=sqlite3.connect(db)
q="""select e.name,pd.name,pv.value from parameter_value pv
join parameter_definition pd on pd.id=pv.parameter_definition_id
join entity e on e.id=pv.entity_id
where pd.name in ('user_constraint_slack_penalty','right_hand_side')
and e.name like '%co2%'"""
for n,p,v in c.execute(q):
    s=bytes(v).decode('utf8',errors='replace')
    print(n[:38],p[:22],s[:46])
