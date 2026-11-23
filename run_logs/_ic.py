import sqlite3
for p in [r"checkpoints\Investment_Results.3day_routeemis.sqlite",
          r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"]:
    c=sqlite3.connect(p)
    print(p.split("\\")[-1][:52], "->", c.execute("PRAGMA integrity_check").fetchone()[0])
    c.close()
