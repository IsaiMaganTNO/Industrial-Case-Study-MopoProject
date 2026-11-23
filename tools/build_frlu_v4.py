r"""Build FR+LU v4 input: v3 input with every NL/BE '-existing' unit (and its relationships/params)
replaced by the version in the MR baseline input. Nothing else changes.
usage: python tools/build_frlu_v4.py"""
import re, glob, shutil, os, spinedb_api as s
MR = glob.glob(r"final_runs_pessimistic_ccs\3_*\input\*.sqlite")[0]
V3 = r"share_frlu_xpress\input.sqlite"
OUT = r"runs\3day_mr_frlu_v4\input\Final_SpineOpt_Model.tiny.3day.mr_frlu_ccslow_ccu_cap16_dac0.v4.sqlite"
assert not os.path.exists(OUT), "OUT exists"
PAT = re.compile(r"-existing_(BEC|NLC)\d")
hit = lambda names: any(PAT.search(n) for n in ([names] if isinstance(names, str) else names))
shutil.copyfile(V3, OUT)
src = s.DatabaseMapping("sqlite:///" + MR); a = s.export_data(src); src.close()
db = s.DatabaseMapping("sqlite:///" + os.path.abspath(OUT))
# 1. remove all NL/BE existing units in v3 (cascade removes relationships, params, group links)
ids = [e["id"] for e in db.get_items("entity") if e["entity_class_name"] == "unit" and PAT.search(e["name"])]
print("removing v3 units:", len(ids))
db.remove_items("entity", *ids); db.commit_session("v4: drop NL/BE existing units")
# 2. import MR versions (entities whose name or element names match, plus their params)
ents = [e for e in a["entities"] if hit(e[1])]
ent_keys = {(e[0], e[1] if isinstance(e[1], str) else tuple(e[1])) for e in ents}
pvs = [p for p in a["parameter_values"] if (p[0], p[1] if isinstance(p[1], str) else tuple(p[1])) in ent_keys]
print("importing entities:", len(ents), "values:", len(pvs))
n, err = s.import_data(db, entities=ents, parameter_values=pvs)
assert not err, err[:5]
db.commit_session("v4: import NL/BE existing units from MR baseline"); db.close()
print("imported", n, "->", OUT)
