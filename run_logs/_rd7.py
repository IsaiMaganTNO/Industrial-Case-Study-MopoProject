import sqlite3,re,collections
c=sqlite3.connect(r"file:.spinetoolbox/items/ines_db/ines_db.sqlite?mode=ro",uri=True)
ents=[r[0] for r in c.execute("SELECT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id WHERE ec.name='node__unit__node' OR ec.name='unit__node__node'")]
atm=[e for e in ents if "atmosphere" in e]
print("entities involving atmosphere:",len(atm))
cnt=collections.Counter()
for e in atm:
    m=re.search(r"_(BEC\d|NLC\d|DE|DK|NO|UK)(__|$)",e)
    cnt[m.group(1) if m else "?"]+=1
print(dict(cnt))
print(sorted(atm)[:6])
