import sqlite3, os, json, sys, datetime
paths = {
 "Biomass_DB": "biomass_db/biomass_db.sqlite",
 "Cargo_DB": "cargo_db/cargo_db.sqlite",
 "Commodity_DB": "commodity_db/commodity_db.sqlite",
 "Gas_DB": "gas_db/gas_db.sqlite",
 "Heat_DB": "heat_db/heat_db.sqlite",
 "Hydro_DB": "hydro_db/hydro_db.sqlite",
 "INES_DB": "ines_db/INES_DB.sqlite",
 "Industry_DB": "industry_db/industry_db.sqlite",
 "Other_Industry_DB": "other_industry_db/Other_Industry_DB.sqlite",
 "Power_DB": "power_db/power_db.sqlite",
 "RDemand_DB": "rdemand_db/rdemand_db.sqlite",
 "SpineOpt_target": "spineopt_target/SpineOpt_target.sqlite",
 "Transmission_DB": "transmission_db/transmission_db.sqlite",
 "Transport_DB": "transport_db/transport_db.sqlite",
 "VRE_DB": "vre_db/vre_db.sqlite",
 "Final_SpineOpt_Model": "final_spineopt_model/Final_SpineOpt_Model.sqlite",
}
root = ".spinetoolbox/items/"
out = {}
for n, rel in paths.items():
    p = root + rel
    if not os.path.exists(p):
        out[n] = {"MISSING": True}; continue
    st = os.stat(p)
    r = {"size": st.st_size,
         "mtime": datetime.datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds")}
    try:
        c = sqlite3.connect("file:%s?mode=ro" % p, uri=True)
        for t in ["entity", "entity_class", "parameter_value", "alternative"]:
            r[t] = c.execute("SELECT count(*) FROM %s" % t).fetchone()[0]
        c.close()
    except Exception as e:
        r["ERR"] = str(e)[:40]
    out[n] = r
tag = sys.argv[1]
json.dump(out, open("run_logs/fp_%s.json" % tag, "w"), indent=1)
for n, r in out.items():
    print("%-22s %9s %7s %7s  %s" % (n[:22], r.get("entity"), r.get("parameter_value"),
          r.get("alternative"), r.get("mtime")))
print("wrote run_logs/fp_%s.json" % tag)
