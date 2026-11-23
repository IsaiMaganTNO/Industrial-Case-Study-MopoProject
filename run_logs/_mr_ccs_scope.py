import sqlite3,collections
d=sqlite3.connect(r"runs\3day_mr_fix\input\Final_SpineOpt_Model.tiny.3day.mr_fix.sqlite")
q=lambda s,*a:d.execute(s,a).fetchall()
print("scenario:",[r[0] for r in q("select a.name from scenario_alternative sa join alternative a on a.id=sa.alternative_id order by sa.rank")])
for a in ["high_CO2","low_CO2"]:
  r=q("""select c.name,pd.name,count(*) from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id join entity e on e.id=pv.entity_id
   join entity_class c on c.id=e.class_id join alternative al on al.id=pv.alternative_id where al.name=? group by 1,2""",a)
  ents=sorted(x[0] for x in q("select distinct e.name from parameter_value pv join entity e on e.id=pv.entity_id join alternative al on al.id=pv.alternative_id where al.name=?",a))
  print(a,r,len(ents),ents)
print("CO2 cost params:",q("""select pd.name,al.name,count(*) from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id join entity e on e.id=pv.entity_id
 join alternative al on al.id=pv.alternative_id where (e.name like '%CO2%' or e.name like '%injection%') and pd.name like '%cost%' group by 1,2"""))
print("injection units:",[r[0] for r in q("select e.name from entity e join entity_class c on c.id=e.class_id where c.name='unit' and e.name like 'CO2-injection%'")])
