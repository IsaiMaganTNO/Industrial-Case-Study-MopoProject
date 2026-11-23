import sqlite3,os,glob,re
for p in sorted(glob.glob(r"EU_case\.spinetoolbox\items\*\*.sqlite")):
    lab=os.path.basename(p)
    try:
        c=sqlite3.connect("file:%s?mode=ro"%p.replace("\\","/"),uri=True)
        rs=[r[0] for r in c.execute("SELECT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id WHERE ec.name='region'")]
        tgt=[r for r in rs if r in ("DE","DK","NO","UK")]
        print("%-26s size=%-10d regions=%-5d has DE/DK/NO/UK: %s"%(lab,os.path.getsize(p),len(rs),sorted(tgt)))
        c.close()
    except Exception as ex:
        print("%-26s ERR %s"%(lab,ex))
