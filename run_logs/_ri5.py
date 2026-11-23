import sqlite3,collections,re
c=sqlite3.connect(r"file:EU_case/.spinetoolbox/items/transport_db/transport_db.sqlite?mode=ro",uri=True)
rows=list(c.execute("""SELECT a.name,e.name FROM parameter_value pv JOIN alternative a ON a.id=pv.alternative_id
 JOIN entity e ON e.id=pv.entity_id"""))
c.close()
pat=re.compile(r"(^|__)(DE|DK|NO|UK)$")
cnt=collections.Counter(a for a,e in rows if pat.search(e.split("__")[-1]) or e.split("__")[-1] in ("DE","DK","NO","UK"))
print("EU transport values for 4 countries by alt:",dict(cnt))
c=sqlite3.connect(r"file:.spinetoolbox/items/industry_db/industry_db.sqlite?mode=ro",uri=True)
print("IC1 industry CO2_emitted:",c.execute("""SELECT count(*) FROM parameter_value pv
 JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id WHERE pd.name='CO2_emitted'""").fetchone()[0])
c.close()
c=sqlite3.connect(r"file:EU_case/.spinetoolbox/items/industry_db/industry_db.sqlite?mode=ro",uri=True)
print("EU industry CO2_emitted defs:",c.execute("SELECT count(*) FROM parameter_definition WHERE name='CO2_emitted'").fetchone()[0])
print("EU industry CO2_captured vals:",c.execute("""SELECT count(*) FROM parameter_value pv
 JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id WHERE pd.name='CO2_captured'""").fetchone()[0])
c.close()
