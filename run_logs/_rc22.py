import sqlite3,collections,os
EXTRA={'AT','CH','CZ','FR','IE','LU','PL','SE','FI','DE','DK','NO','UK'}
for lab,p in [("BASELINE (pre-mixedres backup)", r"backups\spinetoolbox-items-pre-mixedres\items\ines_db\ines_db.sqlite"),
              ("NEW (mixed-resolution)",        r".spinetoolbox\items\ines_db\ines_db.sqlite")]:
    if not os.path.exists(p): print(lab,"MISSING"); continue
    c=sqlite3.connect("file:%s?mode=ro"%p.replace("\\","/"),uri=True)
    rows=[(r[0],r[1]) for r in c.execute("SELECT ec.name,e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id")]
    cnt=collections.Counter()
    for cls,n in rows:
        s=n.rsplit("_",1)[-1]
        if s in EXTRA: cnt[s]+=1
    print("%-32s total_ents=%d" % (lab,len(rows)))
    print("    foreign-suffix entity counts:",dict(sorted(cnt.items())))
    c.close()
