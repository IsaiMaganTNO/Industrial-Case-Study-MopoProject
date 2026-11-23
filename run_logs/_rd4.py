import sqlite3,re,json
c=sqlite3.connect(r"file:.spinetoolbox/items/ines_db/ines_db.sqlite?mode=ro",uri=True)
q="""SELECT pd.name,e.name,pv.value FROM parameter_value pv
 JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
 JOIN entity e ON e.id=pv.entity_id"""
rows=list(c.execute(q))
print("== bio_* nodes and their params")
import collections
d=collections.defaultdict(list)
for pn,en,v in rows:
    if en.startswith("bio_") or en=="bio": d[en].append(pn)
for k in sorted(d): print("  %-12s %s"%(k,sorted(set(d[k]))))
print("\n== atmosphere")
for pn,en,v in rows:
    if en=="atmosphere": print("  ",pn,v[:220])
print("\n== entities whose name ends in _DE/_DK/_NO/_UK and start with bio")
n=[e for e in set(r[1] for r in rows) if re.search(r"_(DE|DK|NO|UK)$",e) and "bio" in e]
print("  count",len(n),sorted(n)[:20])
