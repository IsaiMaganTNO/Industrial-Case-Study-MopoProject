import sqlite3,sys
con=sqlite3.connect(sys.argv[1]);c=con.cursor()
q="""select ec.name,e.name,pd.name,pv.value from parameter_value pv join entity e on e.id=pv.entity_id
join entity_class ec on ec.id=e.class_id join parameter_definition pd on pd.id=pv.parameter_definition_id
where e.name like '%global-H2%' or e.name like '%LH2%' or e.name like '%H2-terminal%' or e.name like '%H2-import%'"""
for r in c.execute(q): print(r[0],'|',r[1],'|',r[2],'|',str(r[3])[:120])
print([n for (n,) in c.execute("select name from entity where name like '%global-H2%' or name like '%LH2%'")][:40])
