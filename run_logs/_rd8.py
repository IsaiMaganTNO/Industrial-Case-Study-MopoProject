import sqlite3,re,collections
c=sqlite3.connect(r"file:.spinetoolbox/items/ines_db/ines_db.sqlite?mode=ro",uri=True)
rows=list(c.execute("SELECT ec.name,e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id"))
atm=[(k,e) for k,e in rows if "atmosphere" in e]
print("atmosphere entities:",len(atm))
print(collections.Counter(k for k,_ in atm))
cnt=collections.Counter()
for k,e in atm:
    m=re.search(r"_(BEC\d|NLC\d|DE|DK|NO|UK)(__|$)",e)
    cnt[m.group(1) if m else "NOREG"]+=1
print(dict(cnt))
for k,e in atm[:8]: print("  ",k,"|",e[:90])
