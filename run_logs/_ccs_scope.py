import sqlite3
d=sqlite3.connect(r"runs\3day_nb_v2\input\Final_SpineOpt_Model.tiny.3day.nb_v2.sqlite")
q=lambda s:d.execute(s).fetchall()
print("scenario alts:",q("select s.name,sa.rank,a.name from scenario_alternative sa join scenario s on s.id=sa.scenario_id join alternative a on a.id=sa.alternative_id order by sa.rank"))
print("all alts:",[r[0] for r in q("select name from alternative")])
print(q("""select e.name,pd.name,a.name,substr(pv.value,1,90) from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id
 join entity e on e.id=pv.entity_id join alternative a on a.id=pv.alternative_id where e.name like '%NSNL0%' and a.name like '%CO2%' order by e.name,a.name"""))
print("CO2 cost params by alt:",q("""select pd.name,a.name,count(*) from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id
 join entity e on e.id=pv.entity_id join alternative a on a.id=pv.alternative_id where (e.name like '%CO2%' or e.name like '%injection%') and pd.name like '%cost%' group by 1,2"""))
