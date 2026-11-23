import sqlite3,json
m=sqlite3.connect("file:%s?mode=ro"%r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.co2div365.sqlite",uri=True)
# which regions can reach NSNL031 / NSNL012?
for res in ("NSNL031","NSNL012"):
    rs=m.execute("""SELECT DISTINCT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id
      WHERE ec.name='node__to_unit' AND e.name LIKE ?""",("%CO2-injection-"+res+"%",)).fetchall()
    regs=sorted(set(n.split("__")[0] for (n,) in rs))
    print(res,"fed from:",regs)
# is BEC6 (cement region) connected to any CO2 store?
rs=m.execute("""SELECT DISTINCT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id
  WHERE ec.name='node__to_unit' AND e.name LIKE 'CO2_BEC%'""").fetchall()
print("\nBE CO2 nodes feeding units:",sorted(set(n.split('__')[0] for (n,) in rs)))
for (n,) in rs[:14]: print("   ",n[:74])
m.close()
