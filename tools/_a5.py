import sqlite3
for lbl,p in {"base":r"checkpoints\Final_SpineOpt_Model.tiny.3day.group1.sqlite",
              "patched":r"checkpoints\Final_SpineOpt_Model.tiny.3day.group1.biocap365.sqlite"}.items():
    c=sqlite3.connect(p)
    r=c.execute("""SELECT typeof(pv.value),CAST(pv.value AS TEXT) FROM parameter_value pv
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      JOIN entity e ON e.id=pv.entity_id JOIN alternative al ON al.id=pv.alternative_id
      WHERE pd.name='storage_investment_count_fix_cumulative' AND e.name='biomass-stock_BEC1'
        AND al.name='medium_bio'""").fetchone()
    print("%-8s typeof=%-6s value=%s"%(lbl,r[0],r[1][:40]))
