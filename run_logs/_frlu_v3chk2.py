import sqlite3
d = sqlite3.connect(r".spinetoolbox\items\rdemand_db\rdemand_db.sqlite")
r = sorted({n.split("__")[-1] for (n,) in d.execute("select name from entity") if "__" in n})
print(len(r), r)
