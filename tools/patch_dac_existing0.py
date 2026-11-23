"""Zero the implicit default existing unit of all DAC_* units (SpineOpt default existing_units=1.0).
Usage: patch_dac_existing0.py SRC DST
Copies SRC to DST, then adds existing_units=0.0 (alternative Base) for every DAC_* unit. Asserts there were none before.
"""
import sys, shutil, os
from spinedb_api import DatabaseMapping
src, dst = sys.argv[1:3]
assert not os.path.exists(dst), "DST exists"
shutil.copyfile(src, dst)
with DatabaseMapping("sqlite:///" + os.path.abspath(dst)) as db:
    units = sorted(e["name"] for e in db.get_entity_items(entity_class_name="unit") if e["name"].startswith("DAC_"))
    pre = [x for x in db.get_parameter_value_items(entity_class_name="unit", parameter_definition_name="existing_units") if x["entity_name"].startswith("DAC_")]
    assert not pre, f"DAC already has existing_units: {len(pre)}"
    for u in units:
        db.add_parameter_value_item(entity_class_name="unit", entity_byname=(u,), parameter_definition_name="existing_units", alternative_name="Base", parsed_value=0.0)
    db.commit_session("DAC existing_units=0 (remove free default unit)")
with DatabaseMapping("sqlite:///" + os.path.abspath(dst)) as db:
    post = {x["entity_name"]: x["parsed_value"] for x in db.get_parameter_value_items(entity_class_name="unit", parameter_definition_name="existing_units")}
    assert set(post) == set(units) and set(post.values()) == {0.0}, post
    print(f"DAC units: {len(units)}; existing_units=0 set on all; total existing_units values in DB: {len(post)}")
