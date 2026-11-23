import sqlite3, glob, os
for p in sorted(glob.glob(r".spinetoolbox\items\*\*.sqlite")):
    try:
        c=sqlite3.connect(p)
        ent=c.execute("select count(*) from entity").fetchone()[0]
        pv=c.execute("select count(*) from parameter_value").fetchone()[0]
        print(f"  {os.path.basename(os.path.dirname(p)):24} {os.path.getsize(p)/1e6:8.1f} MB  entities={ent:8,}  params={pv:10,}")
    except Exception as e:
        print(f"  {p}: {type(e).__name__} {e}")
