import sqlite3, json, collections
d = sqlite3.connect(r".spinetoolbox\items\rdemand_db\rdemand_db.sqlite")
print("rdemand regions:", sorted({n.split("__")[-1] for (n,) in d.execute("select name from entity") if "__" in n})[-8:])
b = sqlite3.connect(r".spinetoolbox\items\biomass_db\biomass_db.sqlite")
regs = sorted({n.split("__")[-1] for (n,) in b.execute("select name from entity") if "__" in n})
print("biomass regions:", regs)
