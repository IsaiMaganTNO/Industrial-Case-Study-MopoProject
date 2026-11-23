import sqlite3,glob
for n,db in [("MR",glob.glob(r"final_runs_pessimistic_ccs\3_*\input\*.sqlite")[0]),("S4",r"runs\3day_mr_frlu_ccslow_ccu_cap16_dac0_v3\input\Final_SpineOpt_Model.tiny.3day.mr_frlu_ccslow_ccu_cap16_dac0.v3.sqlite")]:
  c=sqlite3.connect(db); print("==",n)
  q="""select ec.name,e.name,pd.name,a.name,cast(pv.value as text) from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id join entity e on e.id=pv.entity_id join entity_class ec on ec.id=e.class_id join alternative a on a.id=pv.alternative_id where e.name like '%NSNL0%' and pd.name not in ('vom_cost','flow_ratio_equality_coefficient')"""
  for r in c.execute(q): print(r[0],r[1][:70],r[2],r[3],r[4][:200])
