import sqlite3, json
for lab,db in [("MR",r"final_runs_pessimistic_ccs\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK\input\Final_SpineOpt_Model.tiny.3day.mr_ccslow_ccu_cap16_dac0.sqlite"),
               ("RP10",r"runs\rp10_mr_noblend\Final_SpineOpt_Model.tiny.10day_noblend.mr_ccslow_ccu_cap16_dac0.sqlite")]:
    c=sqlite3.connect(db)
    w=[r[0] for r in c.execute("""select pv.value from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id where pd.name='weight' and e.name like 'representative_period_2050%'""")]
    print(lab,"n reps 2050:",len(w),"sum weights:",round(sum(float(x) for x in w),2))
    v=c.execute("""select pv.value from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id where pd.name='representative_blocks_by_period' and e.name='operations_y2050'""").fetchone()[0]
    print(lab,"rbp y2050:", (v.decode() if isinstance(v,bytes) else v)[:600])
    print(lab,"block_end rp2050_1:", c.execute("""select pv.value from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id where pd.name='block_end' and e.name='representative_period_2050_1'""").fetchone())
