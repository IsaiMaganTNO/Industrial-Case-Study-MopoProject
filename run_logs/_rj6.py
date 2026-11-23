import sqlite3,collections,os
p=r"EU_case\.spinetoolbox\items\transport_db\transport_db.sqlite"
print("size GB %.2f"%(os.path.getsize(p)/1e9))
c=sqlite3.connect("file:%s?mode=ro"%p.replace("\\","/"),uri=True)
rows=list(c.execute("""SELECT pd.name,e.name,a.name,length(pv.value) FROM parameter_value pv
 JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id JOIN entity e ON e.id=pv.entity_id
 JOIN alternative a ON a.id=pv.alternative_id"""))
c.close()
four=[r for r in rows if r[1].split("__")[-1] in ("DE","DK","NO","UK")]
print("total values",len(rows),"-> 4 countries",len(four))
print("bytes for 4 countries: %.1f MB"%(sum(r[3] for r in four)/1e6))
print("by param:",collections.Counter(r[0] for r in four))
print("alts:",collections.Counter(r[2] for r in four))
