import sqlite3, os, json

targets = {
 "TB_Final_SpineOpt_Model": ".spinetoolbox/items/final_spineopt_model/Final_SpineOpt_Model.sqlite",
 "TB_SpineOpt_target":      ".spinetoolbox/items/spineopt_target/SpineOpt_target.sqlite",
 "TB_INES_DB":              ".spinetoolbox/items/ines_db/INES_DB.sqlite",
 "TB_VRE_DB":               ".spinetoolbox/items/vre_db/vre_db.sqlite",
 "CKPT_vre15":              "checkpoints/Final_SpineOpt_Model.tiny.3day.gascap.vre15.sqlite",
}
out = {}
for name, p in targets.items():
    if not os.path.exists(p):
        print("MISSING", name, p); continue
    c = sqlite3.connect("file:%s?mode=ro" % p, uri=True)
    rec = {"size_mb": round(os.path.getsize(p)/1e6, 1)}
    for t in ["entity", "entity_class", "parameter_value",
              "parameter_definition", "alternative", "scenario"]:
        try:
            rec[t] = c.execute("SELECT count(*) FROM %s" % t).fetchone()[0]
        except Exception as e:
            rec[t] = "ERR"
    c.close()
    out[name] = rec
    print("%-26s %s" % (name, json.dumps(rec)))
json.dump(out, open("run_logs/baseline_fingerprint.json", "w"), indent=1)
print("\nwrote run_logs/baseline_fingerprint.json")
