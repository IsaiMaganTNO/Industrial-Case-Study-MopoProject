import sqlite3
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.group1.biocap365.retireall.sqlite"
c=sqlite3.connect(db)
for u in ["CCGT+CC_NLC1","oil-eng_NLC1","CCGT_NLC1"]:
    q="""SELECT e.name, pd.name, CAST(pv.value AS TEXT) FROM parameter_value pv
     JOIN entity e ON e.id=pv.entity_id
     JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
     WHERE e.name LIKE ?||'%' AND pd.name IN
      ('vom_cost','unit_investment_cost','fom_cost','flow_ratio_equality_coefficient')"""
    for n,p,v in c.execute(q,(u,)):
        print(n[:48],"|",p[:32],"|",str(v)[:52])
    print()
