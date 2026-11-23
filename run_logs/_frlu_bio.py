import sqlite3
M = r"runs\3day_mr_frlu_ccslow_ccu_cap16_dac0\input\Final_SpineOpt_Model.tiny.3day.mr_frlu_ccslow_ccu_cap16_dac0.sqlite"
c = sqlite3.connect(M)
for cc in ("DE","DK","NO","UK","FR","LU","NLC1"):
    r = c.execute("""select count(*) from parameter_value pv join entity e on e.id=pv.entity_id where e.name=?""", (f"biomass-stock_{cc}",)).fetchone()[0]
    print(cc, "biomass-stock params:", r)
for db in [r".spinetoolbox\items\biomass_db\biomass_db.sqlite", r"EU_case\.spinetoolbox\items\biomass_db\biomass_db.sqlite"]:
    try:
        d = sqlite3.connect(db)
        regs = sorted({n.split("__")[-1] for (n,) in d.execute("select name from entity where name like '%\\_\\_%' escape '\\'")})
        print(db, len(regs), regs[:40])
    except Exception as e: print("ERR", db, e)
