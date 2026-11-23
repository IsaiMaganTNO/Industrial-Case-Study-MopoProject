import sqlite3,glob
for n,db in [("MR",glob.glob(r"final_runs_pessimistic_ccs\3_*\input\*.sqlite")[0]),("S3",glob.glob(r"final_runs_pessimistic_ccs\6_*\input\*.sqlite")[0]),("S4",r"runs\3day_mr_frlu_ccslow_ccu_cap16_dac0_v3\input\Final_SpineOpt_Model.tiny.3day.mr_frlu_ccslow_ccu_cap16_dac0.v3.sqlite")]:
  c=sqlite3.connect(db); print("==",n)
  q="""select e.name,pd.name,cast(pv.value as text) from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id join entity e on e.id=pv.entity_id where e.name like '%CO2-injection-NSNL%'"""
  for r in c.execute(q): print(r[0][:80],r[1],r[2][:160])
