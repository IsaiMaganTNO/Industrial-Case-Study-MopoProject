import sys, yaml, pandas as pd
sys.path.insert(0, r"data-pipelines/europe/_ines-builder")
import ines_target as it
cfg = yaml.safe_load(open(r"data-pipelines/europe/userconfig.yaml", encoding="utf-8"))
print("countries", cfg["countries"])
p = r"data-pipelines/europe/_ines-builder/region_transformation.xlsx"
rd = {s: pd.read_excel(p, s) for s in pd.ExcelFile(p).sheet_names}
poly = it.define_polygons(cfg, rd, "IC1", "OFF3")
on = poly["onshore_polygons"]; off = poly["offshore_polygons"]
print("ONSHORE", len(on), sorted(on))
print("OFFSHORE", len(off))
for k in sorted(off): print(" ", k, off[k])
