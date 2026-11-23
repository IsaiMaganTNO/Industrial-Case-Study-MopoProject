import sqlite3
for n,db in [("MR",r"final_runs_pessimistic_ccs\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK\input\Final_SpineOpt_Model.tiny.3day.mr_ccslow_ccu_cap16_dac0.sqlite"),("S3",r"final_runs_pessimistic_ccs\6_MixedRes_OptimisticCCS\input"),("S4",r"runs\3day_mr_frlu_ccslow_ccu_cap16_dac0_v3\input\Final_SpineOpt_Model.tiny.3day.mr_frlu_ccslow_ccu_cap16_dac0.v3.sqlite")]:
  import glob,os
  if os.path.isdir(db): db=glob.glob(db+r"\*.sqlite")[0]
  q="""select e.name,pd.name,cast(pv.value as text) from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id join entity e on e.id=pv.entity_id where (e.name like '%CO2-storage%' or e.name like '%CO2-injection%' or e.name like '%co2%cap%') and pd.name in ('node_state_cap','unit_capacity','storage_state_max','investment_count_max_cumulative','candidate_units','unit_investment_cost','fix_ratio_out_in_unit_flow','max_cumulated_unit_flow_from') """
  print("==",n); [print(r[0][:60],r[1],r[2][:120]) for r in sqlite3.connect(db).execute(q) if "NSNL" in r[0] or "NL" in r[0]][:20]
