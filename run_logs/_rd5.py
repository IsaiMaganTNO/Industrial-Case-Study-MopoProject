import sqlite3,re,collections
c=sqlite3.connect(r"file:.spinetoolbox/items/ines_db/ines_db.sqlite?mode=ro",uri=True)
q="""SELECT pd.name,e.name,a.name,pv.value FROM parameter_value pv
 JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
 JOIN entity e ON e.id=pv.entity_id JOIN alternative a ON a.id=pv.alternative_id"""
rows=list(c.execute(q))
# biomass supply units
sup=[r for r in rows if re.match(r"^bio-(supply|potential|prod)",r[1]) or "bio-sup" in r[1]]
print("bio-supply-ish:",len(sup))
ents=sorted(set(r[1] for r in rows))
cand=[e for e in ents if e.startswith("bio") and not e.startswith("bio_") and not e.startswith("bio-diges") and not e.startswith("bioST")]
print("candidate bio entities:",sorted(set(cand))[:30])
# which entities FEED bio_ nodes
print("\nentities containing '__bio_' as OUTPUT (name starts with tech, 2nd part bio_):")
feed=[e for e in ents if re.match(r"^[^_]*_[A-Z]+\d*__bio_",e)]
print(len(feed),sorted(set(feed))[:20])
