import sqlite3
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.mixedres.sqlite")
for r in c.execute("select s.name,a.name,sa.rank from scenario_alternative sa join scenario s on s.id=sa.scenario_id join alternative a on a.id=sa.alternative_id where s.active=1 or 1 order by s.name,sa.rank"): print(r)
