import sqlite3
d=sqlite3.connect(r"runs\3day_nb_v2\input\Final_SpineOpt_Model.tiny.3day.nb_v2.sqlite")
for a in ["high_CO2","low_CO2","medium_CO2"]:
  print(a,d.execute("""select e.name,pd.name from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id
   join entity e on e.id=pv.entity_id join alternative al on al.id=pv.alternative_id where al.name=? order by 1,2""",(a,)).fetchall())
