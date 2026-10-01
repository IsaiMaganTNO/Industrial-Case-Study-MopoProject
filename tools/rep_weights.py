"""Does the representative day get weighted up to a full year?"""
from spinedb_api import DatabaseMapping
from spinedb_api.parameter_value import from_database

for tag, url in (("TINY (solved)", "sqlite:///checkpoints/Final_SpineOpt_Model.tiny.sqlite"),
                 ("FULL (untouched)", "sqlite:///.spinetoolbox/items/final_spineopt_model/Final_SpineOpt_Model.sqlite")):
    print("=" * 64); print(tag)
    with DatabaseMapping(url) as db:
        for v in db.get_parameter_value_items():
            if v["parameter_definition_name"] != "representative_blocks_by_period":
                continue
            m = from_database(v["value"], v["type"])
            idx = list(m.indexes)
            print("  %-22s [%s]  entries=%d" % (v["entity_byname"][0], v["alternative_name"], len(idx)))
            for i, val in list(zip(idx, m.values))[:3]:
                try:
                    arr = [float(x) for x in val.values]
                except Exception:
                    arr = val
                print("      %s -> %s   (sum=%s)" % (str(i)[:19], [round(a,6) for a in arr][:6], round(sum(arr),6)))
            if len(idx) > 3:
                tot = 0.0
                for val in m.values:
                    tot += sum(float(x) for x in val.values)
                print("      ... TOTAL of all coefficients across all entries = %.4f" % tot)
    print()
