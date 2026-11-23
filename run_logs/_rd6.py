import sqlite3,re,collections
c=sqlite3.connect(r"file:.spinetoolbox/items/ines_db/ines_db.sqlite?mode=ro",uri=True)
q="""SELECT pd.name,e.name,pv.value FROM parameter_value pv
 JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
 JOIN entity e ON e.id=pv.entity_id"""
rows=list(c.execute(q))
for reg in ["BEC1","NLC1","DE","UK","NO","DK"]:
    hits=[(pn,en,v[:70]) for pn,en,v in rows if en=="bio_"+reg or en.startswith("bio_"+reg+"__")]
    print("== bio_%s : %d param rows"%(reg,len(hits)))
    for h in hits[:8]: print("    ",h[0],h[1][:40],h[2])
# look for any unit producing into bio node
print("\n== search param 'profile_limit_upper'/'capacity' on entities with 'bio_' second element")
ents=set(e for _,e,_ in rows)
b=[e for e in ents if "__bio_" in e]
print("entities with __bio_ :",len(b))
print(sorted(b)[:10])
