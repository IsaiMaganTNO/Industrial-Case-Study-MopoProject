import sqlite3,glob,os
for db in sorted(glob.glob(r"checkpoints\Final_SpineOpt_Model.tiny*1rep*.sqlite"))+[r"runs\3day_mr_frlu_ccslow_ccu_cap16_dac0_v3\input\Final_SpineOpt_Model.tiny.3day.mr_frlu_ccslow_ccu_cap16_dac0.v3.sqlite"]:
    c=sqlite3.connect(db)
    sc=c.execute("select name from scenario").fetchall()
    tb=c.execute("select count(*) from entity e join entity_class ec on e.class_id=ec.id where ec.name='temporal_block'").fetchone()
    print(os.path.basename(db), "scen=",sc, "tblocks=",tb)
