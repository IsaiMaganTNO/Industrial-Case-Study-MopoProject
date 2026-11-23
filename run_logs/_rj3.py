import sqlite3,collections,json
c=sqlite3.connect(r"file:EU_case/.spinetoolbox/items/heat_db/heat_db.sqlite?mode=ro",uri=True)
rows=list(c.execute("""SELECT pd.name,ec.name,e.name,a.name,pv.type,length(pv.value) FROM parameter_value pv
 JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
 JOIN entity e ON e.id=pv.entity_id JOIN entity_class ec ON ec.id=e.class_id
 JOIN alternative a ON a.id=pv.alternative_id"""))
c.close()
four=[r for r in rows if r[2].split("__")[-1] in ("DE","DK","NO","UK")]
print("EU heat: total values",len(rows),"for 4 countries",len(four))
print("by param/alt:",collections.Counter((r[0],r[3]) for r in four))
print("\nflow_profile entries for 4 countries:")
for r in four:
    if r[0]=="flow_profile": print("   ",r[1],r[2],r[3],r[4],"bytes",r[5])
