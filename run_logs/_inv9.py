import os,sys,sqlite3
sys.path.insert(0,"tools")
from spinedb_api import DatabaseMapping, from_database
for n in ["nb_v2","nb_ctry"]:
  print("=====",n)
  res=rf"runs\3day_{n}\output\Investment_Results.3day_{n}.sqlite"
  with DatabaseMapping("sqlite:///"+os.path.abspath(res)) as db:
    for v in db.get_parameter_value_items(entity_class_name="report__node__stochastic_scenario"):
      nm=v["entity_byname"][1]
      if nm.startswith("salt-cavern_NLC") and v["parameter_definition_name"] in ("storages_invested_available","storages_decommissioned","storages_invested"):
        val=from_database(v["value"],v["type"]); print(nm,v["parameter_definition_name"],[round(float(x),2) for x in val.values])
  d=sqlite3.connect(rf"runs\3day_{n}\input\Final_SpineOpt_Model.tiny.3day.{n}.sqlite")
  print(d.execute("select e.name,pd.name,substr(pv.value,1,60) from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id where e.name like '%salt-cavern_NLC6%'").fetchall())
