import sqlite3, re, collections
M = r"runs\3day_mr_frlu_ccslow_ccu_cap16_dac0\input\Final_SpineOpt_Model.tiny.3day.mr_frlu_ccslow_ccu_cap16_dac0.sqlite"
c = sqlite3.connect(M)
ents = c.execute("select ec.name, e.name from entity e join entity_class ec on ec.id=e.class_id where ec.name in ('unit','node','connection')").fetchall()
for cc in ("DE","UK","FR","LU"):
    pat = re.compile(rf"(^|_){cc}($|_)")
    by = collections.Counter(cl for cl, n in ents if pat.search(n))
    ex = sorted(n for cl, n in ents if cl == "unit" and pat.search(n) and "existing" in n)
    conn = sorted(n for cl, n in ents if cl == "connection" and pat.search(n) and "CO2" not in n)
    print(f"== {cc}: {dict(by)}")
    print("   existing units:", len(ex), ex[:25])
    print("   non-CO2 connections:", len(conn), conn[:25])
