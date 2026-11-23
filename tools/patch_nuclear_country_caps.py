"""Per-country NEW-BUILD nuclear caps (workbook global_constraints_industry_case_study.xlsx,
sheet scenario_config.yaml, set_technology_buildout, "maximum invested capacity in GW", TYNDP2024).

Creates investment_group nuclear-3_<CC> with unit__investment_group links to the candidate
units nuclear-3_<CC>... (NOT nuclear-3-existing_*), and investment_count_total_max_cumulative
(capacity_per_unit = 1 GW, so units == GW) in alternative Base.
Time series stamped 2030-01-01 / 2040-01-01 / 2050-01-01 / 2060-01-01, so the 2040 cap applies from 2040
(user decision 2026-10-09; other inputs use 2041).
Countries with no candidate units in the DB are skipped (e.g. UK in the IC1 run).
Usage: patch_nuclear_country_caps.py SRC DST [--dry-run]
"""
import argparse, shutil, os, re, sys
from spinedb_api import DatabaseMapping, to_database
from spinedb_api.parameter_value import TimeSeriesVariableResolution as TimeSeriesVariable
import numpy as np
CAPS = {"NL": (0, 4, 5), "BE": (0, 6, 6), "UK": (6, 11, 13), "NO": (0, 0, 0), "DE": (0, 0, 0), "DK": (0, 0, 0),
        "FR": (0, 6, 27), "LU": (0, 0, 0)}  # FR/LU: global_constraints_industry_case_study_FR_LU.xlsx (FR: RTE Futurs energetiques 2050)
ap = argparse.ArgumentParser(); ap.add_argument("src"); ap.add_argument("dst"); ap.add_argument("--dry-run", action="store_true")
a = ap.parse_args()
if not a.dry_run: shutil.copyfile(a.src, a.dst)
url = "sqlite:///" + os.path.abspath(a.src if a.dry_run else a.dst)
with DatabaseMapping(url) as db:
    units = [e["name"] for e in db.get_entity_items(entity_class_name="unit") if re.match(r"^nuclear-3_", e["name"])]
    def cc(n):
        m = re.match(r"^nuclear-3_((BE|NL)C\d|DE|DK|NO|UK|FR|LU)$", n); return None if not m else m.group(1)[:2]
    groups = {}
    for u in units:
        c = cc(u)
        if c is None: sys.exit("ABORT: unrecognised nuclear unit name %s" % u)
        groups.setdefault(c, []).append(u)
    for c, us in sorted(groups.items()):
        print("%s caps %s GW -> units %s" % (c, CAPS[c], us))
    if a.dry_run: print("DRY RUN"); sys.exit()
    for c, us in groups.items():
        g = "nuclear-3_" + c
        db.add_entity(entity_class_name="investment_group", name=g)
        for u in us:
            db.add_entity(entity_class_name="unit__investment_group", element_name_list=(u, g))
        v = CAPS[c]
        ts = TimeSeriesVariable(np.array(["2030-01-01T00:00:00", "2040-01-01T00:00:00", "2050-01-01T00:00:00", "2060-01-01T00:00:00"], dtype="datetime64[s]"),
                                np.array([float(v[0]), float(v[1]), float(v[2]), float(v[2])]), ignore_year=False, repeat=False)
        val, typ = to_database(ts)
        db.add_parameter_value(entity_class_name="investment_group", entity_byname=(g,),
                               parameter_definition_name="investment_count_total_max_cumulative",
                               alternative_name="Base", value=val, type=typ)
    db.commit_session("per-country nuclear new-build caps (workbook)")
with DatabaseMapping(url) as db:
    for pv in db.get_parameter_value_items(entity_class_name="investment_group", parameter_definition_name="investment_count_total_max_cumulative"):
        if pv["entity_byname"][0].startswith("nuclear-3_"):
            print("readback", pv["entity_byname"][0], pv["alternative_name"], pv["parsed_value"].values)
    for c in groups:
        n = sum(1 for e in db.get_entity_items(entity_class_name="unit__investment_group") if e["element_name_list"][1] == "nuclear-3_" + c)
        print("links", c, n)
print("WROTE", a.dst)
