import sqlite3,json
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
def show(fam,par):
    r=c.execute("""SELECT e.name,pv.value FROM parameter_value pv JOIN entity e ON e.id=pv.entity_id
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      WHERE pd.name=? AND e.name LIKE ? LIMIT 2""",(par,fam+"_%")).fetchall()
    for n,v in r:
        try: s=bytes(v).decode()[:52]
        except Exception: s=str(v)[:52]
        print("   %-24s %-30s %s"%(n[:24],par[:30],s))
for fam in ("CEM2-(Afm)MEA","LC3-(Afm)Oxy-MEA","CEM2-(Afm)"):
    print("=== %s ==="%fam)
    for par in ("investment_count_max_cumulative","investment_count_fix_new","unit_investment_cost"):
        show(fam,par)
