import sqlite3,glob
for n,db in [("MR",glob.glob(r"final_runs_pessimistic_ccs\3_*\input\*.sqlite")[0]),("S3",glob.glob(r"final_runs_pessimistic_ccs\6_*\input\*.sqlite")[0]),("S4",r"runs\3day_mr_frlu_ccslow_ccu_cap16_dac0_v3\input\Final_SpineOpt_Model.tiny.3day.mr_frlu_ccslow_ccu_cap16_dac0.v3.sqlite"),("S4x",r"share_frlu_xpress\input.sqlite")]:
  c=sqlite3.connect(db); print("==",n)
  print(c.execute("select s.name, group_concat(a.name||':'||sa.rank, ', ') from scenario s join scenario_alternative sa on sa.scenario_id=s.id join alternative a on a.id=sa.alternative_id group by s.name").fetchall())
