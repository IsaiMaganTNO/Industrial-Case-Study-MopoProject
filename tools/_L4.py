import sqlite3
c=sqlite3.connect(r"reports_3day_group1\INPUT_Final_SpineOpt_Model.tiny.3day.group1.sqlite")
q="""SELECT pd.name, COUNT(*) FROM parameter_value pv
     JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
     WHERE pd.name LIKE '%avail%' OR pd.name LIKE '%profile%' OR pd.name LIKE '%factor%'
        OR pd.name LIKE '%ratio%' GROUP BY pd.name ORDER BY 2 DESC"""
for r in c.execute(q): print(f"{r[0]:46s} {r[1]}")
