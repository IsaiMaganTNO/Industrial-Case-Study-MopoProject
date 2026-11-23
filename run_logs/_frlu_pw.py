import sqlite3
for db in [r".spinetoolbox\items\power_db\power_db.sqlite", r"EU_case\.spinetoolbox\items\power_db\power_db.sqlite"]:
    c = sqlite3.connect(db)
    for cc in ("FR","LU","DE","UK"):
        n = c.execute("select count(*) from entity where name like ? or name like ?", (f"%\\_\\_{cc}", f"%\\_{cc}")).fetchone()[0]
        ex = [r[0] for r in c.execute("select name from entity where name like ? limit 6", (f"%existing__{cc}",))]
        print(db[:40], cc, n, ex)
