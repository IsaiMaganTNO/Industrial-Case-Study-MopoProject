import sqlite3,glob,json
for db in sorted(glob.glob(r"checkpoints\*.sqlite")):
    try:
        c=sqlite3.connect("file:%s?mode=ro"%db,uri=True)
        r=c.execute("""SELECT cast(pv.value as text) FROM parameter_value pv
          JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
          JOIN entity e ON e.id=pv.entity_id
          WHERE e.name='atmosphere'
            AND pd.name='storage_investment_count_max_cumulative'""").fetchone()
        if r:
            d=json.loads(r[0])["data"]
            print("%-58s %s" % (db.split("\\")[-1][:58], d.get("2030-01-01T00:00:00")))
        c.close()
    except Exception as ex: pass
