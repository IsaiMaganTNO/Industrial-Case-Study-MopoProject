import sqlite3, json
for lab,db in [("MR",r"final_runs_pessimistic_ccs\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK\input\Final_SpineOpt_Model.tiny.3day.mr_ccslow_ccu_cap16_dac0.sqlite"),
               ("RP10",r"runs\rp10_mr_noblend\Final_SpineOpt_Model.tiny.10day_noblend.mr_ccslow_ccu_cap16_dac0.sqlite")]:
    c=sqlite3.connect(db); print("=====",lab)
    rows=c.execute("""select e.name,pd.name,pv.type,pv.value from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id
      join entity_class ec on ec.id=e.class_id where ec.name='temporal_block'""").fetchall()
    for n,p,t,v in rows:
        v=v.decode() if isinstance(v,bytes) else v
        if p=="representative_blocks_by_period": 
            d=json.loads(v); print(n,p,"type",d.get("type"),"entries",len(d.get("data",{})) if isinstance(d.get("data"),(dict,list)) else "?"); continue
        if n.startswith("representative_period") and p not in ("weight","block_start","resolution"): continue
        print(n,"|",p,"|",str(v)[:120])
    print("long-term storage nodes:", c.execute("""select count(*) from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id where pd.name='storage_longterm_active' """).fetchone())
    print("model params:", [(p,(v.decode() if isinstance(v,bytes) else v)[:60]) for p,v in c.execute("""select pd.name,pv.value from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id join entity_class ec on ec.id=e.class_id where ec.name='model'""")])
