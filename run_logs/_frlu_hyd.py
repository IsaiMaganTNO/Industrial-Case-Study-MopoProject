import sqlite3, os
for tag, base in (("ours", r".spinetoolbox\items"), ("EU", r"EU_case\.spinetoolbox\items")):
    db = os.path.join(base, "hydro_db", "hydro_db.sqlite")
    d = sqlite3.connect(db)
    regs = sorted({n.split("__")[-1] for (n,) in d.execute("select name from entity") if "__" in n})
    print(tag, "hydro regions:", regs)
    for cc in ("DE","FR","LU"):
        print("  ", cc, [n for (n,) in d.execute("select name from entity where name like ?", (f"%__{cc}",))])
