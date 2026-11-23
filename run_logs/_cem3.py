import sqlite3
db=r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.co2div365.sqlite"
c=sqlite3.connect("file:%s?mode=ro"%db,uri=True)
for fam in ["CEM2-(Afm)MEA","CEM2-(Afm)","LC3-(Afm)MEA","CEM2-(BMW)MEA"]:
    rs=c.execute("""SELECT pd.name, count(*), min(cast(pv.value as text))
      FROM parameter_value pv
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      JOIN entity e ON e.id=pv.entity_id
      JOIN entity_class ec ON ec.id=e.class_id
      WHERE ec.name='unit' AND e.name LIKE ?
      GROUP BY pd.name ORDER BY pd.name""",(fam.replace("(","(")+"__%",)).fetchall()
    rs2=c.execute("""SELECT pd.name, count(*)
      FROM parameter_value pv
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      JOIN entity e ON e.id=pv.entity_id
      JOIN entity_class ec ON ec.id=e.class_id
      WHERE ec.name='unit' AND e.name GLOB ? GROUP BY pd.name""",(fam+"_*",)).fetchall()
    print(fam,"->",rs2)
c.close()
