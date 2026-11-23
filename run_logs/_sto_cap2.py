import sqlite3,glob
for n,db in [("MR",glob.glob(r"final_runs_pessimistic_ccs\3_*\input\*.sqlite")[0]),("S3",glob.glob(r"final_runs_pessimistic_ccs\6_*\input\*.sqlite")[0]),("S4",r"runs\3day_mr_frlu_ccslow_ccu_cap16_dac0_v3\input\Final_SpineOpt_Model.tiny.3day.mr_frlu_ccslow_ccu_cap16_dac0.v3.sqlite")]:
  c=sqlite3.connect(db)
  q="""select ec.name,e.name,pd.name,cast(pv.value as text) from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id join entity e on e.id=pv.entity_id join entity_class ec on ec.id=e.class_id where (e.name like '%storage%NSNL%' or e.name like '%injection%NSNL%' or e.name like '%co2_stor%' or e.name like '%CO2stor%' or e.name like '%storcap%') and ec.name like '%user_constraint%' or (e.name like '%user_constraint%co2%')"""
  print("==",n)
  for r in c.execute(q): print(r[0],r[1][:70],r[2],r[3][:150])
  print([r[0] for r in c.execute("select e.name from entity e join entity_class ec on ec.id=e.class_id where ec.name='user_constraint'")])
