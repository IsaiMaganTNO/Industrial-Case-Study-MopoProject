import sqlite3
A=sqlite3.connect(r"runs\3day_nb_v2\input\Final_SpineOpt_Model.tiny.3day.nb_v2.sqlite"); B=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.nb_ccslow.sqlite")
Q="""select c.name,e.name,pd.name,al.name,pv.value from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id
 join entity e on e.id=pv.entity_id join entity_class c on c.id=e.class_id join alternative al on al.id=pv.alternative_id"""
a={r[:4]:r[4] for r in A.execute(Q)}; b={r[:4]:r[4] for r in B.execute(Q)}
print("params",len(a),len(b),"added",len(b.keys()-a.keys()),"removed",len(a.keys()-b.keys()))
ch=[k for k in a if k in b and a[k]!=b[k]]
import collections; print("changed",len(ch),collections.Counter(k[2] for k in ch))
ents=lambda d:set(d.execute("select class_id,name from entity"))
print("entities identical",ents(A)==ents(B))
sa=lambda d:d.execute("select s.name,sa.rank,a.name from scenario_alternative sa join scenario s on s.id=sa.scenario_id join alternative a on a.id=sa.alternative_id order by rank").fetchall()
print("scenario:",[r[2] for r in sa(B)])
print("diff in scenario:",set(sa(A))^set(sa(B)))
