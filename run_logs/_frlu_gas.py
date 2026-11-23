import sqlite3
d = sqlite3.connect(r".spinetoolbox\items\gas_db\gas_db.sqlite")
for cc in ("DE","UK","FR","LU","NLC1"):
    print(cc, sorted(n for (n,) in d.execute("select name from entity where name like ?", (f"%{cc}",)))[:15])
