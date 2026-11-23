import sqlite3
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
print("=== scenarios and their alternatives (in order) ===")
for s,a,r in c.execute("""select s.name, al.name, sa.rank from scenario_alternative sa
  join scenario s on s.id=sa.scenario_id join alternative al on al.id=sa.alternative_id order by s.name, sa.rank"""):
    print(f"  {s:30s} rank{r:3d}  {a}")
print()
print("=== all alternatives ===")
for (a,) in c.execute("select name from alternative order by name"): print("  ",a)
