import sqlite3, collections
# measure total bio_* node inflow from the RESULTS db (unit_flow into/out of bio nodes)
for tag,res in [("BASELINE",r"checkpoints\Investment_Results.3day_routeemis.sqlite"),
                ("BIDIR   ",r"checkpoints\Investment_Results.3day_co2bidir.sqlite")]:
    c=sqlite3.connect(res)
    rows=c.execute("""select ec.name,count(*) from entity e join entity_class ec on ec.id=e.class_id
      where lower(e.name) like '%bio%' group by 1 order by 2 desc limit 5""").fetchall()
    print(tag,"result classes w/ bio:",rows)
