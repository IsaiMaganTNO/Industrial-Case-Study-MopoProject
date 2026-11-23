import sqlite3, re, collections, os
M = r"runs\3day_mr_frlu_ccslow_ccu_cap16_dac0\input\Final_SpineOpt_Model.tiny.3day.mr_frlu_ccslow_ccu_cap16_dac0.sqlite"
c = sqlite3.connect(M)
units = [n for (n,) in c.execute("select e.name from entity e join entity_class ec on ec.id=e.class_id where ec.name='unit'")]
def tech(cc): return {n[:-len(cc)-1] for n in units if n.endswith("_"+cc)}
ref = [tech(x) for x in ("DE","DK","NO","UK")]
common = {t for t in set().union(*ref) if sum(t in r for r in ref) >= 3}
lu, fr = tech("LU"), tech("FR")
miss = sorted(common - lu)
print("LU missing unit techs:", len(miss)); print(miss)
print("FR missing unit techs:", sorted(common - fr))
# are they in the EU source DBs for LU?
base = r"EU_case\.spinetoolbox\items"
for it in ("industry_db","other_industry_db","heat_db","transport_db","power_db"):
    db = os.path.join(base, it, it + ".sqlite")
    if not os.path.exists(db): print("no", db); continue
    d = sqlite3.connect(db)
    names = [n for (n,) in d.execute("select name from entity")]
    lu_n = {n.split("__")[0] for n in names if n.endswith("__LU")}
    de_n = {n.split("__")[0] for n in names if n.endswith("__DE")}
    print(f"EU {it:18s} DE techs {len(de_n):4d}  LU techs {len(lu_n):4d}  DE-not-LU sample {sorted(de_n-lu_n)[:12]}")
