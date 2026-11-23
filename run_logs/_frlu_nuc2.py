import sqlite3, glob
for db in [r".spinetoolbox\items\power_db\power_db.sqlite", r".spinetoolbox\items\ines_db\INES_DB.sqlite", r"EU_case\.spinetoolbox\items\power_db\power_db.sqlite"] + glob.glob(r".spinetoolbox\items\*power*\*.sqlite"):
    try:
        c = sqlite3.connect(db)
        r = c.execute("select name from entity where name like '%nuclear%' and (name like '%FR%' or name like '%UK%' or name like '%BE%') limit 15").fetchall()
        print("==", db); [print("  ", x[0]) for x in r]
    except Exception as e: print("ERR", db, e)
