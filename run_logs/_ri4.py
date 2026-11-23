import sqlite3,collections
# 1) transport flex alternatives: does EU have GA_flex0 (the one our scenario uses)?
c=sqlite3.connect(r"file:EU_case/.spinetoolbox/items/transport_db/transport_db.sqlite?mode=ro",uri=True)
q="""SELECT a.name,count(*) FROM parameter_value pv JOIN alternative a ON a.id=pv.alternative_id
 JOIN entity e ON e.id=pv.entity_id GROUP BY a.name"""
print("EU transport values per alternative:",dict(c.execute(q)))
# restrict to DE/DK/NO/UK
q2="""SELECT a.name,count(*) FROM parameter_value pv JOIN alternative a ON a.id=pv.alternative_id
 JOIN entity e ON e.id=pv.entity_id WHERE e.name LIKE '%\_DE' ESCAPE '\' OR e.name LIKE '%\_DK' ESCAPE '\'
 OR e.name LIKE '%\_NO' ESCAPE '\' OR e.name LIKE '%\_UK' ESCAPE '\' GROUP BY a.name"""
print("EU transport values for 4 countries:",dict(c.execute(q2)))
c.close()
# 2) CO2_emitted missing in EU industry - how many values in ours?
c=sqlite3.connect(r"file:.spinetoolbox/items/industry_db/industry_db.sqlite?mode=ro",uri=True)
print("IC1 industry CO2_emitted count:",c.execute("""SELECT count(*) FROM parameter_value pv
 JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id WHERE pd.name='CO2_emitted'""").fetchone())
c.close()
c=sqlite3.connect(r"file:EU_case/.spinetoolbox/items/industry_db/industry_db.sqlite?mode=ro",uri=True)
print("EU industry has param def CO2_emitted:",c.execute("SELECT count(*) FROM parameter_definition WHERE name='CO2_emitted'").fetchone())
print("EU industry CO2_captured count:",c.execute("""SELECT count(*) FROM parameter_value pv
 JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id WHERE pd.name='CO2_captured'""").fetchone())
c.close()
