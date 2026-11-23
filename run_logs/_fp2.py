import sqlite3, os, glob
ps = sorted(glob.glob("checkpoints/Final_SpineOpt_Model*.sqlite"))
print("%-58s %7s %7s" % ("file", "entity", "pval"))
for p in ps:
    try:
        c = sqlite3.connect("file:%s?mode=ro" % p, uri=True)
        e = c.execute("SELECT count(*) FROM entity").fetchone()[0]
        v = c.execute("SELECT count(*) FROM parameter_value").fetchone()[0]
        c.close()
    except Exception as ex:
        e, v = "ERR", str(ex)[:20]
    print("%-58s %7s %7s" % (os.path.basename(p)[:58], e, v))
